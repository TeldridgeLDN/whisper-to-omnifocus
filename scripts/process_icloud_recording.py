#!/usr/bin/env python3

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path.home() / ".whisper-to-omnifocus.env")

# Configure logging
log_dir = Path(os.getenv("WHISPER_LOG_DIR", "~/whisper-logs")).expanduser()
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"icloud_sync_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def get_icloud_recording():
    """Get the recording from iCloud Drive."""
    icloud_path = Path("/Users/tomeldridge/Library/Mobile Documents/com~apple~CloudDocs/whisper/temp/audio_recording.m4a")
    return icloud_path if icloud_path.exists() else None

def process_recording(recording_path):
    """Process the recording using the main script"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        process_script = os.path.join(script_dir, 'process_recording.py')
        
        # Run the main script
        result = subprocess.run(
            [sys.executable, process_script, recording_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Error processing recording: {result.stderr}")
            return False
            
        logging.info(f"Successfully processed recording: {result.stdout}")
        return True
        
    except Exception as e:
        logging.error(f"Error processing recording: {str(e)}")
        return False

def main():
    """Main function to watch for and process recordings."""
    logging.info("Starting iCloud recording processor")
    
    while True:
        recording = get_icloud_recording()
        
        if recording:
            logging.info(f"Found new recording: {recording}")
            if process_recording(recording):
                logging.info("Successfully processed recording")
            else:
                logging.error("Failed to process recording")
        
        # Wait before checking again
        time.sleep(5)

if __name__ == "__main__":
    main() 