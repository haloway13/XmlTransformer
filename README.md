# XmlTransformer Package

A Sublime Text package for performing XSLT transformations on XML files using Saxon-HE (12.x / 13.x) and xmlresolver (6.x). Supports Linux, Windows, and macOS with a file browser-like interface for selecting XSL files and parameter files.

## Features

- Navigate directories (excluding hidden . directories) and select .xsl files in a single quick panel.
- Scans XSL for <xsl:param name="..."> and supports parameter passing via simple XML files (format: <param name="..." value="..."/>).
- If parameters are detected: Option to enter values manually (saved as XML in the XML/XSL directory) or select an existing XML parameter file.
- Warns on missing parameters in selected files but continues transformation.
- Remembers the last used parameter filename for suggestions.
- Transforms XML files into HTML output (<xml_file>-output.html).
- No output generated if selection is canceled (Escape key).
- Uses Saxon-HE with -warnings:silent for efficiency.
- Dynamic JAR discovery: Automatically detects and utilizes installed Saxon-HE and xmlresolver JAR versions.
- Debug logging to console and error handling via an output panel (xml_transformer_errors).
- Platform-specific dependency checks for Java (supporting Java 17 and 21 LTS) and JARs during plugin load.

## Requirements

- Sublime Text: Version 3 or 4.
- Java: 8+ (Java 17 or 21 LTS recommended; Java 17+ required if using Saxon 13).
- Saxon-HE: Version 12.10 (or 13.0).
- xmlresolver: Version 6.0.23 (including data).
- JAR Locations:
  - Linux: /usr/local/lib/saxon
  - Windows: C:\Program Files\Saxon
  - macOS: ~/Library/Saxon
