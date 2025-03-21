#!/usr/bin/env python3

import os
import sys
import time
import socket
import logging
import subprocess
import urllib.parse
import fcntl
import glob
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser
from dotenv import load_dotenv
from typing import List, Dict, Set, Tuple, Optional
import re

# Load environment variables
load_dotenv(Path.home() / ".whisper-to-omnifocus.env")

# Configure logging
log_dir = Path(os.getenv("WHISPER_LOG_DIR", "~/whisper-logs")).expanduser()
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"icloud_sync_{datetime.now().strftime('%Y%m%d')}.log"

# Configuration
SSH_HOST = "192.168.86.36"
SSH_PORT = "22"
SSH_USER = "tomeldridge"
SSH_KEY = os.path.expanduser("~/.ssh/whisper_automation")

# Paths matching the shortcut configuration
WHISPER_BASE = os.path.expanduser("~/whisper")
TEMP_DIR = os.path.join(WHISPER_BASE, "temp")
ICLOUD_DIR = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Whisper-local")
AUDIO_FILE_PATTERN = os.path.join(ICLOUD_DIR, "audio_recording_*.m4a")
TRANSCRIPT_FILE = os.path.join(TEMP_DIR, "whisper_transcript.txt")
OMNIFOCUS_URL_FILE = TRANSCRIPT_FILE + "_url"
VENV_ACTIVATE = os.path.join(WHISPER_BASE, "whisper-env/bin/activate")
LOCK_FILE = os.path.join(TEMP_DIR, ".processing.lock")

# Tag mappings and keywords
TAG_MAPPINGS = {
    # Activity tags
    'admin': ['admin', 'administration', 'manage', 'organize'],
    'Bicycle': ['bike', 'bicycle', 'cycling', 'ride'],
    'Coding': ['code', 'coding', 'program', 'programming', 'develop', 'script'],
    'Health': ['health', 'doctor', 'medical', 'medicine', 'workout', 'exercise'],
    'Plan': ['plan', 'planning', 'schedule', 'strategy'],
    'Read/Review': ['read', 'review', 'book', 'article', 'document'],
    'Research': ['research', 'study', 'investigate', 'analyze'],
    'Running': ['run', 'running', 'jog', 'jogging'],
    'Shopping': ['shop', 'buy', 'purchase', 'store', 'grocery'],
    'Travel': ['travel', 'trip', 'flight', 'hotel', 'vacation'],
    'Watch': ['watch', 'view', 'stream', 'movie', 'video'],
    'Write': ['write', 'draft', 'compose', 'document'],
    
    # Time of Day tags
    'Morning': ['morning', 'breakfast', 'early', 'am'],
    'Afternoon': ['afternoon', 'lunch', 'noon'],
    'Evening': ['evening', 'night', 'dinner', 'pm'],
    
    # Other tags
    'App/Service': ['app', 'application', 'service', 'software', 'website'],
    'Communicate': ['email', 'call', 'message', 'contact', 'meet', 'chat'],
    'Device': ['phone', 'computer', 'laptop', 'device', 'hardware'],
    'Errand': ['errand', 'task', 'chore', 'pickup', 'dropoff'],
    'Location': ['at', 'in', 'location', 'place', 'where'],
    'Person': ['with', 'person', 'people', 'team', 'group']
}

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ICLOUD_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

