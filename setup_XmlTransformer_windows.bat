@echo off
setlocal EnableDelayedExpansion

:: Check for Administrator privileges (required to write to %ProgramFiles%)
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo =========================================================================
    echo [ERROR] Administrator privileges are required to install files to:
    echo "%ProgramFiles%\Saxon"
    echo.
    echo Please right-click setup_XmlTransformer_windows.bat and select
    echo "Run as administrator".
    echo =========================================================================
    echo.
    pause
    exit /b 1
)

:: Versions to install
set JAVA_PACKAGE=Temurin-17-JRE
set SAXON_VERSION=12.10
set XMLRESOLVER_VERSION=6.0.23
set SAXON_DIR=%ProgramFiles%\Saxon

echo XmlTransformer Setup Script for Windows
echo ---------------------------------
echo This script will install:
echo - Java: %JAVA_PACKAGE% (Java 17 or higher recommended)
echo - Saxon-HE: %SAXON_VERSION%
echo - xmlresolver: %XMLRESOLVER_VERSION% (including data jar)
echo Target directory for JARs: %SAXON_DIR%
echo.

:: Function to prompt user for yes/no
set /p "=Press Enter to continue or Ctrl+C to cancel..." <nul
echo.

:: Check and install Java
echo Checking for Java (%JAVA_PACKAGE%)...
java -version >nul 2>&1
if %ERRORLEVEL% == 0 (
    for /f "tokens=*" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do set JAVA_CURRENT=%%i
    echo Found: !JAVA_CURRENT!
    set /p INSTALL_JAVA=Java is already installed. Skip installing %JAVA_PACKAGE%? [Y/n]: 
    if /i "!INSTALL_JAVA!"=="n" (
        goto :INSTALL_JAVA_PROC
    ) else (
        echo Skipping Java installation.
    )
) else (
    set /p INSTALL_JAVA=Install %JAVA_PACKAGE%? [Y/n]: 
    if /i "!INSTALL_JAVA!"=="n" (
        echo Warning: Java is required for XmlTransformer. Download from https://adoptium.net.
    ) else (
        goto :INSTALL_JAVA_PROC
    )
)
goto :CHECK_JARS

:INSTALL_JAVA_PROC
where winget >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] winget was not detected on this system.
    echo Please download and install Java manually from: https://adoptium.net
) else (
    echo Installing %JAVA_PACKAGE% via winget...
    winget install --id EclipseAdoptium.Temurin.17.JRE --source winget --accept-package-agreements --accept-source-agreements
    if !ERRORLEVEL! NEQ 0 (
        echo Failed to install Java via winget. Please download manually from: https://adoptium.net
    ) else (
        for /f "tokens=*" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do echo Installed Java: %%i
    )
)

:CHECK_JARS
echo.
:: Check and install Saxon/xmlresolver JARs
echo Checking for Saxon-HE %SAXON_VERSION% and xmlresolver %XMLRESOLVER_VERSION% in %SAXON_DIR%...
set ALL_JARS_PRESENT=1
set REQUIRED_JARS=Saxon-HE-%SAXON_VERSION%.jar xmlresolver-%XMLRESOLVER_VERSION%.jar xmlresolver-%XMLRESOLVER_VERSION%-data.jar
for %%j in (%REQUIRED_JARS%) do (
    if exist "%SAXON_DIR%\%%j" (
        echo Found: %%j
    ) else (
        echo Missing: %%j
        set ALL_JARS_PRESENT=0
    )
)

if %ALL_JARS_PRESENT% == 1 (
    set /p INSTALL_JARS=All JARs found in %SAXON_DIR%. Skip installing Saxon-HE %SAXON_VERSION% and xmlresolver %XMLRESOLVER_VERSION%? [Y/n]: 
    if /i "!INSTALL_JARS!"=="n" (
        set DO_INSTALL_JARS=1
    ) else (
        set DO_INSTALL_JARS=0
    )
) else (
    set /p INSTALL_JARS=Install Saxon-HE %SAXON_VERSION% and xmlresolver %XMLRESOLVER_VERSION% in %SAXON_DIR%? [Y/n]: 
    if /i "!INSTALL_JARS!"=="n" (
        echo Warning: JARs are required for XmlTransformer. Download manually from https://www.saxonica.com and https://github.com/xmlresolver/xmlresolver.
        set DO_INSTALL_JARS=0
    ) else (
        set DO_INSTALL_JARS=1
    )
)

if !DO_INSTALL_JARS! == 1 (
    echo.
    echo Installing JARs to "%SAXON_DIR%"...
    if not exist "%SAXON_DIR%" mkdir "%SAXON_DIR%"

    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$urls = @(" ^
        "  @{ Url = 'https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/%SAXON_VERSION%/Saxon-HE-%SAXON_VERSION%.jar'; Name = 'Saxon-HE-%SAXON_VERSION%.jar' }," ^
        "  @{ Url = 'https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/%XMLRESOLVER_VERSION%/xmlresolver-%XMLRESOLVER_VERSION%.jar'; Name = 'xmlresolver-%XMLRESOLVER_VERSION%.jar' }," ^
        "  @{ Url = 'https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/%XMLRESOLVER_VERSION%/xmlresolver-%XMLRESOLVER_VERSION%-data.jar'; Name = 'xmlresolver-%XMLRESOLVER_VERSION%-data.jar' }" ^
        ");" ^
        "$dest = '%SAXON_DIR%';" ^
        "$failed = $false;" ^
        "foreach ($u in $urls) {" ^
        "    $out = Join-Path $dest $u.Name;" ^
        "    Write-Host ('Downloading {0} ...' -f $u.Name);" ^
        "    try {" ^
        "        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
        "        Invoke-WebRequest -Uri $u.Url -OutFile $out -UseBasicParsing;" ^
        "        $item = Get-Item $out -ErrorAction Stop;" ^
        "        if ($item.Length -le 0) { throw 'Downloaded file is empty (0 bytes).' }" ^
        "        Write-Host (' [OK] {0} ({1:N2} MB)' -f $u.Name, ($item.Length / 1MB));" ^
        "    } catch {" ^
        "        Write-Host (' [ERROR] Failed to download {0}: {1}' -f $u.Name, $_.Exception.Message);" ^
        "        if (Test-Path $out) { Remove-Item $out -Force -ErrorAction SilentlyContinue };" ^
        "        $failed = $true;" ^
        "    }" ^
        "};" ^
        "if ($failed) { exit 1 } else { exit 0 }"

    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo [ERROR] One or more JAR downloads failed or produced empty files.
        echo Please check your internet connection or download manually from:
        echo https://github.com/haloway13/XmlTransformer#dependencies
        pause
        exit /b 1
    )
    echo.
    echo Installed JARs in "%SAXON_DIR%":
    dir "%SAXON_DIR%\*.jar"
)
echo.

:: Final validation
echo =========================================================================
echo Setup complete. Verifying dependencies...
echo =========================================================================
java -version >nul 2>&1
if %ERRORLEVEL% == 0 (
    for /f "tokens=*" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do echo Java: %%i
) else (
    echo Java: Not found in PATH. Please install manually from https://adoptium.net.
)
echo.
echo JARs in "%SAXON_DIR%":
dir "%SAXON_DIR%\*.jar" 2>nul || echo [WARNING] No JARs found. Please install manually.
echo.
echo Run XmlTransformer by opening an XML file in Sublime Text and pressing Ctrl+B.
pause
