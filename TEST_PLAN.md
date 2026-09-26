# XmlTransformer Cross-Platform Test Plan

This document outlines the end-to-end test plan for the **XmlTransformer** Sublime Text package. It covers testing across **Windows**, **macOS**, and **Linux (Ubuntu/Debian)** to validate dependency installations, dynamic JAR discovery, interactive UI flows, parameter processing, transformation output formats, and error handling.

---

## 1. Test Matrix & Environment Specifications

| Component | Windows | macOS | Linux (Ubuntu/Debian) |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 10 / Windows 11 (x64) | macOS 12+ (Intel & Apple Silicon) | Ubuntu 20.04+ / Debian 11+ |
| **Sublime Text** | Sublime Text 3 & 4 | Sublime Text 3 & 4 | Sublime Text 3 & 4 |
| **Packages Directory** | `%APPDATA%\Sublime Text\Packages\XmlTransformer` | `~/Library/Application Support/Sublime Text/Packages/XmlTransformer` | `~/.config/sublime-text/Packages/XmlTransformer` (or `sublime-text-3`) |
| **Java Runtimes** | Java 8, 11, 17 LTS (Temurin/Zulu/Oracle), 21 LTS | Java 11, 17 LTS (OpenJDK via Homebrew), 21 LTS | OpenJDK 11, 17, 21 (`default-jre` / `openjdk-17-jre`) |
| **Saxon JAR Path** | `C:\Program Files\Saxon` | `~/Library/Saxon` | `/usr/local/lib/saxon` |
| **Tested Saxon JARs** | `Saxon-HE-12.9.jar`, `Saxon-HE-12.10.jar`, `Saxon-HE-13.0.jar` | `Saxon-HE-12.9.jar`, `Saxon-HE-12.10.jar`, `Saxon-HE-13.0.jar` | `Saxon-HE-12.9.jar`, `Saxon-HE-12.10.jar`, `Saxon-HE-13.0.jar` |
| **Tested xmlresolver**| `xmlresolver-6.0.6*.jar`, `xmlresolver-6.0.23*.jar` | `xmlresolver-6.0.6*.jar`, `xmlresolver-6.0.23*.jar` | `xmlresolver-6.0.6*.jar`, `xmlresolver-6.0.23*.jar` |
| **Setup Script** | `setup_XmlTransformer_windows.bat` | `setup_XmlTransformer_macos.sh` | `setup_XmlTransformer_ubuntu.sh` |

---

## 2. Platform-Specific Test Procedures

### Platform A: Windows

#### A.1 Setup & Dependency Verification
1. **Administrative Setup Script Execution**:
   - Open Command Prompt or PowerShell as **Administrator**.
   - Execute `setup_XmlTransformer_windows.bat`.
   - **Verify**:
     - Administrator check passes (non-admin execution should warn and pause).
     - Prompts to install or skip Java 17 via `winget` if missing.
     - Downloads `Saxon-HE-12.10.jar`, `xmlresolver-6.0.23.jar`, and `xmlresolver-6.0.23-data.jar` to `C:\Program Files\Saxon`.
     - Validates downloaded file sizes (no 0-byte files).
2. **Directory & File Integrity**:
   - Run in PowerShell:
     ```powershell
     java -version
     dir "C:\Program Files\Saxon\*.jar"
     ```
   - **Expected**: Java version string displayed; all 3 JAR files exist and are non-empty.

#### A.2 Package Installation / Development Link
1. Link workspace repository to Sublime Text:
   ```cmd
   cmd /c mklink /J "%APPDATA%\Sublime Text\Packages\XmlTransformer" "<path-to-repo>\XmlTransformer"
   ```
2. Verify directory junction exists:
   ```powershell
   Get-Item "$env:APPDATA\Sublime Text\Packages\XmlTransformer"
   ```

#### A.3 Standalone CLI Smoke Test
Execute the transformation directly in Command Prompt / PowerShell:
```cmd
java -cp "C:\Program Files\Saxon\Saxon-HE-12.10.jar;C:\Program Files\Saxon\xmlresolver-6.0.23.jar;C:\Program Files\Saxon\xmlresolver-6.0.23-data.jar" net.sf.saxon.Transform -s:test_xslt\test.xml -xsl:test_xslt\test.xsl -o:test_xslt\test-output.html pTestParam=TestValue pTestParam2=TestValue2 -warnings:silent
```
- **Expected**: `test_xslt\test-output.html` is generated containing `Parameter pTestParam: TestValue`.

