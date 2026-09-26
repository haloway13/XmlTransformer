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
        # Poll every 500ms for up to 5 minutes; JVM startup alone can exceed a second
        sublime.set_timeout(lambda: self.check_output(output_file, attempts=600), 500)

    def check_output(self, output_file, attempts):
        # Wait for the exec panel's "[Finished ...]" line before deciding anything: an
        # output file left over from a previous run already exists while Java is still
        # running, so checking for it early opens stale output and skips error handling.
        # On a non-zero exit Sublime appends [cmd:]/[dir:]/[path:] lines after it.
        output_view = self.window.find_output_panel("exec")
        lines = []
        if output_view:
            lines = output_view.substr(sublime.Region(0, output_view.size())).splitlines()
        finished_index = next((i for i, l in enumerate(lines) if l.startswith("[Finished")), None)
        if finished_index is None:
            if attempts <= 0:
                print("DEBUG: Timed out waiting for transformation to finish")
                sublime.error_message("XmlTransformer transformation did not finish, check the build output panel for details.")
                return
            sublime.set_timeout(lambda: self.check_output(output_file, attempts - 1), 500)
            return

        exit_match = re.search(r"exit code (\d+)", lines[finished_index])
        exit_code = int(exit_match.group(1)) if exit_match else 0
        content_lines = lines[:finished_index]
        if content_lines and content_lines[0].startswith("Running "):
            content_lines = content_lines[1:]
        error_text = '\n'.join(content_lines).strip()
        print("DEBUG: Transformation finished with exit code", exit_code)

        if exit_code != 0:
            print("DEBUG: Transformation error:", error_text)
            error_panel = self.window.create_output_panel("xml_transformer_errors")
            error_panel.set_syntax_file("Packages/XML/XML.sublime-syntax")
            error_panel.run_command("append", {"characters": "XmlTransformer Error:\n" + (error_text or lines[finished_index])})
            self.window.run_command("show_panel", {"panel": "output.xml_transformer_errors"})
            # Saxon 12: "... on line 6 column 45 of broken.xsl:"; older: "Error on line 6 column 45"
            match = re.search(r"on line (\d+) column (\d+)(?: of ([^:\n]+))?", error_text)
            if match and self.xsl_path:
                line, col, error_file = match.groups()
                if error_file is None or os.path.basename(error_file) == os.path.basename(self.xsl_path):
                    self.window.open_file("{0}:{1}:{2}".format(self.xsl_path, line, col), sublime.ENCODED_POSITION)
            return
        if os.path.exists(output_file):
            print("DEBUG: Opening output file:", output_file)
            self.window.open_file(output_file)
            return
        print("DEBUG: Output file not found:", output_file)
        sublime.error_message("XmlTransformer transformation failed, check the xml_transformer_errors panel for details.")