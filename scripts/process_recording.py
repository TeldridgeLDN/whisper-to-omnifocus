#!/usr/bin/env python3

import os
import sys
import whisper
import logging
from pathlib import Path
from datetime import datetime

# Configure paths to match the working setup
WHISPER_DIR = "/Users/tomeldridge/whisper"
TEMP_DIR = os.path.join(WHISPER_DIR, "temp")
VENV_PATH = "/Users/tomeldridge/Library/Mobile Documents/com~apple~CloudDocs/whisper/whisper-env/bin/activate"

# Configure logging
log_dir = Path(os.getenv("WHISPER_LOG_DIR", "~/whisper-logs")).expanduser()
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"whisper_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def process_recording(audio_file):
    """Process a voice recording and create an OmniFocus task."""
    try:
        # Ensure we're in the correct directory
        os.chdir(WHISPER_DIR)
        logging.info(f"Working directory: {os.getcwd()}")
        
        # Load model and transcribe
        logging.info(f"Processing recording: {audio_file}")
        model = whisper.load_model("base")
        result = model.transcribe(str(audio_file))
        transcribed_text = result["text"].strip()
        logging.info(f"Transcribed text: {transcribed_text}")
        
        # Save transcript
        output_file = os.path.join(TEMP_DIR, "whisper_transcript.txt")
        with open(output_file, "w") as f:
            f.write(transcribed_text)
        logging.info(f"Saved transcript to: {output_file}")
        
        # Run the OmniFocus script
        omnifocus_script = os.path.join(WHISPER_DIR, "whisper_to_omnifocus.sh")
        if os.path.exists(omnifocus_script):
            cmd = f"bash {omnifocus_script} {audio_file} {output_file}"
            logging.info(f"Running OmniFocus script: {cmd}")
            os.system(cmd)
        
        return True
        
    except Exception as e:
        logging.error(f"Error processing recording: {str(e)}")
        raise

def main():
    if len(sys.argv) != 2:
        print("Usage: process_recording.py <audio_file>")
        sys.exit(1)
    
    audio_file = Path(sys.argv[1])
    if not audio_file.exists():
        logging.error(f"Audio file not found: {audio_file}")
        sys.exit(1)
    
    process_recording(audio_file)

if __name__ == "__main__":
    main() 