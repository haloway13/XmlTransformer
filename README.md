# XmlTransformer Package

A Sublime Text package for performing XSLT transformations on XML files using Saxon-HE 12.9 and xmlresolver 6.0.6. Supports Linux, Windows, and macOS with a file browser-like interface for selecting XSL files and parameter files.

## Features

- Navigate directories (excluding hidden . directories) and select .xsl files in a single quick panel.
- Scans XSL for <xsl:param name="..."> and supports parameter passing via simple XML files (format: <param name="..." value="..."/>).
- If parameters are detected: Option to enter values manually (saved as XML in the XML/XSL directory) or select an existing XML parameter file.
- Warns on missing parameters in selected files but continues transformation.
- Remembers the last used parameter filename for suggestions.
- Transforms XML files into HTML output (<xml_file>-output.html).
- No output generated if selection is canceled (Escape key).
- Uses Saxon-HE 12.9 with -warnings:silent for efficiency.
- Debug logging to console and error handling via an output panel (xml_transformer_errors).
- Platform-specific dependency checks for Java and JARs during plugin load.

## Requirements

- Sublime Text: Version 3 or 4.
- Java: 8+ (recommended: openjdk-11-jre or equivalent).
- Saxon-HE: Version 12.9.
- xmlresolver: Version 6.0.6 (including data).
- JAR Locations:
  - Linux: /usr/local/lib/saxon
  - Windows: C:\Program Files\Saxon
  - macOS: ~/Library/Saxon
- Files:
  - Saxon-HE-12.9.jar
  - xmlresolver-6.0.6.jar
  - xmlresolver-6.0.6-data.jar

## Installation

### Linux

1. Install Dependencies:
   Run the setup script to install Java (openjdk-11-jre), Saxon-HE 12.9, and xmlresolver 6.0.6:
   ```
   ~/.config/sublime-text/Packages/XmlTransformer/setup_XmlTransformer_ubuntu.sh
   ```
   Follow prompts to install or skip dependencies (press Y or n).
   Requires sudo for /usr/local/lib/saxon.
   Alternatively, manually install:
   - Java:
     ```
     sudo apt update
     sudo apt install openjdk-11-jre
     ```
   - JARs: Download from:
     - https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/12.9/Saxon-HE-12.9.jar
     - https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/6.0.6/xmlresolver-6.0.6.jar
     - https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/6.0.6/xmlresolver-6.0.6-data.jar
   - Place JARs in /usr/local/lib/saxon:
     ```
     sudo mkdir -p /usr/local/lib/saxon
     sudo cp ~/Downloads/Saxon-HE-12.9.jar /usr/local/lib/saxon/
     sudo cp ~/Downloads/xmlresolver-6.0.6.jar /usr/local/lib/saxon/
     sudo cp ~/Downloads/xmlresolver-6.0.6-data.jar /usr/local/lib/saxon/
     sudo chmod 644 /usr/local/lib/saxon/*.jar
     ```

2. Install Package:
   Copy the XmlTransformer directory to Sublime Text’s Packages folder:
   ```
   mkdir -p ~/.config/sublime-text/Packages/XmlTransformer
   cp -r /path/to/XmlTransformer/* ~/.config/sublime-text/Packages/XmlTransformer/
   ```
   Ensure files include XmlTransformer_build.py, XmlTransformer_exec.py, XmlTransformer.sublime-build, XmlTransformer.sublime-settings, setup_XmlTransformer_ubuntu.sh, and README.md

3. Verify:
   Check Java and JARs:
   ```
   java -version
   ls /usr/local/lib/saxon/*.jar
   ```
   Expected: Java 11+ (e.g., openjdk version "11.0.20"), lists Saxon-HE-12.9.jar, xmlresolver-6.0.6.jar, xmlresolver-6.0.6-data.jar.

### Windows