---

### Platform B: macOS

#### B.1 Setup & Dependency Verification
1. **Setup Script Execution**:
   - Open Terminal.
   - Run:
     ```bash
     chmod +x setup_XmlTransformer_macos.sh
     ./setup_XmlTransformer_macos.sh
     ```
   - **Verify**:
     - Homebrew detection (prompts to install Homebrew if missing).
     - Java 17+ detection via `/usr/libexec/java_home` and brew paths (`openjdk@17` or `openjdk`); an older Java on PATH must not count as satisfying the requirement.
     - If Java 17+ is missing, installs the prebuilt `temurin@17` cask (falling back to the `openjdk@17` formula) and continues to the JAR step even if the Java install fails.
     - Downloads JARs to `~/Library/Saxon`.
     - Tests `curl -fSL` with file size validation.
2. **Path Detection for Both Architectures**:
   - **Apple Silicon (M1/M2/M3)**: Java bin at `/opt/homebrew/opt/openjdk@17/bin/java` or `/opt/homebrew/bin/java`.
   - **Intel Mac**: Java bin at `/usr/local/opt/openjdk@17/bin/java` or `/usr/local/bin/java`.
   - **Either architecture (Temurin/Zulu/Oracle .pkg or cask)**: `$(/usr/libexec/java_home)/bin/java`, e.g. `/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/java`. The plugin prefers this over brew paths when it is Java 17+.
3. **Directory Verification**:
   ```bash
   java -version
   ls -lh ~/Library/Saxon/*.jar
   ```

#### B.2 Package Installation / Development Link
1. Link repository to Sublime Text Packages folder:
   ```bash
   ln -s "$(pwd)" "$HOME/Library/Application Support/Sublime Text/Packages/XmlTransformer"
   ```

#### B.3 Standalone CLI Smoke Test
```bash
java -cp "$HOME/Library/Saxon/Saxon-HE-12.10.jar:$HOME/Library/Saxon/xmlresolver-6.0.23.jar:$HOME/Library/Saxon/xmlresolver-6.0.23-data.jar" net.sf.saxon.Transform -s:test_xslt/test.xml -xsl:test_xslt/test.xsl -o:test_xslt/test-output.html pTestParam=TestValue pTestParam2=TestValue2 -warnings:silent
```
- **Expected**: Exit code 0, `test_xslt/test-output.html` generated with valid HTML.

---

### Platform C: Linux (Ubuntu / Debian)

#### C.1 Setup & Dependency Verification
1. **Setup Script Execution**:
   - Open Terminal.
   - Run:
     ```bash
     chmod +x setup_XmlTransformer_ubuntu.sh
     ./setup_XmlTransformer_ubuntu.sh
     ```
   - **Verify**:
     - Root/sudo privilege detection (prompts or aborts if unprivileged).
     - Updates apt lists and checks/installs `default-jre` (or `openjdk-17-jre`).
     - Uses `curl` (or `wget` fallback) to download JARs to `/usr/local/lib/saxon`.
     - Sets permissions `chmod 644 /usr/local/lib/saxon/*.jar`.
2. **Directory Verification**:
   ```bash
   java -version
   ls -lh /usr/local/lib/saxon/*.jar
   ```

#### C.2 Package Installation / Development Link
1. Link repository to Sublime Text Packages folder:
   ```bash
   mkdir -p ~/.config/sublime-text/Packages
   ln -s "$(pwd)" ~/.config/sublime-text/Packages/XmlTransformer
   ```
   *(For Sublime Text 3, use `~/.config/sublime-text-3/Packages/XmlTransformer` if applicable)*.

