#!/bin/bash
set -e

# Versions to install
JAVA_PACKAGE="openjdk-11-jre"
SAXON_VERSION="12.9"
XMLRESOLVER_VERSION="6.0.6"
SAXON_DIR="/usr/local/lib/saxon"

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

# Header
echo "XmlTransformer Setup Script for Linux"
echo "---------------------------------"
echo "This script will install:"
echo "- Java: $JAVA_PACKAGE"
echo "- Saxon-HE: $SAXON_VERSION"
echo "- xmlresolver: $XMLRESOLVER_VERSION (including data)"
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
        sudo apt update
        sudo apt install -y "$JAVA_PACKAGE"
        echo "Installed Java: $(java -version 2>&1 | head -n 1)"
    fi
else
    if prompt_user "Install $JAVA_PACKAGE?" "y"; then
        echo "Installing $JAVA_PACKAGE..."
        sudo apt update
        sudo apt install -y "$JAVA_PACKAGE"
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
        echo "Skipping JAR installation."
    else
        INSTALL_JARS=1
    fi
else
    if prompt_user "Install Saxon-HE $SAXON_VERSION and xmlresolver $XMLRESOLVER_VERSION in $SAXON_DIR?" "y"; then
        INSTALL_JARS=1
    else
        echo "Warning: JARs are required for XmlTransformer. Please install manually from https://www.saxonica.com and https://github.com/xmlresolver/xmlresolver."
        INSTALL_JARS=0
    fi
fi

if [ "$INSTALL_JARS" -eq 1 ]; then
    echo "Installing JARs to $SAXON_DIR..."
    sudo mkdir -p "$SAXON_DIR"
    wget -O "$SAXON_DIR/Saxon-HE-$SAXON_VERSION.jar" "https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/$SAXON_VERSION/Saxon-HE-$SAXON_VERSION.jar"
    wget -O "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION.jar" "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION.jar"
    wget -O "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION-data.jar" "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION-data.jar"
    sudo chmod 644 "$SAXON_DIR"/*.jar
    echo "Installed JARs:"
    ls -l "$SAXON_DIR"/*.jar
fi
echo

# Final validation
echo "Setup complete. Verifying dependencies..."
if command -v java >/dev/null 2>&1; then
    echo "Java: $(java -version 2>&1 | head -n 1)"
else
    echo "Java: Not found. Please install manually."
fi
echo "JARs in $SAXON_DIR:"
ls -l "$SAXON_DIR"/*.jar || echo "No JARs found. Please install manually."
echo "Run XmlTransformer by opening an XML file in Sublime Text and pressing Ctrl+B."