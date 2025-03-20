#!/usr/bin/env python3

import os
import sys
import whisper
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path.home() / ".whisper-to-omnifocus.env")

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

class TaskParser:
    """Parse transcribed text into task components."""
    
    def __init__(self, text):
        self.text = text
        self.components = {
            "task": "",
            "project": None,
            "due": None,
            "defer": None,
            "flag": False,
            "tags": [],
            "note": None
        }
    
    def parse(self):
        """Parse the text into task components."""
        parts = self.text.split(" hashtag ")
        self.components["task"] = parts[0].strip('"').strip()
        
        for part in parts[1:] if len(parts) > 1 else []:
            if part.startswith("project "):
                self.components["project"] = part[8:].strip()
            elif part.startswith("due "):
                self.components["due"] = part[4:].strip()
            elif part.startswith("defer "):
                self.components["defer"] = part[6:].strip()
            elif part.startswith("tag "):
                self.components["tags"] = part[4:].strip().split(",")
            elif part.startswith("note "):
                self.components["note"] = part[5:].strip()
            elif part.strip() == "flag":
                self.components["flag"] = True
        
        return self.components

class OmniFocusURLBuilder:
    """Build OmniFocus URL scheme for task creation."""
    
    def __init__(self, components):
        self.components = components
        self.base_url = f"omnifocus:///"
    
    def build_url(self):
        """Build the OmniFocus URL with task components."""
        params = []
        
        # Add task name
        params.append(f"name={quote(self.components['task'])}")
        
        # Add project if specified
        if self.components["project"]:
            params.append(f"project={quote(self.components['project'])}")
        
        # Add due date if specified
        if self.components["due"]:
            params.append(f"due={quote(self.components['due'])}")
        
        # Add defer date if specified
        if self.components["defer"]:
            params.append(f"defer={quote(self.components['defer'])}")
        
        # Add note if specified
        if self.components["note"]:
            params.append(f"note={quote(self.components['note'])}")
        
        # Add flag if specified
        if self.components["flag"]:
            params.append("flag=true")
        
        # Add tags if specified
        if self.components["tags"]:
            tags_param = ",".join(quote(tag) for tag in self.components["tags"])
            params.append(f"tags={tags_param}")
        
        return f"{self.base_url}add?{'&'.join(params)}"

def transcribe_audio(audio_file):
    """Transcribe audio file using Whisper."""
    try:
        model = whisper.load_model(os.getenv("WHISPER_MODEL", "base"))
        result = model.transcribe(str(audio_file))
        return result["text"].strip()
    except Exception as e:
        logging.error(f"Error transcribing audio: {e}")
        raise

def create_task(url):
    """Create task in OmniFocus using URL scheme."""
    try:
        subprocess.run(["open", url], check=True)
        logging.info("Task created successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error creating task: {e}")
        raise

def process_recording(audio_file):
    """Process a voice recording and create an OmniFocus task."""
    try:
        # Transcribe audio
        logging.info(f"Processing recording: {audio_file}")
        transcribed_text = transcribe_audio(audio_file)
        logging.info(f"Transcribed text: {transcribed_text}")
        
        # Parse task components
        parser = TaskParser(transcribed_text)
        components = parser.parse()
        logging.info(f"Parsed components: {components}")
        
        # Build OmniFocus URL
        url_builder = OmniFocusURLBuilder(components)
        url = url_builder.build_url()
        logging.info(f"Generated URL: {url}")
        
        # Create task
        create_task(url)
        
        # Clean up audio file
        audio_file.unlink()
        logging.info(f"Deleted audio file: {audio_file}")
        
    except Exception as e:
        logging.error(f"Error processing recording: {e}")
        sys.exit(1)

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