#### C.3 Standalone CLI Smoke Test
```bash
java -cp "/usr/local/lib/saxon/Saxon-HE-12.10.jar:/usr/local/lib/saxon/xmlresolver-6.0.23.jar:/usr/local/lib/saxon/xmlresolver-6.0.23-data.jar" net.sf.saxon.Transform -s:test_xslt/test.xml -xsl:test_xslt/test.xsl -o:test_xslt/test-output.html pTestParam=TestValue pTestParam2=TestValue2 -warnings:silent
```
- **Expected**: Exit code 0, `test_xslt/test-output.html` generated with valid HTML.

---

## 3. Core Functional Test Suite (All Platforms)

Run these test cases within **Sublime Text** on each target platform.

```
+-----------------------------------------------------------------------+
| TEST CASES OVERVIEW                                                   |
|                                                                       |
| [TC-01] Plugin Initialization & Readiness                             |
| [TC-02] Dynamic Version Discovery (JAR Sort Order)                    |
| [TC-03] Missing Java / Missing JARs Diagnostic Dialogs                |
| [TC-04] Standard Transformation with XML Parameter File               |
| [TC-05] Manual Parameter Entry & File Persistence                     |
| [TC-06] Run Without Parameters                                        |
| [TC-07] Multi-Format Output Detection (HTML, TXT, XML)                 |
| [TC-08] Quick Panel Navigation & Parent Directory Browsing            |
| [TC-09] User Cancellation (Esc Key Handling)                         |
| [TC-10] Error Panel & Syntax Validation (`xml_transformer_errors`)    |
| [TC-11] Localization Verification (English & Spanish Fallbacks)       |
+-----------------------------------------------------------------------+
```

---

### [TC-01] Plugin Initialization & Readiness
- **Objective**: Verify that `XmlTransformer_build.py` loads successfully and checks system dependencies.
- **Steps**:
  1. Open `XmlTransformer.sublime-settings` and ensure `"debug": true`.
  2. Start or restart Sublime Text.
  3. Open console (`Ctrl + `` on Windows/Linux, `Cmd + `` on macOS).
- **Pass Criteria**:
  - Console prints `DEBUG: XmlTransformer_build.py loaded at: ...`.
  - Console prints Java version and detected JAR paths.
  - No Python tracebacks.

---

### [TC-02] Dynamic Version Discovery
- **Objective**: Verify the version parser identifies and selects the newest JARs when multiple versions exist.
- **Setup**: Place both `Saxon-HE-12.9.jar` and `Saxon-HE-12.10.jar` (and both `xmlresolver-6.0.6.jar` and `xmlresolver-6.0.23.jar`) in the platform JAR directory.
- **Steps**:
  1. Reload Sublime Text or save `XmlTransformer_build.py`.
  2. Inspect the console output.
- **Pass Criteria**:
  - `get_installed_jars()` dynamically chooses `Saxon-HE-12.10.jar` and `xmlresolver-6.0.23.jar`.
  - Backward compatibility remains functional if only 12.9 / 6.0.6 are present.

---

### [TC-03] Missing Dependencies Error Handling
- **Objective**: Verify clear, platform-appropriate pop-up error dialogs when prerequisites are missing.
- **Steps**:
  1. Temporarily rename the Saxon directory (e.g., `Saxon_disabled`).
  2. In Sublime Text, open `test_xslt/test.xml` and trigger build (`Ctrl+B` or `Cmd+B`).
- **Pass Criteria**:
  - Dialog pop-up displays localized missing JAR message with path to setup script.
  - Process aborts cleanly without throwing uncaught exceptions.
  - Repeat test by temporarily removing Java from PATH to test the Java missing dialog.
  - Restore folder names and PATH after testing.

---

### [TC-04] Transformation with XML Parameter File
- **Objective**: Transform XML with predefined parameters.
- **Input Files**: `test_xslt/test.xml`, `test_xslt/test.xsl`, `test_xslt/params.xml`.
- **Steps**:
  1. Open `test_xslt/test.xml` in Sublime Text.
  2. Press `Ctrl+B` (Windows/Linux) or `Cmd+B` (macOS).
  3. Quick Panel: Select `test.xsl`.
  4. Parameter Mode: Select `Select variables XML file`.
  5. File Browser: Select `params.xml`.
- **Pass Criteria**:
  - Output file `test_xslt/test-output.html` is generated.
  - The generated file automatically opens in a new tab.
  - File contains:
    ```html
    <p>Parameter pTestParam: TestValue</p>
    <p>Parameter pTestParam2: TestValue2</p>
    ```

