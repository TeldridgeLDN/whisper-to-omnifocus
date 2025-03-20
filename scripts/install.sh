#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Whisper to OmniFocus Installation...${NC}\n"

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo -e "${RED}Python 3.8 or higher is required. Current version: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}Python $PYTHON_VERSION detected${NC}"

# Check pip installation
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Installing pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Create virtual environment
echo "Setting up virtual environment..."
python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install openai-whisper python-dotenv requests urllib3

# Run setup script
echo "Running setup script..."
python3 setup.py

# Create directories if they don't exist
echo "Creating required directories..."
mkdir -p ~/Library/Application\ Scripts/com.omnigroup.OmniFocus3
mkdir -p ~/whisper-temp
mkdir -p ~/whisper-logs

# Set up environment file
ENV_FILE="$HOME/.whisper-to-omnifocus.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating environment file..."
    cat > "$ENV_FILE" << EOL
# Whisper to OmniFocus Configuration
WHISPER_TEMP_DIR=~/whisper-temp
WHISPER_LOG_DIR=~/whisper-logs
WHISPER_MODEL=base
OMNIFOCUS_URL_SCHEME=omnifocus
EOL
fi

# Check OmniFocus installation
if ! osascript -e 'id of application "OmniFocus"' &> /dev/null; then
    echo -e "${YELLOW}Warning: OmniFocus not found. Please ensure OmniFocus is installed.${NC}"
fi

# Set up shell configuration
SHELL_RC="$HOME/.$(basename $SHELL)rc"
if [ -f "$SHELL_RC" ]; then
    if ! grep -q "WHISPER_TO_OMNIFOCUS" "$SHELL_RC"; then
        echo "Adding environment variables to shell configuration..."
        cat >> "$SHELL_RC" << EOL

# Whisper to OmniFocus Configuration
export PATH="\$PATH:\$HOME/whisper-to-omnifocus/scripts"
export WHISPER_TO_OMNIFOCUS=1
EOL
    fi
fi

# Make scripts executable
chmod +x process_recording.py
chmod +x setup.py

echo -e "\n${GREEN}Installation completed!${NC}"
echo -e "\nNext steps:"
echo -e "1. Set up the Shortcuts app using the guide in docs/shortcuts.md"
echo -e "2. Configure Automator using the guide in docs/configuration.md"
echo -e "3. Test the installation by running a sample voice command"
echo -e "\nFor more information, please read the documentation in the docs directory."

# Deactivate virtual environment
deactivate 