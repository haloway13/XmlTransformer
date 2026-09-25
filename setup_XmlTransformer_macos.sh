#!/bin/bash
set -e

# Versions to install
JAVA_PACKAGE="openjdk@17"
SAXON_VERSION="12.10"
XMLRESOLVER_VERSION="6.0.23"
SAXON_DIR="$HOME/Library/Saxon"

echo "XmlTransformer Setup Script for macOS"
echo "---------------------------------"
echo "This script will install:"
echo "- Java: $JAVA_PACKAGE (Java 17 or higher recommended)"
echo "- Saxon-HE: $SAXON_VERSION"
echo "- xmlresolver: $XMLRESOLVER_VERSION (including data jar)"
echo "Target directory for JARs: $SAXON_DIR"
echo ""

# Function to prompt user for yes/no
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo ""
    echo "Homebrew is required for automated installation but was not found."
    read -p "Install Homebrew? [Y/n]: " INSTALL_BREW
    if [[ "$INSTALL_BREW" != "n" && "$INSTALL_BREW" != "N" ]]; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        if [ $? -ne 0 ]; then
            echo "Failed to install Homebrew. Please install manually from https://brew.sh."
            exit 1
        fi
        echo "Homebrew installed."
    else
        echo "Warning: Homebrew is required for automated Java installation. Skipping."
    fi
fi

# Helper function to configure brew java path
configure_java_path() {
    BREW_PREFIX=$(brew --prefix "$JAVA_PACKAGE" 2>/dev/null || brew --prefix)
    if [ -d "$BREW_PREFIX/bin" ]; then
        if ! grep -q "$BREW_PREFIX/bin" ~/.zshrc 2>/dev/null; then
            echo "export PATH=\"$BREW_PREFIX/bin:\$PATH\"" >> ~/.zshrc
        fi
        export PATH="$BREW_PREFIX/bin:$PATH"
    fi
    if [ -d "$BREW_PREFIX/libexec/openjdk.jdk" ]; then
        sudo ln -sfn "$BREW_PREFIX/libexec/openjdk.jdk" /Library/Java/JavaVirtualMachines/openjdk.jdk 2>/dev/null || true
    fi
}

# Download helper with curl -fSL and file-size verification
download_jar() {
    local url="$1"
    local dest="$2"
    local name
    name=$(basename "$dest")
    echo -n "Downloading $name ... "
    if curl -fSL "$url" -o "$dest" --silent --show-error; then
        if [ ! -s "$dest" ]; then
            echo "FAILED (0 bytes)"
            rm -f "$dest"
            return 1
        fi
        local size
        size=$(du -h "$dest" | cut -f1)
        echo "OK ($size)"
        return 0
    else
        echo "FAILED"
        rm -f "$dest"
        return 1
    fi
}

# Check and install Java
has_java() {
    if /usr/libexec/java_home &>/dev/null; then
        return 0
    elif command -v java &>/dev/null && java -version &>/dev/null; then
        return 0
    fi
    return 1
}

echo ""
echo "Checking for Java ($JAVA_PACKAGE)..."
if has_java; then
    JAVA_CURRENT=$(java -version 2>&1 | head -n 1)
    echo "Found: $JAVA_CURRENT"
    read -p "Java is already installed. Skip installing $JAVA_PACKAGE? [Y/n]: " INSTALL_JAVA
    if [[ "$INSTALL_JAVA" == "n" || "$INSTALL_JAVA" == "N" ]]; then
        echo "Installing $JAVA_PACKAGE..."
        brew install $JAVA_PACKAGE
        configure_java_path
        echo "Installed Java: $(java -version 2>&1 | head -n 1)"
    else
        echo "Skipping Java installation."
    fi
else
    read -p "Install $JAVA_PACKAGE? [Y/n]: " INSTALL_JAVA
    if [[ "$INSTALL_JAVA" == "n" || "$INSTALL_JAVA" == "N" ]]; then
        echo "Warning: Java is required for XmlTransformer. Install manually with 'brew install $JAVA_PACKAGE'."
    else
        echo "Installing $JAVA_PACKAGE..."
        brew install $JAVA_PACKAGE
        configure_java_path
        echo "Installed Java: $(java -version 2>&1 | head -n 1)"
    fi
fi

# Check and install Saxon/xmlresolver JARs
echo ""
echo "Checking for Saxon-HE $SAXON_VERSION and xmlresolver $XMLRESOLVER_VERSION in $SAXON_DIR..."
ALL_JARS_PRESENT=true
REQUIRED_JARS=("Saxon-HE-$SAXON_VERSION.jar" "xmlresolver-$XMLRESOLVER_VERSION.jar" "xmlresolver-$XMLRESOLVER_VERSION-data.jar")
for JAR in "${REQUIRED_JARS[@]}"; do
    if [ -f "$SAXON_DIR/$JAR" ]; then
        echo "Found: $JAR"
    else
        echo "Missing: $JAR"
        ALL_JARS_PRESENT=false
    fi
done

if $ALL_JARS_PRESENT; then
    read -p "All JARs found in $SAXON_DIR. Skip installing Saxon-HE $SAXON_VERSION and xmlresolver $XMLRESOLVER_VERSION? [Y/n]: " INSTALL_JARS
    if [[ "$INSTALL_JARS" == "n" || "$INSTALL_JARS" == "N" ]]; then
        DO_INSTALL_JARS=true
    else
        DO_INSTALL_JARS=false
    fi
else
    read -p "Install Saxon-HE $SAXON_VERSION and xmlresolver $XMLRESOLVER_VERSION in $SAXON_DIR? [Y/n]: " INSTALL_JARS
    if [[ "$INSTALL_JARS" == "n" || "$INSTALL_JARS" == "N" ]]; then
        echo "Warning: JARs are required for XmlTransformer. Download manually from https://www.saxonica.com and https://github.com/xmlresolver/xmlresolver."
        DO_INSTALL_JARS=false
    else
        DO_INSTALL_JARS=true
    fi
fi

if $DO_INSTALL_JARS; then
    echo "Installing JARs to $SAXON_DIR..."
    mkdir -p "$SAXON_DIR"

    download_jar "https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/$SAXON_VERSION/Saxon-HE-$SAXON_VERSION.jar" "$SAXON_DIR/Saxon-HE-$SAXON_VERSION.jar" || exit 1
    download_jar "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION.jar" "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION.jar" || exit 1
    download_jar "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION-data.jar" "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION-data.jar" || exit 1

    chmod 644 "$SAXON_DIR"/*.jar
    echo
    echo "Installed JARs:"
    ls -lh "$SAXON_DIR"/*.jar
fi

# Final validation
echo ""
echo "========================================================================="
echo "Setup complete. Verifying dependencies..."
echo "========================================================================="
if has_java; then
    echo "Java: $(java -version 2>&1 | head -n 1)"
else
    echo "Java: Not found. Please install manually with 'brew install $JAVA_PACKAGE'."
fi
echo
echo "JARs in $SAXON_DIR:"
ls -lh "$SAXON_DIR"/*.jar 2>/dev/null || echo "No JARs found. Please install manually."
echo
echo "Run XmlTransformer by opening an XML file in Sublime Text and pressing Cmd+B."
echo "Press any key to exit..."
read -n 1 -s