def can_connect_ssh():
    """Check if we can connect to the SSH server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((SSH_HOST, int(SSH_PORT)))
        sock.close()
        return True
    except Exception as e:
        logging.debug(f"SSH connection test failed: {str(e)}")
        return False

def run_ssh_command(command, capture_output=True):
    """Run an SSH command with detailed error logging"""
    try:
        ssh_cmd = [
            "ssh",
            "-i", SSH_KEY,
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no",
            "-p", SSH_PORT,
            f"{SSH_USER}@{SSH_HOST}",
            command
        ]
        logging.debug(f"Running SSH command: {' '.join(ssh_cmd)}")
        result = subprocess.run(ssh_cmd, capture_output=capture_output, text=True, check=True)
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        logging.error(f"SSH command failed: {str(e)}")
        if capture_output:
            logging.error(f"SSH stderr: {e.stderr}")
        return False, str(e)

def parse_date_time(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse date and time information from text.
    Returns (defer_date, due_date)"""
    text = text.lower()
    defer_date = None
    due_date = None
    
    # Common time patterns
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    # Pattern for "at X time" or "at X o'clock" or "at X pm/am"
    time_patterns = [
        r'at (\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
        r'at (\d{1,2}) o\'clock',
        r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
    ]
    
    # Pattern for dates like "on Monday" or "next Tuesday"
    day_patterns = [
        r'(today)',
        r'(tomorrow)',
        r'next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'on (monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'this (monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
    ]
    
    # Check for time patterns
    time_str = None
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            time_str = match.group(1)
            try:
                # Parse the time string
                if 'o\'clock' in time_str:
                    time_str = time_str.replace('o\'clock', '')
                parsed_time = parser.parse(time_str)
                time_str = parsed_time.strftime("%I:%M%p").lower()
                break
            except ValueError:
                continue
    
    # Check for date patterns
    date_str = None
    for pattern in day_patterns:
        match = re.search(pattern, text)
        if match:
            day = match.group(1)
            if day == 'today':
                date_str = today.strftime("%Y-%m-%d")
            elif day == 'tomorrow':
                date_str = tomorrow.strftime("%Y-%m-%d")
            else:
                # Handle "next" or "this" weekday
                target_day = parser.parse(day).weekday()
                current_day = today.weekday()
                days_ahead = target_day - current_day
                if days_ahead <= 0:  # If the day has passed this week
                    days_ahead += 7  # Move to next week
                target_date = today + timedelta(days=days_ahead)
                date_str = target_date.strftime("%Y-%m-%d")
            break
    
    # Combine date and time if both are present
    if date_str and time_str:
        due_date = f"{date_str} {time_str}"
    elif date_str:
        due_date = date_str
    elif time_str:
        # If only time is specified, assume today
        due_date = f"{today.strftime('%Y-%m-%d')} {time_str}"
    
    return defer_date, due_date

def create_omnifocus_url(transcript_text, **kwargs):
    """Create an OmniFocus URL from the transcript text with optional parameters"""
    # First detect any dates/times in the transcript
    defer_date, due_date = parse_date_time(transcript_text)
    
    # Start with the base parameters
    params = {
        'name': transcript_text.strip(),
    }
    
    # Add detected dates if found
    if defer_date:
        params['defer'] = defer_date
    if due_date:
        params['due'] = due_date
    
    # Add other optional parameters if provided
    if kwargs.get('note'):
        params['note'] = kwargs['note']
    if kwargs.get('flag'):
        params['flag'] = 'true' if kwargs['flag'] else 'false'
    if kwargs.get('project'):
        params['project'] = kwargs['project']
    if kwargs.get('context'):
        params['context'] = kwargs['context']
    if kwargs.get('estimate'):
        params['estimate'] = kwargs['estimate']
    
    # Override detected dates with explicitly provided ones
    if kwargs.get('defer'):
        params['defer'] = kwargs['defer']
    if kwargs.get('due'):
        params['due'] = kwargs['due']
    
    # URL encode each parameter
    encoded_params = []
    for key, value in params.items():
        encoded_value = urllib.parse.quote(str(value))
        encoded_params.append(f"{key}={encoded_value}")
    
    # Create the OmniFocus URL
    return f"omnifocus:///add?{'&'.join(encoded_params)}"

def detect_tags(text: str) -> Set[str]:
    """Detect relevant tags based on keywords in the text."""
    text = text.lower()
    detected_tags = set()
    
    # Check each tag's keywords against the text
    for tag, keywords in TAG_MAPPINGS.items():
        if any(keyword in text for keyword in keywords):
            detected_tags.add(tag)
    
    return detected_tags

def process_transcript_to_url(transcript_file, url_file):
    """Convert transcript to OmniFocus URL and save it"""
    try:
        # Read the transcript
        with open(transcript_file, 'r') as f:
            transcript = f.read().strip()
        
        # Check if this exact transcript was recently processed (within last minute)
        recent_transcripts_file = os.path.join(TEMP_DIR, ".recent_transcripts")
        current_time = time.time()
        recent_transcripts = {}
        
        # Load recent transcripts
        if os.path.exists(recent_transcripts_file):
            try:
                with open(recent_transcripts_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            saved_time, saved_transcript = line.strip().split('|', 1)
                            recent_transcripts[saved_transcript] = float(saved_time)
            except Exception as e:
                logging.warning(f"Failed to read recent transcripts: {str(e)}")
        
        # Clean up old entries (older than 1 minute)
        recent_transcripts = {
            t: ts for t, ts in recent_transcripts.items()
            if current_time - ts < 60
        }
        
        # Check for duplicate
        if transcript in recent_transcripts:
            logging.info("Duplicate transcript detected, skipping task creation")
            return True
        
        # Add current transcript to recent list
        recent_transcripts[transcript] = current_time
        
        # Save updated recent transcripts
        try:
            with open(recent_transcripts_file, 'w') as f:
                for t, ts in recent_transcripts.items():
                    f.write(f"{ts}|{t}\n")
        except Exception as e:
            logging.warning(f"Failed to save recent transcripts: {str(e)}")
        
        # Detect relevant tags
        detected_tags = detect_tags(transcript)
        
        # Join multiple tags with commas for OmniFocus
        context = ', '.join(detected_tags) if detected_tags else None
        
        # Create OmniFocus URL with default parameters and detected tags
        omnifocus_url = create_omnifocus_url(
            transcript,
            flag=True,  # Flag all voice tasks by default
            note="Created via Voice Transcription",  # Add a note about the source
            context=context  # Add detected tags
        )
        
        # Save URL to file
        with open(url_file, 'w') as f:
            f.write(omnifocus_url)
        
        if detected_tags:
            logging.info(f"Created OmniFocus URL with tags: {', '.join(detected_tags)}")
        else:
            logging.info("Created OmniFocus URL without tags")

        # Open the OmniFocus URL directly
        try:
            subprocess.run(['open', omnifocus_url], check=True)
            logging.info("Opened OmniFocus URL")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to open OmniFocus URL: {str(e)}")
            return False
            
        return True
    except Exception as e:
        logging.error(f"Failed to create OmniFocus URL: {str(e)}")
        return False

def cleanup_files(local_files=None, remote_files=None):
    """Clean up files both locally and remotely"""
    if local_files:
        for file in local_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    logging.info(f"Removed local file: {file}")
            except Exception as e:
                logging.error(f"Failed to remove local file {file}: {str(e)}")
    
    if remote_files:
        cleanup_cmd = "rm -f " + " ".join(f"'{f}'" for f in remote_files)
        success, _ = run_ssh_command(cleanup_cmd)
        if not success:
            logging.warning("Failed to clean up remote files")
        else:
            logging.info("Cleaned up remote files")

class FileLock:
    """Context manager for file locking to prevent duplicate processing"""
    def __init__(self, lock_file):
        self.lock_file = lock_file
        self.lock_fd = None

    def __enter__(self):
        try:
            # Open the lock file (create if doesn't exist)
            self.lock_fd = os.open(self.lock_file, os.O_RDWR | os.O_CREAT)
            # Try to acquire an exclusive lock
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError) as e:
            if self.lock_fd:
                os.close(self.lock_fd)
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_fd:
            # Release the lock and close the file
            fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            os.close(self.lock_fd)
            try:
                os.remove(self.lock_file)
            except OSError:
                pass

def process_via_ssh(audio_filename):
    """Process an audio file that's already on the remote server"""
    try:
        # Generate unique names for transcript and URL files
        base_name = os.path.splitext(audio_filename)[0]
        transcript_file = f"{base_name}_transcript.txt"
        url_file = os.path.join(TEMP_DIR, f"{base_name}_url.txt")
        
        with FileLock(LOCK_FILE):
            # Process the audio file on the remote server
            process_cmd = (
                f"export PATH=$HOME/bin:$PATH && "  # Add ffmpeg to PATH
                f"cd {WHISPER_BASE} && "
                f"source {VENV_ACTIVATE} && "
                f"PYTHONWARNINGS='ignore::UserWarning' python3 -W ignore transcribe.py "
                f"'{os.path.join(TEMP_DIR, audio_filename)}' '{os.path.join(TEMP_DIR, transcript_file)}'"
            )
            success, output = run_ssh_command(process_cmd)
            if not success:
                logging.error(f"Transcription failed: {output}")
                return False
            
            # Verify the transcript file exists on remote server
            check_cmd = f"test -f '{os.path.join(TEMP_DIR, transcript_file)}' && echo 'exists'"
            success, output = run_ssh_command(check_cmd)
            if not success or 'exists' not in output:
                logging.error("Transcript file not found on remote server")
                return False
            
            # Copy the transcript back
            scp_cmd = [
                "scp",
                "-i", SSH_KEY,
                "-o", "BatchMode=yes",
                "-o", "StrictHostKeyChecking=no",
                "-P", SSH_PORT,
                f"{SSH_USER}@{SSH_HOST}:{os.path.join(TEMP_DIR, transcript_file)}",
                os.path.join(TEMP_DIR, transcript_file)
            ]
            
            try:
                subprocess.run(scp_cmd, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"SCP failed retrieving transcript: {str(e)}")
                if e.stderr:
                    logging.error(f"SCP stderr: {e.stderr}")
                return False
            
            # Verify local transcript file exists and has content
            if not os.path.exists(os.path.join(TEMP_DIR, transcript_file)):
                logging.error("Local transcript file not found after SCP")
                return False
            
            # Process the transcript to create OmniFocus URL
            if not process_transcript_to_url(os.path.join(TEMP_DIR, transcript_file), url_file):
                return False
        
        # Clean up all files after releasing the lock
        local_files = [
            os.path.join(TEMP_DIR, transcript_file),
            url_file
        ]
        remote_files = [
            os.path.join(TEMP_DIR, audio_filename),
            os.path.join(TEMP_DIR, transcript_file)
        ]
        cleanup_files(local_files, remote_files)
        
        return True
            
    except Exception as e:
        logging.error(f"Error processing via SSH: {str(e)}")
        return False

def move_to_temp(audio_file: str) -> str:
    """Move audio file from iCloud to temp directory and return new path."""
    filename = os.path.basename(audio_file)
    dest_path = os.path.join(TEMP_DIR, filename)
    try:
        shutil.move(audio_file, dest_path)
        logging.info(f"Moved {filename} to temp directory")
        return dest_path
    except Exception as e:
        logging.error(f"Failed to move file to temp directory: {str(e)}")
        raise

def main():
    """Main function to watch for and process recordings."""
    logging.info("Starting recording processor (checking every 5 seconds)")
    logging.info(f"Monitoring iCloud directory: {ICLOUD_DIR}")
    logging.info(f"Monitoring remote directory: {TEMP_DIR}")
    
    while True:
        try:
            # First, check iCloud directory for offline recordings
            for audio_file in glob.glob(AUDIO_FILE_PATTERN):
                logging.info(f"Found audio file in iCloud: {audio_file}")
                temp_audio_file = None
                
                # Check if the file is still being written to
                try:
                    initial_size = os.path.getsize(audio_file)
                    time.sleep(1)  # Wait a second
                    if os.path.getsize(audio_file) != initial_size:
                        logging.info("File is still being written, waiting...")
                        continue
                except OSError:
                    logging.info("File is not accessible, skipping...")
                    continue
                
                if can_connect_ssh():
                    logging.info("Home network detected, processing iCloud file...")
                    try:
                        # Move file to temp directory first
                        temp_audio_file = move_to_temp(audio_file)
                        # Get just the filename for the remote path
                        audio_filename = os.path.basename(temp_audio_file)
                        
                        # Verify the file exists in temp directory
                        if not os.path.exists(temp_audio_file):
                            raise Exception("File not found in temp directory after move")
                        
                        # Copy to remote server
                        scp_cmd = [
                            "scp",
                            "-i", SSH_KEY,
                            "-o", "BatchMode=yes",
                            "-o", "StrictHostKeyChecking=no",
                            "-P", SSH_PORT,
                            temp_audio_file,
                            f"{SSH_USER}@{SSH_HOST}:{os.path.join(TEMP_DIR, audio_filename)}"
                        ]
                        
                        try:
                            subprocess.run(scp_cmd, check=True, capture_output=True, text=True)
                        except subprocess.CalledProcessError as e:
                            logging.error(f"SCP failed copying audio file: {str(e)}")
                            if e.stderr:
                                logging.error(f"SCP stderr: {e.stderr}")
                            raise
                        
                        # Verify file exists on remote server
                        check_cmd = f"test -f '{os.path.join(TEMP_DIR, audio_filename)}' && echo 'exists'"
                        success, output = run_ssh_command(check_cmd)
                        if not success or 'exists' not in output:
                            raise Exception("Audio file not found on remote server after SCP")
                        
                        if process_via_ssh(audio_filename):
                            logging.info("Processing complete")
                        else:
                            raise Exception("Processing failed")
                            
                    except Exception as e:
                        logging.error(f"Error during processing: {str(e)}")
                        # Move file back to iCloud if it exists in temp
                        if temp_audio_file and os.path.exists(temp_audio_file):
                            try:
                                shutil.move(temp_audio_file, audio_file)
                                logging.info("Moved file back to iCloud for retry")
                            except Exception as move_error:
                                logging.error(f"Failed to move file back to iCloud: {str(move_error)}")
                else:
                    logging.info("Not on home network, leaving file in iCloud for later")
            
            # Then check remote directory for direct SSH recordings
            check_cmd = f"ls -1 {os.path.join(TEMP_DIR, 'audio_recording_*.m4a')} 2>/dev/null || true"
            success, output = run_ssh_command(check_cmd)
            
            if success and output.strip():
                # Process each file found
                for remote_file in output.strip().split('\n'):
                    audio_filename = os.path.basename(remote_file)
                    logging.info(f"Found audio file on remote: {audio_filename}")
                    
                    if process_via_ssh(audio_filename):
                        logging.info("Processing complete")
                    else:
                        logging.error("Processing failed")
            
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main() 