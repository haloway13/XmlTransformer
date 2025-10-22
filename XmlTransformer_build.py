import sublime
import sublime_plugin
import os
import subprocess
import platform
import xml.etree.ElementTree as ET
import time
import json

settings = sublime.load_settings("XmlTransformer.sublime-settings")

def is_debug():
    return settings.get("debug", False)

def get_message(key, *args):
    # Fallback to English for Sublime Text 3 compatibility (no sublime.locale())
    lang = "en"  # Default to English; extend for ST4 with sublime.locale().split('-')[0]
    try:
        messages_path = "Packages/XmlTransformer/locale/{0}.sublime-messages".format(lang)
        messages = sublime.load_resource(messages_path)
        return json.loads(messages)[key].format(*args)
    except:
        # Fallback to English if lang file missing
        messages = sublime.load_resource("Packages/XmlTransformer/locale/en.sublime-messages")
        return json.loads(messages)[key].format(*args)

# Global flags for environment readiness
java_available = True
jars_available = True

def plugin_loaded():
    global java_available
    global jars_available
    if is_debug():
        print("DEBUG: XmlTransformer_build.py loaded at:", time.time())
    if is_debug():
        print("DEBUG: XmlTransformer settings:", {
            "last_param_filename": settings.get("last_param_filename", "params.xml"),
            "suppress_warnings": settings.get("suppress_warnings", True)
        })
    system = sublime.platform()
    is_windows = system == "windows"
    is_macos = system == "osx"
    if is_windows:
        jar_path = os.path.join(os.environ["ProgramFiles"], "Saxon")
        java_bin = "java"  # Windows typically has java in PATH
    elif is_macos:
        jar_path = os.path.expanduser("~/Library/Saxon")
        possible_java_paths = [
            "/opt/homebrew/opt/openjdk@11/bin/java",  # Apple Silicon
            "/usr/local/opt/openjdk@11/bin/java"      # Intel
        ]
        java_bin = None
        for path in possible_java_paths:
            if os.path.exists(path):
                java_bin = path
                break
        if not java_bin:
            java_bin = "java"  # Fallback to PATH
    else:  # Linux
        jar_path = "/usr/local/lib/saxon"
        java_bin = "java"
    try:
        creation_flags = 0
        if sublime.platform() == "windows":
            creation_flags = 0x08000000  # subprocess.CREATE_NO_WINDOW
        process = subprocess.Popen([java_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flags)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, [java_bin, "-version"])
        global java_available
        java_available = True
        if is_debug():
            print("DEBUG: Java found: %s" % stdout.decode('utf-8').split('\n')[0])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        if is_debug():
            print("DEBUG: Java not found at:", time.time(), "Error:", str(e))
        java_install_cmd = "brew install openjdk@11" if is_macos else "sudo apt install openjdk-11-jre" if system == "linux" else "download from adoptium.net"
        platform_name = "macOS" if is_macos else "Linux" if system == "linux" else "Windows"
        msg = get_message("java_missing", java_install_cmd, platform_name)
        if is_debug():
            print("DEBUG: " + msg)
        java_available = False
    required_jars = ["Saxon-HE-12.9.jar", "xmlresolver-6.0.6.jar", "xmlresolver-6.0.6-data.jar"]
    if not all(os.path.exists(os.path.join(jar_path, jar)) for jar in required_jars):
        if is_debug():
            print("DEBUG: Missing JARs in", jar_path, "at:", time.time())
        setup_cmd = "setup_XmlTransformer_macos.sh" if is_macos else "setup_XmlTransformer_ubuntu.sh" if system == "linux" else "setup_XmlTransformer_windows.bat"
        msg = get_message("jars_missing", jar_path, setup_cmd)
        if is_debug():
            print("DEBUG: " + msg)
        global jars_available
        jars_available = False
    else:
        jars_available = True

class XmlTransformerBuildCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        if is_debug():
            print("DEBUG: XmlTransformerBuildCommand run() called at:", time.time())
            print("DEBUG: Current window ID:", self.window.id())
        if not java_available:
            sublime.error_message(get_message("java_missing"))
            return
        if not jars_available:
            sublime.error_message(get_message("jars_missing"))
            return
        if is_debug():
            print("DEBUG: Before active_view at:", time.time())
        view = self.window.active_view()
        if is_debug():
            print("DEBUG: After active_view at:", time.time())
        if not view or view.file_name() is None:
            if is_debug():
                print("DEBUG: No active view or file not saved at:", time.time())
            sublime.error_message(get_message("no_xml_file"))
            return
        self.xml_path = view.file_name()
        self.working_dir = os.path.dirname(self.xml_path) if os.path.sep in self.xml_path else "."
        self.default_xsl = os.path.splitext(self.xml_path)[0] + '.xsl'
        if is_debug():
            print("DEBUG: XML file path set at:", time.time())
        self.show_combined_panel(self.working_dir)

    def show_combined_panel(self, current_dir):
        sublime.status_message(get_message("navigate_xsl"))
        if is_debug():
            print("DEBUG: Starting show_combined_panel at:", time.time())
        if not os.path.isdir(current_dir):
            if is_debug():
                print("DEBUG: Invalid directory check at:", time.time())
            sublime.error_message(get_message("invalid_dir", current_dir))
            return
        self.current_dir = os.path.realpath(current_dir)
        if is_debug():
            print("DEBUG: Directory resolved at:", time.time())
        items = ["[Parent Directory]" if self.current_dir != os.path.abspath(os.path.sep) else "[Root Directory]"]
        dirs = sorted([d + os.path.sep for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith('.') and len(d) < 100])
        xsl_files = sorted([f for f in os.listdir(current_dir) if f.endswith('.xsl') and len(f) < 100])
        if is_debug():
            print("DEBUG: Directory scan completed at:", time.time())
        items.extend(dirs)
        items.extend(xsl_files)
        if not dirs and not xsl_files:
            if is_debug():
                print("DEBUG: No files found at:", time.time())
            sublime.error_message(get_message("no_files_in_dir", self.current_dir))
            return
        self.items = items
        self.xsl_files = xsl_files
        self.window.show_quick_panel(
            items,
            self.on_item_selected
        )

    def on_item_selected(self, index):
        if index == -1:
            if is_debug():
                print("DEBUG: Selection cancelled, exiting")
            sublime.status_message(get_message("param_choice_cancelled"))
            return
        selected_item = self.items[index]
        self.system = sublime.platform()
        self.is_windows = self.system == "windows"
        self.is_macos = self.system == "osx"
        if self.is_macos:
            possible_java_paths = [
                "/opt/homebrew/opt/openjdk@11/bin/java",  # Apple Silicon
                "/usr/local/opt/openjdk@11/bin/java"      # Intel
            ]
            self.java_bin = None
            for path in possible_java_paths:
                if os.path.exists(path):
                    self.java_bin = path
                    break
            if not self.java_bin:
                self.java_bin = "java"  # Fallback to PATH
        else:
            self.java_bin = "java"
        self.cp_separator = ";" if self.is_windows else ":"
        self.jar_path = os.path.join(os.environ["ProgramFiles"], "Saxon") if self.is_windows else os.path.expanduser("~/Library/Saxon") if self.is_macos else "/usr/local/lib/saxon"
        if selected_item == "[Parent Directory]" and self.current_dir != os.path.abspath(os.path.sep):
            parent_dir = os.path.dirname(self.current_dir)
            self.show_combined_panel(parent_dir)
        elif selected_item == "[Root Directory]":
            self.show_combined_panel(self.current_dir)
        elif selected_item.endswith(os.path.sep):
            sub_dir = os.path.join(self.current_dir, selected_item[:-1])
            self.show_combined_panel(sub_dir)
        else:
            self.xsl_path = os.path.join(self.current_dir, selected_item)
            if is_debug():
                print("DEBUG: XSL path selected:", self.xsl_path)
            if not os.path.exists(self.xsl_path):
                if is_debug():
                    print("DEBUG: Invalid XSL path:", self.xsl_path)
                sublime.error_message(get_message("invalid_xsl_path", self.xsl_path))
                return
            try:
                tree = ET.parse(self.xsl_path)
                root = tree.getroot()
                ns = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
                self.params = [elem.attrib['name'] for elem in root.findall('xsl:param', ns)]
                if is_debug():
                    print("DEBUG: Detected parameters:", self.params)
            except Exception as e:
                if is_debug():
                    print("DEBUG: Failed to parse XSL for params:", str(e))
                self.params = []
            if self.params:
                self.window.show_quick_panel(
                    ["Run without parameters", "Enter parameters manually", "Select variables XML file"],
                    self.on_param_choice
                )
            else:
                self.run_transformation(None)

    def on_param_choice(self, index):
        if index == -1:
            if is_debug():
                print("DEBUG: Parameter choice cancelled, exiting")
            sublime.status_message(get_message("param_choice_cancelled"))
            return
        if index == 0:
            self.run_transformation(None)
        elif index == 1:
            self.current_param_index = 0
            self.param_values = {}
            self.prompt_for_param()
        else:
            self.show_param_file_panel(self.working_dir)

    def prompt_for_param(self):
        if self.current_param_index >= len(self.params):
            last_filename = settings.get("last_param_filename", "params.xml")
            self.window.show_input_panel(
                get_message("enter_param_file", self.working_dir),
                last_filename,
                self.on_param_file_name_entered,
                None,
                None
            )
            return
        param_name = self.params[self.current_param_index]
        self.window.show_input_panel(
            get_message("enter_param_value", param_name),
            "",
            lambda value: self.on_param_value_entered(param_name, value),
            None,
            None
        )

    def on_param_file_name_entered(self, file_name):
        if is_debug():
            print("DEBUG: Entering on_param_file_name_entered")
        if not file_name.endswith('.xml'):
            file_name += '.xml'
        param_file = os.path.join(self.working_dir, file_name)
        try:
            root = ET.Element('params')
            for name, value in self.param_values.items():
                param = ET.SubElement(root, 'param', name=name, value=value)
            self.pretty_print_xml(root)
            tree = ET.ElementTree(root)
            tree.write(param_file, encoding='utf-8', xml_declaration=True)
            if is_debug():
                print("DEBUG: Saved parameters to:", param_file)
            sublime.status_message(get_message("params_saved", file_name))
            settings.set("last_param_filename", file_name)
            sublime.save_settings("XmlTransformer.sublime-settings")
            param_values = self.parse_xml_param_file(param_file)
            if param_values is None:
                return
            if is_debug():
                print("DEBUG: Exiting on_param_file_name_entered")
            self.run_transformation(param_file)
        except Exception as e:
            if is_debug():
                print("DEBUG: Failed to save param file:", str(e))
            sublime.error_message(get_message("param_parse_failed", file_name, str(e)))

    def show_param_file_panel(self, current_dir):
        if not os.path.isdir(current_dir):
            if is_debug():
                print("DEBUG: Invalid directory:", current_dir)
            sublime.error_message(get_message("invalid_param_dir", current_dir))
            return
        sublime.status_message(get_message("select_param_file"))
        self.current_dir = os.path.realpath(current_dir)
        if is_debug():
            print("DEBUG: Showing param file panel for:", self.current_dir)
        items = ["[Parent Directory]" if self.current_dir != os.path.abspath(os.path.sep) else "[Root Directory]"]
        dirs = sorted([d + os.path.sep for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith('.')])
        param_files = sorted([f for f in os.listdir(current_dir) if f.endswith('.xml')])
        items.extend(dirs)
        items.extend(param_files)
        if not dirs and not param_files:
            if is_debug():
                print("DEBUG: No directories or XML files found in:", self.current_dir)
            sublime.error_message(get_message("no_param_files", self.current_dir))
            return
        self.items = items
        self.param_files = param_files
        self.window.show_quick_panel(
            items,
            self.on_param_file_selected
        )

    def on_param_file_selected(self, index):
        if is_debug():
            print("DEBUG: Entering on_param_file_selected")
        if index == -1:
            if is_debug():
                print("DEBUG: Param file selection cancelled, exiting")
            sublime.status_message(get_message("param_file_cancelled"))
            return
        selected_item = self.items[index]
        if selected_item == "[Parent Directory]" and self.current_dir != os.path.abspath(os.path.sep):
            parent_dir = os.path.dirname(self.current_dir)
            self.show_param_file_panel(parent_dir)
        elif selected_item == "[Root Directory]":
            self.show_param_file_panel(self.current_dir)
        elif selected_item.endswith(os.path.sep):
            sub_dir = os.path.join(self.current_dir, selected_item[:-1])
            self.show_param_file_panel(sub_dir)
        else:
            param_file = os.path.join(self.current_dir, selected_item)
            if is_debug():
                print("DEBUG: Param file selected:", param_file)
            if not os.path.exists(param_file):
                if is_debug():
                    print("DEBUG: Invalid param file:", param_file)
                sublime.error_message(get_message("invalid_param_file", param_file))
                return
            param_values = self.parse_xml_param_file(param_file)
            if param_values is None:
                return
            missing_params = [p for p in self.params if p not in param_values]
            if missing_params:
                warning = get_message("missing_params_warning", selected_item, ", ".join(missing_params))
                if is_debug():
                    print("DEBUG:", warning)
                sublime.status_message(warning)
            settings.set("last_param_filename", selected_item)
            sublime.save_settings("XmlTransformer.sublime-settings")
            if is_debug():
                print("DEBUG: Exiting on_param_file_selected")
            self.run_transformation(param_file)

    def parse_xml_param_file(self, param_file):
        try:
            param_values = {}
            tree = ET.parse(param_file)
            root = tree.getroot()
            for param in root.findall('.//param'):
                name = param.get('name')
                value = param.get('value', '')
                if name and value:
                    param_values[name] = value
            if is_debug():
                print("DEBUG: Parsed parameters:", param_values)
            return param_values
        except Exception as e:
            if is_debug():
                print("DEBUG: Failed to parse param file:", str(e))
            sublime.error_message(get_message("param_parse_failed", param_file, str(e)))
            return None

    def validate_xml_file(self, file_path):
        try:
            ET.parse(file_path)
            if is_debug():
                print("DEBUG: Validated %s as well-formed XML/XSL" % file_path)
            return True
        except ET.ParseError as e:
            if is_debug():
                print("DEBUG: Invalid XML/XSL in %s: %s" % (file_path, str(e)))
            sublime.error_message(get_message("invalid_xml_xsl", file_path, str(e)))
            return False
        except Exception as e:
            if is_debug():
                print("DEBUG: Unexpected error validating %s: %s" % (file_path, str(e)))
            sublime.error_message(get_message("validation_error", file_path, str(e)))
            return False

    def get_xsl_output_method(self, xsl_path):
        try:
            tree = ET.parse(xsl_path)
            root = tree.getroot()
            ns = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
            output_elem = root.find('xsl:output', ns)
            if output_elem is not None and 'method' in output_elem.attrib:
                method = output_elem.attrib['method'].lower()
                if is_debug():
                    print("DEBUG: Parsed <xsl:output method> from XSLT:", method)
                if method in ['xml', 'html', 'text']:
                    return method
                else:
                    if is_debug():
                        print("DEBUG: Invalid <xsl:output method> found, defaulting to xml")
            else:
                if is_debug():
                    print("DEBUG: No <xsl:output> element found, checking content")
            if root.find('.//html', ns) is not None or root.find('.//xsl:element[@name="html"]', ns) is not None:
                if is_debug():
                    print("DEBUG: Detected HTML content in XSLT, using html")
                return 'html'
            text_templates = root.findall('.//xsl:value-of', ns) + root.findall('.//xsl:text', ns)
            if text_templates and not root.findall('.//*', ns):
                if is_debug():
                    print("DEBUG: Detected text-like content in XSLT, using text")
                return 'text'
            if is_debug():
                print("DEBUG: Defaulting to xml")
            return 'xml'
        except Exception as e:
            if is_debug():
                print("DEBUG: Failed to parse XSLT for output method:", str(e))
            return 'xml'

    def run_transformation(self, param_file):
        if not self.validate_xml_file(self.xml_path) or not self.validate_xml_file(self.xsl_path):
            return
        suppress_warnings = settings.get("suppress_warnings", True)
        if is_debug():
            print("DEBUG: suppress_warnings setting:", suppress_warnings)
        output_method = self.get_xsl_output_method(self.xsl_path)
        extension = '.xml' if output_method == 'xml' else '.html' if output_method == 'html' else '.txt'
        output_file = os.path.splitext(self.xml_path)[0] + "-output" + extension
        cmd = [
            self.java_bin, "-cp", os.path.normpath(os.path.join(self.jar_path, "Saxon-HE-12.9.jar")) + self.cp_separator +
                           os.path.normpath(os.path.join(self.jar_path, "xmlresolver-6.0.6.jar")) + self.cp_separator +
                           os.path.normpath(os.path.join(self.jar_path, "xmlresolver-6.0.6-data.jar")),
            "net.sf.saxon.Transform",
            "-s:" + os.path.normpath(self.xml_path),
            "-xsl:" + os.path.normpath(self.xsl_path),
            "-o:" + os.path.normpath(output_file)
        ]
        if suppress_warnings:
            cmd.append("-warnings:silent")
        if param_file:
            param_values = self.parse_xml_param_file(param_file)
            if param_values is None:
                return
            for name, value in param_values.items():
                cmd.append("{0}={1}".format(name, value.replace(" ", "\\ ")))
        if is_debug():
            print("DEBUG: Command:", cmd)
        self.window.run_command("xml_transformer_exec", {
            "cmd": cmd,
            "file_regex": "^(.+?):([0-9]+):?([0-9]*):?(.*)$",
            "working_dir": self.working_dir,
            "output_file": output_file
        })

    def pretty_print_xml(self, elem, level=0):
        indent = "    "
        i = "\n" + level * indent
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + indent
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.pretty_print_xml(child, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i