---

### [TC-05] Manual Parameter Entry & File Persistence
- **Objective**: Enter parameter values manually via Sublime Text input panel and persist them to disk.
- **Steps**:
  1. Open `test_xslt/test.xml`.
  2. Press `Ctrl+B` / `Cmd+B` and select `test.xsl`.
  3. Select `Enter parameters manually`.
  4. When prompted:
     - For `pTestParam`, enter: `ManualAlpha`
     - For `pTestParam2`, enter: `ManualBeta`
     - For filename prompt, enter: `custom_params.xml`
- **Pass Criteria**:
  - `custom_params.xml` is saved in `test_xslt/`.
  - `test-output.html` opens displaying `ManualAlpha` and `ManualBeta`.
  - Subsequent runs suggest `custom_params.xml` as the default filename.

---

### [TC-06] Run Without Parameters
- **Objective**: Execute transformation skipping parameters even if declared in the XSL stylesheet.
- **Steps**:
  1. Open `test_xslt/test.xml`.
  2. Press `Ctrl+B` / `Cmd+B` and select `test.xsl`.
  3. Select `Run without parameters`.
- **Pass Criteria**:
  - Transformation completes without prompting for variables.
  - `test-output.html` renders with empty or default parameter bindings.

---

### [TC-07] Multi-Format Output Detection
- **Objective**: Verify proper output file extensions based on `<xsl:output method="...">`.
- **Test Matrix**:
  | Input XSL | Output Method | Expected Output File |
  | :--- | :--- | :--- |
  | `testHTML.xsl` | `html` | `test_xslt/test-output.html` |
  | `testTXT.xsl` | `text` | `test_xslt/test-output.txt` |
  | `test_xml.xsl` | `xml` | `test_xslt/test-output.xml` |
- **Steps**:
  1. Run `Ctrl+B` / `Cmd+B` on `test.xml` against each stylesheet.
  2. Select `Run without parameters` or `params.xml`.
- **Pass Criteria**:
  - Exact target extensions (`.html`, `.txt`, `.xml`) are generated and automatically opened in Sublime Text.

---

### [TC-08] Quick Panel Navigation
- **Objective**: Verify directory navigation in quick panels.
- **Steps**:
  1. Create a subfolder `test_xslt/subfolder/` and move a copy of `test.xsl` inside it.
  2. Create a hidden directory `test_xslt/.hidden/`.
  3. Run `Ctrl+B` on `test.xml`.
- **Pass Criteria**:
  - Subfolder `subfolder/` appears in the quick panel.
  - Hidden folder `.hidden/` is excluded.
  - Selecting `subfolder/` navigates into it.
  - Selecting `[Parent Directory]` returns to `test_xslt/`.

---

### [TC-09] Cancellation Flow
- **Objective**: Ensure pressing `Escape` at any quick panel or input panel cancels cleanly.
- **Steps**:
  1. Trigger build (`Ctrl+B` / `Cmd+B`).
  2. Press `Escape` while choosing XSL stylesheet.
  3. Trigger build, choose XSL, then press `Escape` while choosing parameter option.
  4. Trigger build, choose manual entry, then press `Escape` while entering a parameter value.
- **Pass Criteria**:
  - Status bar indicates cancelled operation (e.g., `Parameter choice cancelled`).
  - No ghost output files are created.
  - No error alerts or traceback logs in console.

---

### [TC-10] Error Panel & Syntax Validation
- **Objective**: Verify error handling for invalid XML/XSL files or transformation failures.
- **Steps**:
  1. Create an invalid XML file `broken.xml` containing `<<root>missing close`.
  2. Open `broken.xml` and press `Ctrl+B` / `Cmd+B`.
  3. Create an invalid XSL file `broken.xsl` with malformed XSLT syntax.
  4. Run transformation with `test.xml` and `broken.xsl`.
- **Pass Criteria**:
  - Pre-validation flags invalid XML structure and shows a descriptive alert.
  - Execution errors display inside the `xml_transformer_errors` panel at the bottom of the window.

---

