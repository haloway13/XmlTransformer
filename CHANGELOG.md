# Changelog

## [Unreleased]
- **Fix**: `get_message()` hardcoded `lang = "en"` unconditionally, so `locale/es.sublime-messages` was never actually loaded on any platform despite the 1.2.0 "Localization" entry below — Spanish support was dead code. Sublime Text has no API to query the UI language (confirmed: `sublime.locale()` does not exist, even on ST4 build 4200), so added an explicit `"language"` setting (`"auto"` by default, falls back to the OS locale via Python's `locale` module; an explicit code like `"es"` overrides it). An unsupported/missing language code falls back to English cleanly.
- **Fix**: `enter_param_file` and `enter_param_value` message keys were referenced by `XmlTransformer_build.py` (manual parameter entry flow) but never existed in either `locale/en.sublime-messages` or `locale/es.sublime-messages`, causing an uncaught `KeyError` crash when a user chose "Enter parameters manually" (TC-05). Added both keys to both locale files.
- **Fix**: `on_param_value_entered()` was called as the manual-entry input panel's callback but was never defined anywhere in `XmlTransformerBuildCommand`, so entering the first parameter's value crashed with `AttributeError` instead of advancing to the next prompt. Manual parameter entry (TC-05) never worked on any platform. Implemented the missing handler.
- **Fix**: `pretty_print_xml()` set every leaf `<param>` element's tail to its own indentation level but never dedented the *last* child's tail back to the parent's level, so saved parameter files (e.g. `custom_params.xml`) had the closing `</params>` tag misindented under the last `<param>` instead of aligned with the opening tag.
- **Fix**: Escaping out of the manual-parameter-value or save-filename input panels gave no feedback at all (the `on_cancel` callback was `None`), unlike every quick-panel cancellation elsewhere in the plugin. Added a status bar message on cancel for both input panels.
- **Improvement**: The active XML file was only validated deep inside `run_transformation()`, after the user had already picked an XSL stylesheet and a parameter option. Pressing Ctrl+B on a malformed XML file would walk you through both of those prompts before finally showing the "invalid XML" error. Now validated immediately on Ctrl+B.
- **Fix**: The "Java missing" and "JARs missing" dialogs shown by `run()` called `get_message()` with no arguments, so the platform-specific install command / setup script path computed in `plugin_loaded()` was silently dropped — TC-03 requires the JARs dialog to show the setup script path, which it never did. Extracted `get_java_install_hint()` / `get_setup_script_name()` helpers, wired real arguments into both dialogs, and updated the locale strings to actually use them.

## [1.2.0] - 2026-09-25
- **Setup Instructions**: Updated `messages/install.txt` to include complete dependency requirements and setup instructions for Java, Saxon-HE, and setup scripts, replacing the placeholder text.
- **Localization**: Added multi-language message support with English (`en`) and Spanish (`es`) translations in `locale/`.
- **Compatibility**: Maintained Sublime Text 3 (Python 3.3) compatibility by ensuring `.format()` string formatting is used throughout build and execution scripts.

## [1.1.0] - 2025-10-21
- Added localization foundation and message translation files.

## [1.0.0] - 2025-10-06
- Initial release of XmlTransformer.
- Features:
  - XSLT transformations using Saxon-HE 12.9 and xmlresolver 6.0.6.
  - Quick panel for selecting XSL and parameter files.
  - Support for manual parameter entry and XML parameter files.
  - Platform-specific setup scripts for Linux, macOS, Windows.
  - Error handling with output panel and debug logging.
- Compatible with Sublime Text 3 and 4.
