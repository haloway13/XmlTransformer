import sublime
import sublime_plugin
import os
import time
import re

print("DEBUG: XmlTransformer_exec.py loaded")

class XmlTransformerExecCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        print("DEBUG: XmlTransformerExecCommand run() called")
        cmd = kwargs.get("cmd")
        output_file = kwargs.get("output_file")
        xsl_path = None
        for arg in cmd:
            if arg.startswith("-xsl:"):
                xsl_path = arg.split(":", 1)[1]
                break
        print("DEBUG: Output file:", output_file)
        self.output_file = output_file
        self.xsl_path = xsl_path
        self.window.run_command("exec", {
            "cmd": cmd,
            "file_regex": kwargs.get("file_regex"),
            "working_dir": kwargs.get("working_dir")
        })
        sublime.set_timeout(lambda: self.check_output(output_file, attempts=20), 500)

    def check_output(self, output_file, attempts):
        output_view = self.window.find_output_panel("exec")
        finished = False
        error_text = ""
        if output_view:
            full_text = output_view.substr(sublime.Region(0, output_view.size()))
            lines = full_text.splitlines()
            content_lines = lines
            if lines and lines[0].startswith("Running "):
                content_lines = lines[1:]
            if content_lines and content_lines[-1].startswith("[Finished "):
                finished = True
                content_lines = content_lines[:-1]
            error_text = '\n'.join(content_lines).strip()
        has_error = bool(error_text) and ("Exception in thread" in error_text or 
                                         "Error" in error_text or 
                                         "Warning" in error_text or 
                                         "Fatal Error" in error_text)
        if has_error:
            print("DEBUG: Transformation error:", error_text)
            error_panel = self.window.create_output_panel("xml_transformer_errors")
            error_panel.set_syntax_file("Packages/XML/XML.sublime-syntax")
            error_panel.run_command("append", {"characters": "XmlTransformer Error:\n" + error_text})
            self.window.run_command("show_panel", {"panel": "output.xml_transformer_errors"})
            if "Error on line" in error_text and self.xsl_path:
                match = re.search(r"Error on line (\d+) column (\d+)", error_text)
                if match:
                    line, col = match.groups()
                    self.window.open_file("{0}:{1}:{2}".format(self.xsl_path, line, col), sublime.ENCODED_POSITION)
                else:
                    self.window.open_file("{0}:1:1".format(self.xsl_path), sublime.ENCODED_POSITION)
            if os.path.exists(output_file):
                print("DEBUG: Opening output file despite error:", output_file)
                self.window.open_file(output_file)
            return
        if os.path.exists(output_file):
            print("DEBUG: Opening output file:", output_file)
            self.window.open_file(output_file)
            return
        if attempts <= 0 or finished:
            print("DEBUG: Output file not found:", output_file)
            sublime.error_message("XmlTransformer transformation failed, check the xml_transformer_errors panel for details.")
            return
        sublime.set_timeout(lambda: self.check_output(output_file, attempts - 1), 500)