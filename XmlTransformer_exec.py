import sublime
import sublime_plugin
import os
import time
import re

settings = sublime.load_settings("XmlTransformer.sublime-settings")

def is_debug():
    return settings.get("debug", False)

class XmlTransformerExecCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        if is_debug():
            print("DEBUG: XmlTransformerExecCommand run() called")
        cmd = kwargs.get("cmd")
        output_file = kwargs.get("output_file")
        xsl_path = kwargs.get("xsl_path")
        if not xsl_path and cmd:
            for arg in cmd:
                if arg.startswith("-xsl:"):
                    xsl_path = arg[5:]
                    break
        if is_debug():
            print("DEBUG: Output file:", output_file)
        self.output_file = output_file
        self.xsl_path = xsl_path

        # Clean up any previous exec output panel so stale [Finished ...] lines do not persist
        self.window.destroy_output_panel("exec")
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
        finished_indices = [i for i, l in enumerate(lines) if l.startswith("[Finished")]
        if not finished_indices:
            if attempts <= 0:
                if is_debug():
                    print("DEBUG: Timed out waiting for transformation to finish")
                sublime.error_message("XmlTransformer transformation did not finish, check the build output panel for details.")
                return
            sublime.set_timeout(lambda: self.check_output(output_file, attempts - 1), 500)
            return

        finished_index = finished_indices[-1]
        finished_line = lines[finished_index]

        exit_match = re.search(r"exit code (\d+)", finished_line)
        exit_code = int(exit_match.group(1)) if exit_match else 0
        content_lines = lines[:finished_index]
        if content_lines and content_lines[0].startswith("Running "):
            content_lines = content_lines[1:]
        error_text = '\n'.join(content_lines).strip()
        if is_debug():
            print("DEBUG: Finished line:", repr(finished_line))
            print("DEBUG: Error text:", repr(error_text))

        has_error = (exit_code != 0) or bool(error_text and (
            "Error" in error_text or 
            "Exception" in error_text or 
            "Fatal" in error_text or
            "XPST" in error_text
        ))
        if is_debug():
            print("DEBUG: Transformation finished with exit code", exit_code, "has_error:", has_error)

        if has_error:
            if exit_code == 0:
                exit_code = 1
            if is_debug():
                print("DEBUG: Transformation error:", error_text)
            error_panel = self.window.create_output_panel("xml_transformer_errors")
            error_panel.set_syntax_file("Packages/XML/XML.sublime-syntax")
            error_panel.run_command("append", {"characters": "XmlTransformer Error:\n" + (error_text or finished_line)})
            self.window.run_command("show_panel", {"panel": "output.xml_transformer_errors"})
            match = re.search(r"on line (\d+) column (\d+)(?: of ([^:\r\n]+))?", error_text)
            if is_debug():
                print("DEBUG: Error location match:", match.groups() if match else None)
            if match and self.xsl_path:
                line, col, error_file = match.groups()
                error_file = error_file.strip() if error_file else None
                if error_file and os.path.basename(error_file).lower() != os.path.basename(self.xsl_path).lower():
                    candidate = os.path.join(os.path.dirname(self.xsl_path), error_file)
                    if os.path.exists(candidate):
                        target_file = candidate
                    elif os.path.exists(error_file):
                        target_file = error_file
                    else:
                        target_file = self.xsl_path
                else:
                    target_file = self.xsl_path

                target_path = target_file.replace("\\", "/")
                target = "{0}:{1}:{2}".format(target_path, line, col)
                if is_debug():
                    print("DEBUG: Opening error location:", target)
                opened_view = self.window.open_file(target, sublime.ENCODED_POSITION)
                if opened_view:
                    self.window.focus_view(opened_view)
                    sublime.set_timeout(lambda: self.window.focus_view(opened_view), 50)
            return
        if os.path.exists(output_file):
            if is_debug():
                print("DEBUG: Opening output file:", output_file)
            self.window.open_file(output_file)
            return
        if is_debug():
            print("DEBUG: Output file not found:", output_file)
        sublime.error_message("XmlTransformer transformation failed, check the xml_transformer_errors panel for details.")