#!/bin/bash

# Configuration
SSH_HOST="192.168.86.36"
SSH_USER="tomeldridge"
SSH_PORT="22"

# Paths
AUDIO_FILE="/Users/tomeldridge/Library/Mobile Documents/com~apple~CloudDocs/whisper/temp/audio_recording.m4a"
OUTPUT_FILE="/Users/tomeldridge/Library/Mobile Documents/com~apple~CloudDocs/whisper/temp/whisper_transcript.txt"

# Ensure audio file exists
if [[ ! -f "$AUDIO_FILE" ]]; then
    echo "Error: Audio file not found at $AUDIO_FILE"
    exit 1
fi

# Copy audio file to remote server
scp -P $SSH_PORT "$AUDIO_FILE" "${SSH_USER}@${SSH_HOST}:/Users/tomeldridge/whisper/temp/"

# Run transcription on remote server
ssh -p $SSH_PORT "${SSH_USER}@${SSH_HOST}" "cd /Users/tomeldridge/whisper && \
    python3 - << EOF
import whisper
import sys
import os

try:
    print(f\"Processing audio file: {os.path.abspath('/Users/tomeldridge/whisper/temp/audio_recording.m4a')}\")
    model = whisper.load_model(\"base\")
    result = model.transcribe('/Users/tomeldridge/whisper/temp/audio_recording.m4a')
    print(f\"Transcription result: {result['text']}\")
    with open('/Users/tomeldridge/whisper/temp/whisper_transcript.txt', 'w') as f:
        f.write(result['text'])
    print(\"Transcription saved to file\")
except Exception as e:
    print(f\"Error: {str(e)}\", file=sys.stderr)
EOF"

# Run the OmniFocus processing script on remote server
ssh -p $SSH_PORT "${SSH_USER}@${SSH_HOST}" "cd /Users/tomeldridge/whisper && \
    ./whisper_to_omnifocus.sh '/Users/tomeldridge/whisper/temp/audio_recording.m4a' '/Users/tomeldridge/whisper/temp/whisper_transcript.txt'" 