#!/bin/bash
set -e

# Versions to install
JAVA_PACKAGE="default-jre"
SAXON_VERSION="12.10"
XMLRESOLVER_VERSION="6.0.23"
SAXON_DIR="/usr/local/lib/saxon"

# Check sudo / root
SUDO=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo >/dev/null 2>&1; then
        SUDO="sudo"
    else
        echo "Error: This script requires root or sudo privileges to install packages and write to $SAXON_DIR."
        exit 1
    fi
fi

# Function to prompt user for yes/no
prompt_user() {
    local prompt="$1"
    local default="$2"
    read -p "$prompt [Y/n]: " response
    response=${response:-$default}
    case "$response" in
        [Yy]*) return 0 ;;
        *) return 1 ;;
    esac
}

# Download helper with curl/wget fallback and file-size verification
download_jar() {
    local url="$1"
    local dest="$2"
    local name
    name=$(basename "$dest")
    echo -n "Downloading $name ... "
    if command -v curl >/dev/null 2>&1; then
        $SUDO curl -fSL "$url" -o "$dest" --silent --show-error
    elif command -v wget >/dev/null 2>&1; then
        $SUDO wget -q -O "$dest" "$url"
    else
        echo "FAILED"
        echo "Error: Neither curl nor wget is installed. Please install curl or wget."
        return 1
    fi

    # Verify download exists and is non-empty
    if [ ! -s "$dest" ]; then
        echo "FAILED (file is empty or missing)"
        $SUDO rm -f "$dest"
        return 1
    fi

    local size
    size=$(du -h "$dest" | cut -f1)
    echo "OK ($size)"
    return 0
}

# Header
echo "XmlTransformer Setup Script for Linux"
echo "---------------------------------"
echo "This script will install:"
echo "- Java: $JAVA_PACKAGE (Java 17 or higher recommended)"
echo "- Saxon-HE: $SAXON_VERSION"
echo "- xmlresolver: $XMLRESOLVER_VERSION (including data jar)"
echo "Target directory for JARs: $SAXON_DIR"
echo

# Check and install Java
echo "Checking for Java ($JAVA_PACKAGE)..."
if command -v java >/dev/null 2>&1; then
    JAVA_CURRENT=$(java -version 2>&1 | head -n 1)
    echo "Found: $JAVA_CURRENT"
    if prompt_user "Java is already installed. Skip installing $JAVA_PACKAGE?" "y"; then
        echo "Skipping Java installation."
    else
        echo "Installing $JAVA_PACKAGE..."
        $SUDO apt update
        $SUDO apt install -y "$JAVA_PACKAGE"
        echo "Installed Java: $(java -version 2>&1 | head -n 1)"
    fi
else
    if prompt_user "Install $JAVA_PACKAGE?" "y"; then
        echo "Installing $JAVA_PACKAGE..."
        $SUDO apt update
        $SUDO apt install -y "$JAVA_PACKAGE"
        echo "Installed Java: $(java -version 2>&1 | head -n 1)"
    else
        echo "Warning: Java is required for XmlTransformer. Please install manually."
    fi
fi
echo

# Check and install Saxon/xmlresolver JARs
echo "Checking for Saxon-HE $SAXON_VERSION and xmlresolver $XMLRESOLVER_VERSION in $SAXON_DIR..."
ALL_JARS_PRESENT=1
REQUIRED_JARS=("Saxon-HE-$SAXON_VERSION.jar" "xmlresolver-$XMLRESOLVER_VERSION.jar" "xmlresolver-$XMLRESOLVER_VERSION-data.jar")
for jar in "${REQUIRED_JARS[@]}"; do
    if [ -f "$SAXON_DIR/$jar" ]; then
        echo "Found: $jar"
    else
        echo "Missing: $jar"
        ALL_JARS_PRESENT=0
    fi
done

if [ "$ALL_JARS_PRESENT" -eq 1 ]; then
    if prompt_user "All JARs found in $SAXON_DIR. Skip installing Saxon-HE $SAXON_VERSION and xmlresolver $XMLRESOLVER_VERSION?" "y"; then
        INSTALL_JARS=0
    else
        INSTALL_JARS=1
    fi
else
    if prompt_user "Install Saxon-HE $SAXON_VERSION and xmlresolver $XMLRESOLVER_VERSION in $SAXON_DIR?" "y"; then
        INSTALL_JARS=1
    else
        echo "Warning: JARs are required for XmlTransformer. Download manually from https://www.saxonica.com and https://github.com/xmlresolver/xmlresolver."
        INSTALL_JARS=0
    fi
fi

if [ "$INSTALL_JARS" -eq 1 ]; then
    echo "Installing JARs to $SAXON_DIR..."
    $SUDO mkdir -p "$SAXON_DIR"

    download_jar "https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/$SAXON_VERSION/Saxon-HE-$SAXON_VERSION.jar" "$SAXON_DIR/Saxon-HE-$SAXON_VERSION.jar" || exit 1
    download_jar "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION.jar" "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION.jar" || exit 1
    download_jar "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION-data.jar" "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION-data.jar" || exit 1

    $SUDO chmod 644 "$SAXON_DIR"/*.jar
    echo
    echo "Installed JARs:"
    ls -lh "$SAXON_DIR"/*.jar
fi
echo

# Final validation
echo "========================================================================="
echo "Setup complete. Verifying dependencies..."
echo "========================================================================="
if command -v java >/dev/null 2>&1; then
    echo "Java: $(java -version 2>&1 | head -n 1)"
else
    echo "Java: Not found. Please install manually."
fi
echo
echo "JARs in $SAXON_DIR:"
ls -lh "$SAXON_DIR"/*.jar 2>/dev/null || echo "No JARs found. Please install manually."
echo
echo "Run XmlTransformer by opening an XML file in Sublime Text and pressing Ctrl+B."