- Files:
  - Saxon-HE-*.jar (e.g., Saxon-HE-12.10.jar or Saxon-HE-13.0.jar)
  - xmlresolver-*.jar (e.g., xmlresolver-6.0.23.jar)
  - xmlresolver-*-data.jar (e.g., xmlresolver-6.0.23-data.jar)

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
     sudo apt install default-jre
     ```
   - JARs: Download from Maven Central:
     - https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/12.10/Saxon-HE-12.10.jar
     - https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/6.0.23/xmlresolver-6.0.23.jar
     - https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/6.0.23/xmlresolver-6.0.23-data.jar
   - Place JARs in /usr/local/lib/saxon:
     ```
     sudo mkdir -p /usr/local/lib/saxon
     sudo cp ~/Downloads/Saxon-HE-12.10.jar /usr/local/lib/saxon/
     sudo cp ~/Downloads/xmlresolver-6.0.23.jar /usr/local/lib/saxon/
     sudo cp ~/Downloads/xmlresolver-6.0.23-data.jar /usr/local/lib/saxon/
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
   ls -lh /usr/local/lib/saxon/*.jar
   ```
   Expected: Java 17+ (or 8+), lists Saxon-HE-*.jar, xmlresolver-*.jar, xmlresolver-*-data.jar.

### Windows

1. Install Dependencies:
   Run the setup script as Administrator to install Java, Saxon-HE 12.10, and xmlresolver 6.0.23:
   ```
   %APPDATA%\Sublime Text\Packages\XmlTransformer\setup_XmlTransformer_windows.bat
   ```
   Open a Command Prompt as Administrator (or right-click the .bat and select Run as administrator).
   Follow prompts to install or skip dependencies (press Y or n).
   Downloads JARs to C:\Program Files\Saxon.
   Alternatively, manually install:
   - Java: Download and install from https://adoptium.net (Temurin 17 or 21 LTS). Ensure java is in your PATH.
   - JARs: Download from the URLs above.
   - Place JARs in C:\Program Files\Saxon:
     ```
     mkdir "C:\Program Files\Saxon"
     copy \path\to\Saxon-HE-12.10.jar "C:\Program Files\Saxon\"
     copy \path\to\xmlresolver-6.0.23.jar "C:\Program Files\Saxon\"
     copy \path\to\xmlresolver-6.0.23-data.jar "C:\Program Files\Saxon\"
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
   Expected: Java 17+ (or 8+), lists Saxon-HE-*.jar, xmlresolver-*.jar, xmlresolver-*-data.jar.

### macOS

1. Install Dependencies:
   Run the setup script to install Java, Saxon-HE 12.10, and xmlresolver 6.0.23:
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
     brew install openjdk@17
     ```
     Add to PATH (e.g., in ~/.zshrc):
     ```
     echo 'export PATH="$(brew --prefix openjdk@17)/bin:$PATH"' >> ~/.zshrc
     source ~/.zshrc
     ```
   - JARs: Download from the URLs above.
   - Place JARs in ~/Library/Saxon:
     ```
     mkdir -p ~/Library/Saxon
     cp ~/Downloads/Saxon-HE-12.10.jar ~/Library/Saxon/
     cp ~/Downloads/xmlresolver-6.0.23.jar ~/Library/Saxon/
     cp ~/Downloads/xmlresolver-6.0.23-data.jar ~/Library/Saxon/
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
   Expected: Java 17+ (or 8+), lists Saxon-HE-*.jar, xmlresolver-*.jar, xmlresolver-*-data.jar.

## Upgrading

If you already have XmlTransformer installed and are updating to this version:

### Existing Installations Continue Working
XmlTransformer features **dynamic JAR discovery**. If you already have `Saxon-HE-12.9.jar` and `xmlresolver-6.0.6.jar` installed, the package will automatically continue to use them without breaking your existing workflow.

### Upgrading Libraries to Saxon 12.10 and xmlresolver 6.0.23
To upgrade your Saxon and xmlresolver JARs to the latest stable versions:

1. **Re-run the Setup Script** for your platform:
   - **Linux:** `~/.config/sublime-text/Packages/XmlTransformer/setup_XmlTransformer_ubuntu.sh`
   - **Windows:** Right-click `%APPDATA%\Sublime Text\Packages\XmlTransformer\setup_XmlTransformer_windows.bat` and select **Run as administrator**.
   - **macOS:** `~/Library/Application\ Support/Sublime\ Text/Packages/XmlTransformer/setup_XmlTransformer_macos.sh`
   *(Alternatively, re-download the JARs manually from Maven Central into your OS Saxon folder).*

2. **Clean Up Older JARs (Optional):**
   XmlTransformer automatically sorts versions and selects the latest JARs found in your Saxon directory. However, you can delete older JARs (such as `Saxon-HE-12.9.jar` and `xmlresolver-6.0.6*.jar`) from your Saxon directory to save disk space:
   - Linux: `/usr/local/lib/saxon/`
   - Windows: `C:\Program Files\Saxon\`
   - macOS: `~/Library/Saxon/`

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
  - Linux: `sudo apt install default-jre` (or `openjdk-17-jre`)
  - Windows: Download from https://adoptium.net, ensure `java` is in PATH.
  - macOS: `brew install openjdk` (or `openjdk@17`)
  - Verify: `java -version`

- **Missing JARs**:
  - Check paths:
    - Linux: `ls -lh /usr/local/lib/saxon/*.jar`
    - Windows: `dir "%ProgramFiles%\Saxon\*.jar"`
    - macOS: `ls -lh ~/Library/Saxon/*.jar`
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
      java -cp /usr/local/lib/saxon/Saxon-HE-12.10.jar:/usr/local/lib/saxon/xmlresolver-6.0.23.jar:/usr/local/lib/saxon/xmlresolver-6.0.23-data.jar net.sf.saxon.Transform -s:test.xml -xsl:test.xsl -o:test-output.html pTestParam=TestValue pTestParam2=TestValue2 -warnings:silent
      ```
    - Windows:
      ```
      java -cp "C:\Program Files\Saxon\Saxon-HE-12.10.jar;C:\Program Files\Saxon\xmlresolver-6.0.23.jar;C:\Program Files\Saxon\xmlresolver-6.0.23-data.jar" net.sf.saxon.Transform -s:test.xml -xsl:test.xsl -o:test-output.html pTestParam=TestValue pTestParam2=TestValue2 -warnings:silent
      ```

## License
This package is licensed under the MIT License. See LICENSE for details.

## Dependencies
XmlTransformer requires:
- Java 8+ (Java 17 or 21 LTS recommended, available at https://adoptium.net).
- Saxon-HE 12.10 (or 13.0, https://www.saxonica.com/download/java.xml).
- xmlresolver 6.0.23 (https://github.com/xmlresolver/xmlresolver).

After installing via Package Control, copy and run the platform-specific setup script:
- macOS: `cp ~/.config/sublime-text/Packages/XmlTransformer/setup_XmlTransformer_macos.sh ~; chmod +x ~/setup_XmlTransformer_macos.sh; ~/setup_XmlTransformer_macos.sh`
- Linux: `cp ~/.config/sublime-text/Packages/XmlTransformer/setup_XmlTransformer_ubuntu.sh ~; chmod +x ~/setup_XmlTransformer_ubuntu.sh; ~/setup_XmlTransformer_ubuntu.sh`
- Windows: Copy ~/.config/sublime-text/Packages/XmlTransformer/setup_XmlTransformer_windows.bat to a folder, right-click and Run as administrator.

Alternatively, download scripts from:
- macOS: https://raw.githubusercontent.com/haloway13/XmlTransformer/main/setup_XmlTransformer_macos.sh
- Linux: https://raw.githubusercontent.com/haloway13/XmlTransformer/main/setup_XmlTransformer_ubuntu.sh
- Windows: https://raw.githubusercontent.com/haloway13/XmlTransformer/main/setup_XmlTransformer_windows.bat

Place JARs in:
- macOS: ~/Library/Saxon
- Linux: /usr/local/lib/saxon
- Windows: C:\Program Files\Saxon
