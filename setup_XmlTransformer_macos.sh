#!/bin/bash
set -e

# Versions to install
# Java: the prebuilt Temurin cask is preferred because Homebrew has no openjdk@17 bottle
# for older macOS/Intel combinations, where the formula builds from source and needs full
# Xcode (the 'metal' tool). The formula is kept as a fallback.
JAVA_CASK="temurin@17"
JAVA_PACKAGE="openjdk@17"
JAVA_MIN_VERSION=17
SAXON_VERSION="12.10"
XMLRESOLVER_VERSION="6.0.23"
SAXON_DIR="$HOME/Library/Saxon"

echo "XmlTransformer Setup Script for macOS"
echo "---------------------------------"
echo "This script will install:"
echo "- Java: $JAVA_CASK (Java $JAVA_MIN_VERSION or higher required)"
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

# Print the major version of a java binary (e.g. "1.8.0_402" -> 8, "17.0.20" -> 17)
java_major() {
    "$1" -version 2>&1 | head -n 1 | sed -E 's/.*version "([^"]+)".*/\1/' \
        | awk -F. '{ if ($1 == "1") print $2; else print $1 }' | sed -E 's/[^0-9].*//'
}

# Print the path of a Java >= JAVA_MIN_VERSION, checking the same locations as the plugin:
# java_home (Temurin/Zulu/Oracle/casks), Homebrew openjdk formulae, then PATH.
find_java() {
    local candidate major
    for candidate in \
        "$(/usr/libexec/java_home 2>/dev/null)/bin/java" \
        /opt/homebrew/opt/openjdk/bin/java /usr/local/opt/openjdk/bin/java \
        /opt/homebrew/opt/openjdk@21/bin/java /usr/local/opt/openjdk@21/bin/java \
        /opt/homebrew/opt/openjdk@17/bin/java /usr/local/opt/openjdk@17/bin/java \
        "$(command -v java 2>/dev/null)"; do
        [ -x "$candidate" ] || continue
        major=$(java_major "$candidate")
        if [ -n "$major" ] && [ "$major" -ge "$JAVA_MIN_VERSION" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

# Install Java without aborting the script on failure, so the JAR step still runs
install_java() {
    if ! command -v brew &> /dev/null; then
        echo "Warning: Homebrew not found. Install Java $JAVA_MIN_VERSION+ manually from https://adoptium.net."
        return 1
    fi
    echo "Installing $JAVA_CASK (prebuilt, may prompt for your password)..."
    if brew install --cask "$JAVA_CASK"; then
        return 0
    fi
    echo "Cask install failed. Trying Homebrew formula $JAVA_PACKAGE..."
    if brew install "$JAVA_PACKAGE"; then
        configure_java_path
        return 0
    fi
    echo "Warning: Java installation failed. Install Java $JAVA_MIN_VERSION+ manually from https://adoptium.net."
    return 1
}

echo ""
echo "Checking for Java $JAVA_MIN_VERSION or higher..."
if JAVA_FOUND=$(find_java); then
    echo "Found: $("$JAVA_FOUND" -version 2>&1 | head -n 1) ($JAVA_FOUND)"
    read -p "Java $JAVA_MIN_VERSION+ is already installed. Skip installing $JAVA_CASK? [Y/n]: " INSTALL_JAVA
    if [[ "$INSTALL_JAVA" == "n" || "$INSTALL_JAVA" == "N" ]]; then
        install_java || true
    else
        echo "Skipping Java installation."
    fi
else
    if command -v java &>/dev/null && java -version &>/dev/null; then
        echo "Found: $(java -version 2>&1 | head -n 1), but Java $JAVA_MIN_VERSION or higher is required."
    fi
    read -p "Install $JAVA_CASK? [Y/n]: " INSTALL_JAVA
    if [[ "$INSTALL_JAVA" == "n" || "$INSTALL_JAVA" == "N" ]]; then
        echo "Warning: Java $JAVA_MIN_VERSION+ is required for XmlTransformer. Install manually with 'brew install --cask $JAVA_CASK'."
    else
        install_java || true
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
if JAVA_FOUND=$(find_java); then
    echo "Java: $("$JAVA_FOUND" -version 2>&1 | head -n 1) ($JAVA_FOUND)"
else
    echo "Java: Java $JAVA_MIN_VERSION+ not found. Please install manually with 'brew install --cask $JAVA_CASK'."
fi
echo
echo "JARs in $SAXON_DIR:"
ls -lh "$SAXON_DIR"/*.jar 2>/dev/null || echo "No JARs found. Please install manually."
echo
echo "Run XmlTransformer by opening an XML file in Sublime Text and pressing Cmd+B."
echo "Press any key to exit..."
read -n 1 -s