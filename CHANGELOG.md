# Changelog

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
