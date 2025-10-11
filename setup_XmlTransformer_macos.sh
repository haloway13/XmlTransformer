#!/bin/bash

# Versions to install
JAVA_PACKAGE="openjdk@11"
SAXON_VERSION="12.9"
XMLRESOLVER_VERSION="6.0.6"
SAXON_DIR="$HOME/Library/Saxon"

echo "XmlTransformer Setup Script for macOS"
echo "---------------------------------"
echo "This script will install:"
echo "- Java: $JAVA_PACKAGE"
echo "- Saxon-HE: $SAXON_VERSION"
echo "- xmlresolver: $XMLRESOLVER_VERSION (including data)"
echo "Target directory for JARs: $SAXON_DIR"
echo ""

# Function to prompt user for yes/no
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo ""
    echo "Homebrew is required but not installed."
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

# Check and install Java
echo ""
echo "Checking for Java ($JAVA_PACKAGE)..."
if command -v java &> /dev/null; then
    JAVA_CURRENT=$(java -version 2>&1 | grep -i version | awk '{print $3}' | tr -d '"')
    echo "Found: openjdk version $JAVA_CURRENT"
    read -p "Java is already installed. Skip installing $JAVA_PACKAGE? [Y/n]: " INSTALL_JAVA
    if [[ "$INSTALL_JAVA" == "n" || "$INSTALL_JAVA" == "N" ]]; then
        echo "Installing $JAVA_PACKAGE..."
        brew install $JAVA_PACKAGE
        if [ $? -ne 0 ]; then
            echo "Failed to install Java. Please install manually with 'brew install $JAVA_PACKAGE'."
            exit 1
        fi
        echo 'export PATH="/usr/local/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
        echo "Installed Java: $(java -version 2>&1 | grep -i version)"
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
        if [ $? -ne 0 ]; then
            echo "Failed to install Java. Please install manually with 'brew install $JAVA_PACKAGE'."
            exit 1
        fi
        echo 'export PATH="/usr/local/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
        echo "Installed Java: $(java -version 2>&1 | grep -i version)"
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
    curl -L "https://repo1.maven.org/maven2/net/sf/saxon/Saxon-HE/$SAXON_VERSION/Saxon-HE-$SAXON_VERSION.jar" -o "$SAXON_DIR/Saxon-HE-$SAXON_VERSION.jar"
    curl -L "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION.jar" -o "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION.jar"
    curl -L "https://repo1.maven.org/maven2/org/xmlresolver/xmlresolver/$XMLRESOLVER_VERSION/xmlresolver-$XMLRESOLVER_VERSION-data.jar" -o "$SAXON_DIR/xmlresolver-$XMLRESOLVER_VERSION-data.jar"
    chmod 644 "$SAXON_DIR"/*.jar
    echo "Installed JARs:"
    ls "$SAXON_DIR"/*.jar
fi

# Final validation
echo ""
echo "Setup complete. Verifying dependencies..."
if command -v java &> /dev/null; then
    echo "Java: $(java -version 2>&1 | grep -i version)"
else
    echo "Java: Not found. Please install manually with 'brew install $JAVA_PACKAGE'."
fi
echo "JARs in $SAXON_DIR:"
ls "$SAXON_DIR"/*.jar || echo "No JARs found. Please install manually."
echo "Run XmlTransformer by opening an XML file in Sublime Text and pressing Cmd+B."
echo "Press any key to exit..."
read -n 1 -s