### [TC-11] Localization Verification
- **Objective**: Verify internationalization in `locale/`.
- **Steps**:
  1. Verify all keys in `locale/en.sublime-messages` have matching entries in `locale/es.sublime-messages`.
  2. Check placeholder parameter count (`{0}`, `{1}`) matches across language files.
- **Pass Criteria**:
  - Key parity across all locale files.
  - Sublime Text defaults gracefully to English if an unknown language is configured.

---

## 4. Test Execution Sign-Off Checklist

| Test Item | Windows | macOS (Intel / ARM) | Linux (Ubuntu / Debian) | Status | Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Automated Setup Script | [x] | [x] | [x] | Linux & macOS Passed | Java already present (OpenJDK 25) so install was skipped; Saxon-HE 12.10 and xmlresolver 6.0.23 (+ data jar) downloaded to /usr/local/lib/saxon at 644 perms. macOS (Intel x86_64, Ventura 13.3): Found & fixed 3 bugs. (1) `brew install openjdk@17` has no bottle on this OS/CPU, so it built from source and failed on the Xcode-only `metal` tool; with `set -e` the script then exited before the JAR step. Script now installs the prebuilt `temurin@17` cask first, falls back to the formula, and continues to the JAR step if Java install fails. (2) It accepted any `java` on PATH (Java 11 here) as satisfying the 17+ requirement; now checks the major version via java_home and the brew paths. (3) Script was committed as mode 644; now 755. Saxon-HE 12.10 + xmlresolver 6.0.23 (+ data jar) downloaded to ~/Library/Saxon, zip-validated. |
| Java 17+ Detection | [x] | [x] | [x] | Linux & macOS Passed | Detected OpenJDK 25.0.4.1 (exceeds 17/21 target, forward-compatible). macOS: Found & fixed 1 bug: get_java_bin() only checked Homebrew paths, so a leftover brew openjdk@11 beat a Temurin 17 JDK in /Library/Java/JavaVirtualMachines. Now queries /usr/libexec/java_home first (version checked via the JDK release file, since `java_home -v 17+` silently returns the default JDK when nothing matches), and falls back to the brew paths. Verified in ST4 (Python 3.3 host): Temurin 17.0.20.1 selected with openjdk@11 installed and first on PATH. |
| Saxon 12.10 Detection | [x] | [x] | [x] | Linux & macOS Passed | Successfully detected in /usr/local/lib/saxon. macOS: detected in ~/Library/Saxon alongside 12.9 |
| xmlresolver 6.0.23 Detection | [x] | [x] | [x] | Linux & macOS Passed | Successfully detected in /usr/local/lib/saxon. macOS: detected in ~/Library/Saxon alongside 6.0.6 |
| TC-01: Plugin Load | [x] | [x] | [x] | Linux & macOS Passed | Clean initialization on ST4 build 4200 (Linux x64); Java and JAR paths logged, no tracebacks. macOS: clean load on ST4 build 4200 (osx x64); Temurin 17 path and 12.10/6.0.23 JARs logged, no tracebacks |
| TC-02: Version Sorting | [x] | [x] | [x] | Linux & macOS Passed | Prioritizes 12.10/6.0.23 when both versions present; correctly falls back to 12.9/6.0.6 when newer JARs removed, and an actual transformation succeeded on the legacy JARs; re-detects 12.10/6.0.23 once restored. macOS: with 12.9/12.10 and 6.0.6/6.0.23 side by side, picks 12.10/6.0.23; with newer JARs moved out, Cmd+B (no restart) ran a successful transform on 12.9/6.0.6 under Temurin 17; re-detects 12.10/6.0.23 once restored. Minor (not fixed): the data jar is chosen independently of the main xmlresolver jar, so a folder with e.g. xmlresolver-6.0.100.jar but only 6.0.23-data.jar gets a mismatched pair. |
| TC-03: Missing Dependency Alert | [ ] | [x] | [x] | Linux & macOS Passed | Found & fixed 1 bug: java_missing/jars_missing dialogs in run() called get_message() with no args, silently dropping the platform-specific install command and setup script path that plugin_loaded() computed (TC-03 requires the JARs dialog show the setup script path). Wired real args through; both dialogs now show correct, informative text; both scenarios verified clean (no traceback) and fully restored after.. macOS: Found & fixed 1 more bug of the same kind: the transform-time JAR re-check in run_transformation() still called get_message("jars_missing") with no args, so removing JARs while Sublime was running raised IndexError (no dialog). Verified 3 scenarios on ST4: (A) Saxon dir renamed before startup -> immediate dialog with ~/Library/Saxon path and setup_XmlTransformer_macos.sh; (B) Saxon dir renamed mid-session -> dialog at transform time (post-fix), no traceback; (C) Temurin and brew openjdk@11 hidden -> /usr/bin/java stub fails, dialog suggests `brew install --cask temurin@17`. All restored after. |
| TC-04: Param File Transformation| [x] | [x] | [x] | Linux & macOS Passed | HTML output generated with parameter values from params.xml. macOS: params.xml values (incl. extraParam) rendered; run on Temurin 17 |
| TC-05: Manual Param Entry | [ ] | [x] | [x] | Linux & macOS Passed | Found & fixed 3 bugs never caught on any platform: missing enter_param_file/enter_param_value locale keys (KeyError crash), missing on_param_value_entered() method (AttributeError crash after 1st param), pretty_print_xml() misindented closing </params> tag. custom_params.xml now saves correctly and test-output.html renders entered values.. macOS: params_test_mac.xml saved with correct indentation; values rendered; filename remembered in last_param_filename |
| TC-06: No-Param Mode | [x] | [x] | [x] | Linux & macOS Passed | Clean transformation without parameter variables. macOS: completed without prompts, empty bindings |
| TC-07: HTML/TXT/XML Formats | [x] | [x] | [x] | Linux & macOS Passed | HTML, TXT, and XML output method detection all verified. macOS: .html/.txt/.xml each generated and opened |
| TC-08: Directory Navigation | [ ] | [ ] | [x] | Linux Passed | subfolder/ shown and navigable; .hidden/ correctly excluded from quick panel; Parent Directory returns correctly |
| TC-09: Cancellation Flow | [ ] | [x] | [x] | Linux & macOS Passed | Found & fixed 1 bug: Escape at the manual param-value/filename input panels gave no status bar feedback (on_cancel was None), unlike every quick-panel cancel. All 4 cancellation points now confirmed working with status bar messages, no ghost files, no tracebacks.. macOS: Esc verified at XSL panel, param-mode panel, first param value, filename prompt (after entering all values: no param file written) and param file browser; expected status-bar messages, no ghost files (folder diffed before/after), no tracebacks. |
| TC-10: Error Panel Display | [ ] | [ ] | [x] | Linux Passed | Found & fixed 1 bug: invalid XML was only validated deep inside run_transformation() (after XSL + param prompts), not immediately on Ctrl+B; moved validation earlier. Both invalid-XML and invalid-XSL cases now show clean descriptive alerts with no traceback. |
| TC-11: Localization Parity | [x] | [x] | [x] | Linux & macOS Passed | 100% key/placeholder parity (20/20 keys); fixed get_message() (it hardcoded lang="en", so es.sublime-messages was dead code on every platform); added "language" setting (auto/explicit code); verified live in Sublime: "auto" resolves to OS locale (en), "es" renders Spanish status messages, unsupported code ("fr") falls back to English cleanly with no traceback. NOTE: Windows TC-11 sign-off predates this fix and should be re-verified.. macOS re-verified after the get_message() fix: 22/22 keys with placeholder parity, every key used in code defined (install_message and run_transformation unused). Live in ST4: "auto" resolves to en, "es" shows Spanish status-bar messages, "fr" falls back to English; no tracebacks. Minor (not fixed): quick-panel labels (Run without parameters / Enter parameters manually / Select variables XML file / [Parent Directory]) are hardcoded English; Esc at the XSL panel reuses the "Parameter choice cancelled" message. |

---

## 5. Post-Release Regression Checklist
- [ ] No temporary files (e.g. `test-output.*`, `custom_params.xml`) committed to git.
- [ ] `.gitattributes` ensures `test_xslt/` is excluded from Package Control distribution bundle if desired.
- [ ] Setup script permissions (`chmod +x`) preserved in tar/zip distributions.
