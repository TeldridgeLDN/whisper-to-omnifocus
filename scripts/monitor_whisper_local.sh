#!/bin/bash

# The actual iCloud Drive location where the shortcut saves the file
SOURCE_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Whisper-local"
DEST_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/whisper/temp"

# Create directories if they don't exist
mkdir -p "$SOURCE_DIR"
mkdir -p "$DEST_DIR"

# Function to check if directory exists and is accessible
check_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        echo "Error: Directory $dir does not exist"
        return 1
    fi
    if [[ ! -r "$dir" ]] || [[ ! -w "$dir" ]]; then
        echo "Error: Directory $dir is not readable/writable"
        return 1
    fi
    return 0
}

# Check directories
check_directory "$SOURCE_DIR" || exit 1
check_directory "$DEST_DIR" || exit 1

echo "Starting to monitor iCloud Drive location: $SOURCE_DIR..."
echo "Will move files to: $DEST_DIR"
echo "Current time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Process ID: $$"

# Ensure fswatch is available
if ! command -v fswatch >/dev/null 2>&1; then
    echo "Error: fswatch is not installed. Please install it with 'brew install fswatch'"
    exit 1
fi

# Use fswatch to monitor the directory with detailed event info
fswatch -0 --event Created --event Renamed --event Updated "$SOURCE_DIR" | while read -d "" event
do
    echo "Event detected at $(date '+%Y-%m-%d %H:%M:%S'): $event"
    
    if [[ -f "$SOURCE_DIR/audio_recording.m4a" ]]; then
        echo "Found new recording at $(date '+%Y-%m-%d %H:%M:%S')"
        echo "File size: $(ls -lh "$SOURCE_DIR/audio_recording.m4a" | awk '{print $5}')"
        echo "Moving from: $SOURCE_DIR/audio_recording.m4a"
        echo "Moving to: $DEST_DIR/audio_recording.m4a"
        
        if mv "$SOURCE_DIR/audio_recording.m4a" "$DEST_DIR/"; then
            echo "File moved successfully"
        else
            echo "Error: Failed to move file"
        fi
    else
        echo "No audio_recording.m4a found in $SOURCE_DIR"
        echo "Current files in source directory:"
        ls -la "$SOURCE_DIR"
    fi
done 