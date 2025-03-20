#!/usr/bin/env python3

import os
import sys
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
log_file = log_dir / f"sync_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def get_local_recordings():
    """Get list of recordings from local storage on phone."""
    try:
        # This will be replaced with actual iOS Shortcuts integration
        # For now, we'll use a simulated directory
        local_dir = Path.home() / "whisper-local"
        if not local_dir.exists():
            return []
        
        return list(local_dir.glob("*.m4a"))
    except Exception as e:
        logging.error(f"Error getting local recordings: {e}")
        return []

def process_recording(recording_path):
    """Process a single recording using the main script."""
    try:
        logging.info(f"Processing recording: {recording_path}")
        subprocess.run([sys.executable, "process_recording.py", str(recording_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing recording: {e}")
        return False

def sync_recordings():
    """Sync recordings from local storage to main processing."""
    local_recordings = get_local_recordings()
    
    if not local_recordings:
        logging.info("No local recordings found to sync")
        return
    
    logging.info(f"Found {len(local_recordings)} recordings to sync")
    
    success_count = 0
    for recording in local_recordings:
        if process_recording(recording):
            success_count += 1
    
    logging.info(f"Successfully processed {success_count} of {len(local_recordings)} recordings")

def main():
    sync_recordings()

if __name__ == "__main__":
    main() 