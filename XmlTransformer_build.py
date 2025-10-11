import sublime
import sublime_plugin
import os
import subprocess
import platform
import xml.etree.ElementTree as ET
import time

# Global flags for environment readiness
java_available = True
jars_available = True

def plugin_loaded():
    global java_available
    global jars_available
    print("DEBUG: XmlTransformer_build.py loaded at:", time.time())
    # Load and print settings
    settings = sublime.load_settings("XmlTransformer.sublime-settings")
    print("DEBUG: XmlTransformer settings:", {
        "last_param_filename": settings.get("last_param_filename", "params.xml"),
        "suppress_warnings": settings.get("suppress_warnings", True)
    })
    system = platform.system()
    is_windows = system == "Windows"
    is_macos = system == "Darwin"
    if is_windows:
        jar_path = os.path.join(os.environ["ProgramFiles"], "Saxon")
        java_bin = "java"  # Windows typically has java in PATH
    elif is_macos:
        jar_path = os.path.expanduser("~/Library/Saxon")
        # Try Apple Silicon path first, then Intel
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
    # Check Java availability
    try:
        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = 0x08000000  # subprocess.CREATE_NO_WINDOW
        process = subprocess.Popen([java_bin, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creation_flags)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, [java_bin, "-version"])
        global java_available
        java_available = True
        print("DEBUG: Java found: %s" % stdout.decode('utf-8').split('\n')[0])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("DEBUG: Java not found at:", time.time(), "Error:", str(e))
        java_install_cmd = "brew install openjdk@11" if is_macos else "sudo apt install openjdk-11-jre" if system == "Linux" else "download from adoptium.net"
        platform_name = "macOS" if is_macos else "Linux" if system == "Linux" else "Windows"
        msg = "Java not found. Install Java 8+ (e.g., %s on %s)" % (java_install_cmd, platform_name)
        print("DEBUG: " + msg)
        java_available = False
    # Check JAR availability
    required_jars = ["Saxon-HE-12.9.jar", "xmlresolver-6.0.6.jar", "xmlresolver-6.0.6-data.jar"]
    if not all(os.path.exists(os.path.join(jar_path, jar)) for jar in required_jars):
        print("DEBUG: Missing JARs in", jar_path, "at:", time.time())
        setup_cmd = "setup_XmlTransformer_macos.sh" if is_macos else "setup_XmlTransformer_ubuntu.sh" if system == "Linux" else "setup_XmlTransformer_windows.bat"
        msg = "Missing JARs in %s. Run %s or install manually from https://www.saxonica.com and https://github.com/xmlresolver/xmlresolver." % (jar_path, setup_cmd)
        print("DEBUG: " + msg)
        global jars_available
        jars_available = False
    else:
        jars_available = True

class XmlTransformerBuildCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        """
        Executes the XML build command for the active window.
        Initializes platform-specific settings and triggers the file selection panel.
        Args:
            **kwargs: Optional keyword arguments (currently unused).
        """
        print("DEBUG: XmlTransformerBuildCommand run() called at:", time.time())
        print("DEBUG: Current window ID:", self.window.id())

        # Check environment readiness set during plugin_loaded
        if not java_available:
            sublime.error_message("Java is not available. Please install it and restart Sublime Text.")
            return
        if not jars_available:
            sublime.error_message("JARs are not available. Please install them and restart Sublime Text.")
            return

        # Get the active view and validate it contains a saved XML file
        print("DEBUG: Before active_view at:", time.time())
        view = self.window.active_view()
        print("DEBUG: After active_view at:", time.time())
        if not view or view.file_name() is None:
            print("DEBUG: No active view or file not saved at:", time.time())
            sublime.error_message("No active XML file open or file not saved. Please save the file.")
            return

        # Set file paths for the transformation
        self.xml_path = view.file_name()
        self.working_dir = os.path.dirname(self.xml_path) if os.path.sep in self.xml_path else "."
        self.default_xsl = os.path.splitext(self.xml_path)[0] + '.xsl'
        print("DEBUG: XML file path set at:", time.time())
        self.show_combined_panel(self.working_dir)

    def show_combined_panel(self, current_dir):
        """
        Displays a quick panel with directories and XSL files for selection.
        Optimizes directory scanning and limits items to improve performance.
        Args:
            current_dir (str): The directory to scan for XSL files and subdirectories.
        """
        sublime.status_message("Navigate to and select an .xsl file for the XSLT transformation. Use directories to browse, Escape to cancel.")

        print("DEBUG: Starting show_combined_panel at:", time.time())

        # Validate the directory exists
        if not os.path.isdir(current_dir):
            print("DEBUG: Invalid directory check at:", time.time())
            sublime.error_message("Invalid directory: " + current_dir)
            return

        # Resolve the real path of the directory
        self.current_dir = os.path.realpath(current_dir)
        print("DEBUG: Directory resolved at:", time.time())

        # Build the panel items list, filtering out hidden directories and limiting name length
        items = ["[Parent Directory]" if self.current_dir != os.path.abspath(os.path.sep) else "[Root Directory]"]
        dirs = sorted([d + os.path.sep for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith('.') and len(d) < 100])
        xsl_files = sorted([f for f in os.listdir(current_dir) if f.endswith('.xsl') and len(f) < 100])
        print("DEBUG: Directory scan completed at:", time.time())
        items.extend(dirs)
        items.extend(xsl_files)

        # Handle case where no valid items are found
        if not dirs and not xsl_files:
            print("DEBUG: No files found at:", time.time())
            sublime.error_message("No directories or XSL files found in: " + self.current_dir)
            return

        # Store items and files for later use
        self.items = items
        self.xsl_files = xsl_files
        self.window.show_quick_panel(
            items,
            self.on_item_selected
        )

    def on_item_selected(self, index):
        if index == -1:
            print("DEBUG: Selection cancelled, exiting")
            sublime.status_message("Selection cancelled")
            return
        selected_item = self.items[index]
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_macos = self.system == "Darwin"
        # Set java_bin for macOS to try Apple Silicon and Intel paths
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
            print("DEBUG: XSL path selected:", self.xsl_path)
            if not os.path.exists(self.xsl_path):
                print("DEBUG: Invalid XSL path:", self.xsl_path)
                sublime.error_message("Invalid or missing XSL file path: " + self.xsl_path)
                return
            # Scan XSL for parameters
            try:
                tree = ET.parse(self.xsl_path)
                root = tree.getroot()
                ns = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
                self.params = [elem.attrib['name'] for elem in root.findall('xsl:param', ns)]
                print("DEBUG: Detected parameters:", self.params)
            except Exception as e:
                print("DEBUG: Failed to parse XSL for params:", str(e))
                self.params = []
            if self.params:
                self.window.show_quick_panel(
                    ["Enter parameters manually", "Select variables XML file"],
                    self.on_param_choice
                )
            else:
                self.run_transformation(None)

    def on_param_choice(self, index):
        if index == -1:
            print("DEBUG: Parameter choice cancelled, exiting")
            sublime.status_message("Parameter choice cancelled")
            return
        if index == 0:
            self.current_param_index = 0
            self.param_values = {}
            self.prompt_for_param()
        else:
            self.show_param_file_panel(self.working_dir)

    def prompt_for_param(self):
        if self.current_param_index >= len(self.params):
            # Load last filename from settings
            settings = sublime.load_settings("XmlTransformer.sublime-settings")
            last_filename = settings.get("last_param_filename", "params.xml")
            # Prompt for filename, suggesting last used
            self.window.show_input_panel(
                "Enter name for variables XML file (in %s)" % self.working_dir,
                last_filename,
                self.on_param_file_name_entered,
                None,
                None
            )
            return
        param_name = self.params[self.current_param_index]
        self.window.show_input_panel(
            "Enter value for parameter '%s'" % param_name,
            "",
            lambda value: self.on_param_value_entered(param_name, value),
            None,
            None
        )
        return

    def on_param_file_name_entered(self, file_name):
        print("DEBUG: Entering on_param_file_name_entered")
        if not file_name.endswith('.xml'):
            file_name += '.xml'
        param_file = os.path.join(self.working_dir, file_name)
        try:
            # Save parameters to XML file in generic format with pretty-printing
            root = ET.Element('params')
            for name, value in self.param_values.items():
                param = ET.SubElement(root, 'param', name=name, value=value)
            self.pretty_print_xml(root)  # Apply pretty-printing
            tree = ET.ElementTree(root)
            tree.write(param_file, encoding='utf-8', xml_declaration=True)
            print("DEBUG: Saved parameters to:", param_file)
            sublime.status_message("Parameters saved to %s" % file_name)
            # Save last filename to settings
            settings = sublime.load_settings("XmlTransformer.sublime-settings")
            settings.set("last_param_filename", file_name)
            sublime.save_settings("XmlTransformer.sublime-settings")
            # Parse the saved file to validate parameters
            param_values = self.parse_xml_param_file(param_file)
            if param_values is None:
                return
            print("DEBUG: Exiting on_param_file_name_entered")
            self.run_transformation(param_file)
        except Exception as e:
            print("DEBUG: Failed to save param file:", str(e))
            sublime.error_message("Failed to save %s: %s" % (file_name, str(e)))

    def show_param_file_panel(self, current_dir):
        if not os.path.isdir(current_dir):
            print("DEBUG: Invalid directory:", current_dir)
            sublime.error_message("Invalid directory: " + current_dir)
            return
        
        sublime.status_message("Select an XML parameter file (format: <param name='...' value='...' />) or navigate directories. Escape to cancel.")

        self.current_dir = os.path.realpath(current_dir)
        print("DEBUG: Showing param file panel for:", self.current_dir)
        items = ["[Parent Directory]" if self.current_dir != os.path.abspath(os.path.sep) else "[Root Directory]"]
        dirs = sorted([d + os.path.sep for d in os.listdir(self.current_dir) if os.path.isdir(os.path.join(self.current_dir, d)) and not d.startswith('.')])
        param_files = sorted([f for f in os.listdir(self.current_dir) if f.endswith('.xml')])
        items.extend(dirs)
        items.extend(param_files)
        if not dirs and not param_files:
            print("DEBUG: No directories or XML files found in:", self.current_dir)
            sublime.error_message("No directories or XML files found in: " + self.current_dir)
            return
        self.items = items
        self.param_files = param_files
        self.window.show_quick_panel(
            items,
            self.on_param_file_selected
        )

    def on_param_file_selected(self, index):
        print("DEBUG: Entering on_param_file_selected")
        if index == -1:
            print("DEBUG: Param file selection cancelled, exiting")
            sublime.status_message("Param file selection cancelled")
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
            print("DEBUG: Param file selected:", param_file)
            if not os.path.exists(param_file):
                print("DEBUG: Invalid param file:", param_file)
                sublime.error_message("Invalid or missing param file: " + param_file)
                return
            # Parse parameters from file to check for missing ones
            param_values = self.parse_xml_param_file(param_file)
            if param_values is None:
                return
            # Check for missing parameters and warn
            missing_params = [p for p in self.params if p not in param_values]
            if missing_params:
                warning = "Warning: Missing parameters in %s: %s. Continuing transformation." % (selected_item, ", ".join(missing_params))
                print("DEBUG:", warning)
                sublime.status_message(warning)
            # Save last filename to settings
            settings = sublime.load_settings("XmlTransformer.sublime-settings")
            settings.set("last_param_filename", selected_item)
            sublime.save_settings("XmlTransformer.sublime-settings")
            print("DEBUG: Exiting on_param_file_selected")
            self.run_transformation(param_file)

    def parse_xml_param_file(self, param_file):
        try:
            param_values = {}
            tree = ET.parse(param_file)
            root = tree.getroot()
            # No namespace needed for this simple structure
            for param in root.findall('.//param'):
                name = param.get('name')
                value = param.get('value', '')
                if name and value:
                    param_values[name] = value
            print("DEBUG: Parsed parameters:", param_values)
            return param_values
        except Exception as e:
            print("DEBUG: Failed to parse param file:", str(e))
            sublime.error_message("Failed to parse %s: %s" % (param_file, str(e)))
            return None

    def validate_xml_file(self, file_path):
        """
        Validates that the given XML/XSL file is well-formed using ElementTree.
        Returns True if valid, False otherwise, with an error message.
        """
        try:
            ET.parse(file_path)
            print("DEBUG: Validated %s as well-formed XML/XSL" % file_path)
            return True
        except ET.ParseError as e:
            print("DEBUG: Invalid XML/XSL in %s: %s" % (file_path, str(e)))
            sublime.error_message("Invalid XML/XSL file: %s\nError: %s" % (file_path, str(e)))
            return False
        except Exception as e:
            print("DEBUG: Unexpected error validating %s: %s" % (file_path, str(e)))
            sublime.error_message("Unexpected error validating %s: %s" % (file_path, str(e)))
            return False

    def get_xsl_output_method(self, xsl_path):
        try:
            tree = ET.parse(xsl_path)
            root = tree.getroot()
            ns = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
            output_elem = root.find('xsl:output', ns)
            if output_elem is not None and 'method' in output_elem.attrib:
                method = output_elem.attrib['method'].lower()
                print("DEBUG: Parsed <xsl:output method> from XSLT:", method)
                if method in ['xml', 'html', 'text']:
                    return method
                else:
                    print("DEBUG: Invalid <xsl:output method> found, defaulting to xml")
            else:
                print("DEBUG: No <xsl:output> element found, checking content")
            # Fallback: Inspect XSLT content for HTML or text indicators
            if root.find('.//html', ns) is not None or root.find('.//xsl:element[@name="html"]', ns) is not None:
                print("DEBUG: Detected HTML content in XSLT, using html")
                return 'html'
            # Check for text-like output (e.g., <xsl:value-of> with separators)
            text_templates = root.findall('.//xsl:value-of', ns) + root.findall('.//xsl:text', ns)
            if text_templates and not root.findall('.//*', ns):
                print("DEBUG: Detected text-like content in XSLT, using text")
                return 'text'
            print("DEBUG: Defaulting to xml")
            return 'xml'
        except Exception as e:
            print("DEBUG: Failed to parse XSLT for output method:", str(e))
            return 'xml'  # Fallback to xml on error

    def run_transformation(self, param_file):
        # Validate XML and XSL files before transformation
        if not self.validate_xml_file(self.xml_path) or not self.validate_xml_file(self.xsl_path):
            return

        settings = sublime.load_settings("XmlTransformer.sublime-settings")
        suppress_warnings = settings.get("suppress_warnings", True)
        print("DEBUG: suppress_warnings setting:", suppress_warnings)
        # Determine output file extension based on <xsl:output method>
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
                # Escape spaces in parameter values for Python 3.3 compatibility
                cmd.append("{0}={1}".format(name, value.replace(" ", "\\ ")))
        print("DEBUG: Command:", cmd)
        self.window.run_command("xml_transformer_exec", {
            "cmd": cmd,
            "file_regex": "^(.+?):([0-9]+):?([0-9]*):?(.*)$",
            "working_dir": self.working_dir,
            "output_file": output_file
        })

    def pretty_print_xml(self, elem, level=0):
        indent = "    "  # 4 spaces for indentation
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