1. Install Dependencies:
   Run the setup script as Administrator to install Java (openjdk-11-jre), Saxon-HE 12.9, and xmlresolver 6.0.6:
   ```
   %APPDATA%\Sublime Text\Packages\XmlTransformer\setup_XmlTransformer_windows.bat
   ```
   Open a Command Prompt as Administrator.
   Follow prompts to install or skip dependencies (press Y or n).
   Requires PowerShell and winget for Java; downloads JARs to C:\Program Files\Saxon.
   Alternatively, manually install:
   - Java: Download and install from https://adoptium.net. Ensure java is in your PATH (test with java -version).
   - JARs: Download from the URLs above.
   - Place JARs in C:\Program Files\Saxon:
     ```
     mkdir "C:\Program Files\Saxon"
     copy \path\to\Saxon-HE-12.9.jar "C:\Program Files\Saxon\"
     copy \path\to\xmlresolver-6.0.6.jar "C:\Program Files\Saxon\"
     copy \path\to\xmlresolver-6.0.6-data.jar "C:\Program Files\Saxon\"
     ```

2. Install Package:
   Copy the XmlTransformer directory to Sublime Text’s Packages folder:
   ```
   mkdir "%APPDATA%\Sublime Text\Packages\XmlTransformer"
   copy \path\to\XmlTransformer\* "%APPDATA%\Sublime Text\Packages\XmlTransformer\"
   ```
Ensure files include XmlTransformer_build.py, XmlTransformer_exec.py, XmlTransformer.sublime-build, XmlTransformer.sublime-settings, setup_XmlTransformer_windows.bat, and README.md

3. Verify:
   Check Java and JARs:
   ```
   java -version
   dir "%ProgramFiles%\Saxon\*.jar"
   ```
   Expected: Java 11+ (e.g., openjdk version "11.0.20"), lists Saxon-HE-12.9.jar, xmlresolver-6.0.6.jar, xmlresolver-6.0.6-data.jar.

### macOS

1. Install Dependencies:
   Run the setup script to install Java (openjdk@11), Saxon-HE 12.9, and xmlresolver 6.0.6:
   ```
   ~/Library/Application\ Support/Sublime\ Text/Packages/XmlTransformer/setup_XmlTransformer_macos.sh
   ```
   Follow prompts to install or skip dependencies (press Y or n).
   Requires Homebrew. If not installed:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Downloads JARs to ~/Library/Saxon.
   Alternatively, manually install:
   - Java:
     ```
     brew install openjdk@11
     ```
     Add to PATH (e.g., in ~/.zshrc):
     ```
     echo 'export PATH="/usr/local/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
     source ~/.zshrc
     ```
   - JARs: Download from the URLs above.
   - Place JARs in ~/Library/Saxon:
     ```
     mkdir -p ~/Library/Saxon
     cp ~/Downloads/Saxon-HE-12.9.jar ~/Library/Saxon/
     cp ~/Downloads/xmlresolver-6.0.6.jar ~/Library/Saxon/
     cp ~/Downloads/xmlresolver-6.0.6-data.jar ~/Library/Saxon/
     chmod 644 ~/Library/Saxon/*.jar
     ```

2. Install Package:
   Copy the XmlTransformer directory to Sublime Text’s Packages folder:
   ```
   mkdir -p ~/Library/Application\ Support/Sublime\ Text/Packages/XmlTransformer
   cp -r /path/to/XmlTransformer/* ~/Library/Application\ Support/Sublime\ Text/Packages/XmlTransformer/
   ```
   Ensure files include XmlTransformer_build.py, XmlTransformer_exec.py, XmlTransformer.sublime-build, XmlTransformer.sublime-settings, setup_XmlTransformer_macos.sh, and README.md.

3. Verify:
   Check Java and JARs:
   ```
   java -version
   ls ~/Library/Saxon/*.jar
   ```
   Expected: Java 11+ (e.g., openjdk version "11.0.20"), lists Saxon-HE-12.9.jar, xmlresolver-6.0.6.jar, xmlresolver-6.0.6-data.jar.

## Parameter File Format

