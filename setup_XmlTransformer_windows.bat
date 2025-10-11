@echo off
setlocal EnableDelayedExpansion

:: Versions to install
set JAVA_PACKAGE=openjdk-11-jre
set SAXON_VERSION=12.9
set XMLRESOLVER_VERSION=6.0.6
set SAXON_DIR=%ProgramFiles%\Saxon

echo XmlTransformer Setup Script for Windows
echo ---------------------------------
echo This script will install:
echo - Java: %JAVA_PACKAGE%
echo - Saxon-HE: %SAXON_VERSION%
echo - xmlresolver: %XMLRESOLVER_VERSION% (including data)
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
        echo Installing %JAVA_PACKAGE%...
        winget install --id AdoptOpenJDK.OpenJDK.11 --source winget
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install Java. Download manually from https://adoptium.net.
            pause
            exit /b 1
        )
        for /f "tokens=*" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do echo Installed Java: %%i
    ) else (
        echo Skipping Java installation.
    )
) else (
    set /p INSTALL_JAVA=Install %JAVA_PACKAGE%? [Y/n]:
    if /i "!INSTALL_JAVA!"=="n" (
        echo Warning: Java is required for XmlTransformer. Download from https://adoptium.net.
    ) else (
        echo Installing %JAVA_PACKAGE%...
        winget install --id AdoptOpenJDK.OpenJDK.11 --source winget
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install Java. Download manually from https://adoptium.net.
            pause
            exit /b 1
        )
        for /f "tokens=*" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do echo Installed Java: %%i
    )
)
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
    echo Installing JARs to %SAXON_DIR%...
    mkdir "%SAXON_DIR%"
    powershell -Command "Invoke-WebRequest -Uri 'https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/%SAXON_VERSION%/Saxon-HE-%SAXON_VERSION%.jar' -OutFile '%SAXON_DIR%\Saxon-HE-%SAXON_VERSION%.jar'"
    powershell -Command "Invoke-WebRequest -Uri 'https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/%XMLRESOLVER_VERSION%/xmlresolver-%XMLRESOLVER_VERSION%.jar' -OutFile '%SAXON_DIR%\xmlresolver-%XMLRESOLVER_VERSION%.jar'"
    powershell -Command "Invoke-WebRequest -Uri 'https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/%XMLRESOLVER_VERSION%/xmlresolver-%XMLRESOLVER_VERSION%-data.jar' -OutFile '%SAXON_DIR%\xmlresolver-%XMLRESOLVER_VERSION%-data.jar'"
    echo Installed JARs:
    dir "%SAXON_DIR%\*.jar"
)
echo.

:: Final validation
echo Setup complete. Verifying dependencies...
java -version >nul 2>&1
if %ERRORLEVEL% == 0 (
    for /f "tokens=*" %%i in ('java -version 2^>^&1 ^| findstr /i "version"') do echo Java: %%i
) else (
    echo Java: Not found. Please install manually from https://adoptium.net.
)
echo JARs in %SAXON_DIR%:
dir "%SAXON_DIR%\*.jar" || echo No JARs found. Please install manually.
echo Run XmlTransformer by opening an XML file in Sublime Text and pressing Ctrl+B.
pause