The package uses a simple XML format for parameters:
```
<?xml version="1.0" encoding="UTF-8"?>
<params>
    <param name="pTestParam" value="TestValue"/>
    <param name="pTestParam2" value="TestValue2"/>
    <param name="extraParam" value="ExtraValue"/>
</params>
```
- Root element can be anything (e.g., <params>); the package parses .//param elements.
- Only name and value attributes are used; value defaults to empty string if missing.
- Extra parameters are passed; missing ones trigger a warning.

## Usage

1. Open an XML file in Sublime Text.
2. Run the build command:
   - Linux/Windows: Ctrl+B
   - macOS: Cmd+B
3. In the quick panel: Navigate directories (excludes hidden . directories) and select an .xsl file. Use [Parent Directory] to go up.
4. If <xsl:param> are found in the XSL:
   - Choose: "Enter parameters manually" or "Select variables XML file".
   - Manual: Input values one by one; saved as XML (suggests last filename, in XML/XSL dir).
   - Select: Browse for an XML file; parses <param name value> elements.
5. Transformation runs, producing <xml_file>-output.html (opened automatically).
6. Check the xml_transformer_errors panel (View > Show Console, or Tools > Build Results > Show Build Results) for errors

## Test Files

For verification, use the included test files:
- test.xml: Input XML.
- test.xsl: XSL with parameters (pTestParam, pTestParam2).
- params.xml: Sample parameter file.
- Expected output: test-output.html with parameter values displayed.

## Troubleshooting

- **Java Not Found**:
  - Linux: `sudo apt install openjdk-11-jre`
  - Windows: Download from https://adoptium.net, add to PATH.
  - macOS: `brew install openjdk@11`
  - Verify: `java -version`

- **Missing JARs**:
  - Check paths:
    - Linux: `ls /usr/local/lib/saxon/*.jar`
    - Windows: `dir "%ProgramFiles%\Saxon\*.jar"`
    - macOS: `ls ~/Library/Saxon/*.jar`
  - Re-run setup script or download manually.

- **Permission Issues**:
  - Linux: `sudo chmod 644 /usr/local/lib/saxon/*.jar`
  - Windows: Run .bat as Administrator.
  - macOS: `chmod 644 ~/Library/Saxon/*.jar`

- **Transformation Errors**:
  - Check console (Ctrl+` or Cmd+`) or xml_transformer_errors panel.
  - Test manually (replace paths as needed):
    - Linux/macOS:
      ```
      java -cp /usr/local/lib/saxon/Saxon-HE-12.9.jar:/usr/local/lib/saxon/xmlresolver-6.0.6.jar:/usr/local/lib/saxon/xmlresolver-6.0.6-data.jar net.sf.saxon.Transform -s:test.xml -xsl:test.xsl -o:test-output.html pTestParam=TestValue pTestParam2=TestValue2 -warnings:silent
      ```
    - Windows:
      ```
      java -cp "C:\Program Files\Saxon\Saxon-HE-12.9.jar;C:\Program Files\Saxon\xmlresolver-6.0.6.jar;C:\Program Files\Saxon\xmlresolver-6.0.6-data.jar" net.sf.saxon.Transform -s:test.xml -xsl:test.xsl -o:test-output.html pTestParam=TestValue pTestParam2=TestValue2 -warnings:silent
      ```
## License" with "This package is licensed under the MIT License. See LICENSE for details.

## Dependencies and Their Licenses

This package relies on the following external dependencies, which are installed separately via the setup scripts. Please review their licenses for compliance:

- **Saxon-HE 12.9**: Licensed under the Mozilla Public License 2.0 (MPL 2.0). See [full text](https://www.mozilla.org/en-US/MPL/2.0/) or the [Saxonica license page](https://www.saxonica.com/license/MPL-2.0.txt).
- **xmlresolver 6.0.6**: Licensed under the Apache License 2.0. See [full text](https://www.apache.org/licenses/LICENSE-2.0) or the [project GitHub](https://github.com/xmlresolver/xmlresolver/blob/main/LICENSE).
- **Java (e.g., OpenJDK 11)**: Typically under the GNU General Public License v2 with Classpath Exception (GPLv2+CE), depending on the distribution. Check your installed version with `java --version`.

These dependencies are not included in this package and must be obtained from their official sources.