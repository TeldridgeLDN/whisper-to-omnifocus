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

# Configuration from environment variables
SSH_HOST = os.getenv("WHISPER_SSH_HOST", "localhost")
SSH_PORT = os.getenv("WHISPER_SSH_PORT", "22")
SSH_USER = os.getenv("WHISPER_SSH_USER", os.getenv("USER"))
SSH_KEY = os.path.expanduser(os.getenv("WHISPER_SSH_KEY", "~/.ssh/id_ed25519"))

# Paths matching the shortcut configuration
WHISPER_BASE = os.path.expanduser(os.getenv("WHISPER_BASE", "~/whisper"))
TEMP_DIR = os.path.join(WHISPER_BASE, "temp")
ICLOUD_DIR = os.path.expanduser(os.getenv("WHISPER_ICLOUD_DIR", "~/Library/Mobile Documents/com~apple~CloudDocs/Whisper-local"))
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

# Define common grocery items
GROCERY_ITEMS = {
    'vegetables': [
        'tomatoes', 'onions', 'carrots', 'potatoes', 'broccoli', 'lettuce', 'spinach',
        'peppers', 'cucumber', 'celery', 'radishes', 'spring onions', 'garlic',
        'ginger', 'mushrooms', 'cauliflower', 'asparagus', 'zucchini', 'eggplant',
        'cabbage', 'kale', 'brussels sprouts', 'green beans', 'peas', 'corn'
    ],
    'fruits': [
        'apples', 'bananas', 'oranges', 'grapes', 'strawberries', 'blueberries',
        'raspberries', 'blackberries', 'pears', 'peaches', 'plums', 'nectarines',
        'mangoes', 'pineapple', 'kiwi', 'melons', 'watermelon', 'lemons', 'limes'
    ],
    'dairy': [
        'milk', 'cheese', 'yogurt', 'butter', 'cream', 'eggs', 'sour cream',
        'cottage cheese', 'cream cheese'
    ],
    'meat': [
        'chicken', 'beef', 'pork', 'lamb', 'turkey', 'bacon', 'sausages',
        'ham', 'fish', 'salmon', 'tuna', 'shrimp'
    ],
    'pantry': [
        'bread', 'rice', 'pasta', 'flour', 'sugar', 'salt', 'pepper', 'oil',
        'vinegar', 'cereal', 'oats', 'beans', 'lentils', 'canned tomatoes',
        'spices', 'herbs', 'tea', 'coffee', 'honey', 'jam', 'peanut butter'
    ],
    'spices': [
        'coriander', 'cumin', 'turmeric', 'paprika', 'cinnamon', 'nutmeg',
        'cardamom', 'cloves', 'bay leaves', 'oregano', 'basil', 'thyme',
        'rosemary', 'sage', 'mint', 'chili'
    ]
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
    
    # Pattern for defer phrases
    defer_patterns = [
        r'defer (?:this )?(?:task |action )?(?:to |until |for |on )?',
        r'start (?:this )?(?:task |action )?(?:on |at )?',
        r'begin (?:this )?(?:task |action )?(?:on |at )?',
        r'wait (?:until |for |on )?'
    ]
    
    # Check if this is a defer date request
    is_defer_request = any(re.search(pattern, text) for pattern in defer_patterns)
    
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
        formatted_datetime = f"{date_str} {time_str}"
    elif date_str:
        formatted_datetime = date_str
    elif time_str:
        # If only time is specified, assume today
        formatted_datetime = f"{today.strftime('%Y-%m-%d')} {time_str}"
    else:
        formatted_datetime = None
    
    # Assign the datetime to either defer_date or due_date based on context
    if formatted_datetime:
        if is_defer_request:
            defer_date = formatted_datetime
        else:
            due_date = formatted_datetime
    
    logging.debug(f"Parsed dates - Defer: {defer_date}, Due: {due_date}")
    return defer_date, due_date

def detect_project(text: str) -> Optional[str]:
    """Detect project name from text using common patterns."""
    project_patterns = [
        r'in project (?:called )?["\']?([^"\']+)["\']?',
        r'to project ["\']?([^"\']+)["\']?',
        r'under ["\']?([^"\']+)["\']? project',
        r'@project\(([^)]+)\)'
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).strip()
    return None

def detect_parallel(text: str) -> bool:
    """Detect if tasks should be parallel based on keywords."""
    parallel_keywords = [
        'parallel tasks',
        'parallel actions',
        'can be done in parallel',
        'can be done simultaneously',
        'no specific order'
    ]
    return any(keyword in text.lower() for keyword in parallel_keywords)

def detect_flag(text: str) -> bool:
    """Detect if task should be flagged based on keywords."""
    flag_keywords = [
        'urgent',
        'important',
        'priority',
        'flag',
        'flagged',
        'high priority',
        'critical'
    ]
    return any(keyword in text.lower() for keyword in flag_keywords)

def parse_duration(text: str) -> Optional[str]:
    """Parse duration/estimate from text."""
    # Patterns for different duration formats
    duration_patterns = [
        # Pattern for "X hours and Y minutes"
        (r'(\d+)\s*(?:hour|hr)s?\s*(?:and\s*)?(\d+)?\s*(?:minute|min)s?', 
         lambda h, m=None: f"{int(h)}h{int(m) if m else '0'}m"),
        # Pattern for just minutes
        (r'(\d+)\s*(?:minute|min)s?',
         lambda m: f"{int(m)}m"),
        # Pattern for just hours
        (r'(\d+)\s*(?:hour|hr)s?',
         lambda h: f"{int(h)}h0m"),
        # Pattern for "takes/duration/estimate X hours and Y minutes"
        (r'(?:takes|duration|estimate|estimated|about|around)\s+(\d+)\s*(?:hour|hr)s?\s*(?:and\s*)?(\d+)?\s*(?:minute|min)s?',
         lambda h, m=None: f"{int(h)}h{int(m) if m else '0'}m"),
        # Pattern for "takes/duration/estimate X minutes"
        (r'(?:takes|duration|estimate|estimated|about|around)\s+(\d+)\s*(?:minute|min)s?',
         lambda m: f"{int(m)}m")
    ]
    
    text = text.lower()
    for pattern, formatter in duration_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                # Filter out None values and convert to integers
                groups = [g for g in match.groups() if g is not None]
                return formatter(*groups)
            except Exception as e:
                logging.warning(f"Failed to format duration with pattern {pattern}: {str(e)}")
                continue
    return None

def detect_folder(text: str) -> Optional[str]:
    """Detect folder name from text using common patterns."""
    # Common folder names to look for (case-insensitive)
    KNOWN_FOLDERS = {
        'personal': 'Personal',
        'work': 'Work',
        'home': 'Home',
        'family': 'Family',
        'health': 'Health',
        'finance': 'Finance'
    }
    
    text = text.lower()
    logging.debug(f"Detecting folder in text: {text}")
    
    # First check explicit folder patterns
    folder_patterns = [
        # Most specific patterns first
        r'^in (?:the )?([^"\']+?) folder',  # Matches "in the personal folder" at start
        r'in (?:the )?([^"\']+?) folder',   # Matches "in the personal folder" anywhere
        r'(?:in|to|into|under|for) (?:the )?(?:folder )?["\']?([^"\']+?)["\']? folder',
        r'(?:in|to|into|under|for) (?:the )?([^"\']+?) folder',
        r'folder ["\']?([^"\']+?)["\']?',
        r'@folder\(([^)]+)\)'
    ]
    
    for pattern in folder_patterns:
        match = re.search(pattern, text)
        if match:
            folder_name = match.group(1).strip()
            logging.debug(f"Found folder match with pattern '{pattern}': {folder_name}")
            # Check if it matches a known folder (case-insensitive)
            folder_lower = folder_name.lower()
            if folder_lower in KNOWN_FOLDERS:
                logging.info(f"Matched known folder: {KNOWN_FOLDERS[folder_lower]}")
                return KNOWN_FOLDERS[folder_lower]
            logging.info(f"Using custom folder name: {folder_name.title()}")
            return folder_name.title()  # Return with title case if not a known folder
    
    # If no explicit folder pattern, check for known folder names in the text
    words = text.split()
    for folder_key, folder_name in KNOWN_FOLDERS.items():
        if folder_key in words:  # Only match whole words
            logging.info(f"Matched folder name in text: {folder_name}")
            return folder_name
            
    logging.debug("No folder detected in text")
    return None

def detect_task_status(text: str) -> Dict[str, bool]:
    """Detect task status and reveal preferences."""
    status = {
        'completed': False,
        'reveal': True,  # Default to revealing the task
        'sequential': False
    }
    
    # Check for completion
    if any(word in text.lower() for word in ['done', 'completed', 'finished', 'complete']):
        status['completed'] = True
    
    # Check for sequential tasks
    if any(word in text.lower() for word in ['sequential', 'in order', 'one after another', 'step by step']):
        status['sequential'] = True
    
    # Check for reveal preference
    if any(word in text.lower() for word in ['hide', 'don\'t show', 'don\'t reveal']):
        status['reveal'] = False
    
    return status

def detect_dependencies(text: str) -> List[str]:
    """Detect task dependencies from text."""
    dependencies = []
    dep_patterns = [
        r'after (?:completing|finishing|doing) ["\']?([^"\']+)["\']?',
        r'depends on ["\']?([^"\']+)["\']?',
        r'requires ["\']?([^"\']+)["\']?',
        r'needs ["\']?([^"\']+)["\']?',
        r'@depends\(([^)]+)\)'
    ]
    
    for pattern in dep_patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            dependencies.append(match.group(1).strip())
    
    return dependencies

def detect_location(text: str) -> Optional[str]:
    """Detect location context from text."""
    location_patterns = [
        r'at (?:the )?["\']?([^"\']+)["\']?',
        r'in (?:the )?["\']?([^"\']+)["\']?',
        r'@location\(([^)]+)\)'
    ]
    
    # Common locations to filter out
    common_words = {'the', 'a', 'an', 'this', 'that', 'there', 'here', 'it', 'them'}
    
    for pattern in location_patterns:
        match = re.search(pattern, text.lower())
        if match:
            location = match.group(1).strip()
            # Filter out common words and very short locations
            if location and len(location.split()) > 1 and not all(word in common_words for word in location.split()):
                return location
    return None

def detect_energy_level(text: str) -> Optional[str]:
    """Detect task energy level from text."""
    energy_patterns = {
        'low': ['low energy', 'easy', 'simple', 'quick', 'light'],
        'medium': ['medium energy', 'moderate', 'normal'],
        'high': ['high energy', 'intensive', 'complex', 'difficult', 'challenging']
    }
    
    text = text.lower()
    for level, keywords in energy_patterns.items():
        if any(keyword in text for keyword in keywords):
            return level
    return None

def parse_repeat_pattern(text: str) -> Optional[str]:
    """Parse repeat pattern from text."""
    repeat_patterns = {
        r'daily': 'daily',
        r'every day': 'daily',
        r'weekly': 'weekly',
        r'every week': 'weekly',
        r'monthly': 'monthly',
        r'every month': 'monthly',
        r'yearly': 'yearly',
        r'every year': 'yearly',
        r'every (monday|tuesday|wednesday|thursday|friday|saturday|sunday)': lambda day: f'weekly-{day}',
        r'every (\d+) days?': lambda days: f'{days}d',
        r'every (\d+) weeks?': lambda weeks: f'{weeks}w',
        r'every (\d+) months?': lambda months: f'{months}m'
    }
    
    text = text.lower()
    for pattern, formatter in repeat_patterns.items():
        match = re.search(pattern, text)
        if match:
            if callable(formatter):
                return formatter(*match.groups())
            return formatter
    return None

def parse_bullet_points(text: str) -> Optional[str]:
    """Parse bullet points from text and format them for OmniFocus notes."""
    # First clean up the text by removing unnecessary punctuation
    # Replace multiple spaces and commas between bullet/point with a single space
    cleaned_text = re.sub(r'\s*,?\s*(?:bullet|point)\s*,?\s*', ' bullet ', text.lower())
    
    # Look for items followed by 'bullet' or 'point'
    bullet_patterns = [
        r'([^.]+?)\s+bullet(?:\s|$)',  # matches "item bullet"
        r'bullet\s+([^.]+?)(?:\s|$)'    # matches "bullet item"
    ]
    
    bullet_points = []
    
    # Process the text line by line to maintain order
    lines = cleaned_text.split('\n')
    for line in lines:
        # Check each pattern
        for pattern in bullet_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Get the item (group 1)
                item = match.group(1).strip()
                # Clean up the item
                item = re.sub(r'\s*(?:bullet|point|,)\s*$', '', item)  # Remove trailing bullet/point/comma
                item = re.sub(r'^\s*(?:bullet|point|,)\s*', '', item)  # Remove leading bullet/point/comma
                item = re.sub(r'\s+', ' ', item)  # Normalize spaces
                if item and item not in bullet_points:  # Avoid duplicates
                    bullet_points.append(item)
    
    if bullet_points:
        # Format as Markdown bullet points
        formatted_points = '• ' + '\n• '.join(bullet_points)
        logging.debug(f"Parsed bullet points: {formatted_points}")
        return formatted_points
    
    return None

def extract_task_name_and_note(text: str) -> Tuple[str, Optional[str]]:
    """Extract the task name and note content from the text.
    Handles phrases like 'with note:', 'add note:', etc."""
    note_patterns = [
        r'with note:?\s*(.*)',
        r'add note:?\s*(.*)',
        r'include note:?\s*(.*)',
        r'notes?:?\s*(.*)',
        r'list:?\s*(.*)',  # Handle "list:" format
        r'\.?\s*(?:bullet|point)\s*(.*)'  # Handle cases where bullets start after a period
    ]
    
    # Try to find a note section
    for pattern in note_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Split at the note indicator
            parts = re.split(pattern, text, maxsplit=1, flags=re.IGNORECASE)
            task_name = parts[0].strip()
            note_content = match.group(1).strip()
            
            # If the task name ends with a comma or period, clean it up
            task_name = re.sub(r'[,.]$', '', task_name)
            
            return task_name, note_content
    
    # If no note section found, return the whole text as task name
    return text.strip(), None

def create_omnifocus_url(transcript_text, **kwargs):
    """Create an OmniFocus URL from the transcript text with optional parameters"""
    # First extract task name and note content
    task_name, note_content = extract_task_name_and_note(transcript_text)
    
    # Parse dates from the task name (not the note content)
    defer_date, due_date = parse_date_time(task_name)
    
    # Start with the base parameters
    params = {
        'name': task_name,
    }
    
    # Add detected dates if found
    if defer_date:
        params['defer'] = defer_date
    if due_date:
        params['due'] = due_date
    
    # Handle notes and bullet points
    notes = []
    
    # Add any existing note from kwargs
    if kwargs.get('note'):
        notes.append(kwargs['note'])
    
    # Process bullet points in the note content if it exists
    if note_content:
        bullet_points = parse_bullet_points(note_content)
        if bullet_points:
            notes.append(bullet_points)
        elif note_content:  # If there are no bullet points but there is note content
            notes.append(note_content)
    
    # If we have any notes, combine them
    if notes:
        params['note'] = '\n\n'.join(notes)
    
    # Add other parameters (project, folder, etc.)
    project = detect_project(task_name)
    if project:
        params['project'] = project
        
    folder = detect_folder(task_name)
    if folder:
        params['folder'] = folder
        
    if detect_parallel(task_name):
        params['parallel'] = 'true'
        
    # Only set flag if explicitly mentioned (overrides default)
    flag_detected = detect_flag(task_name)
    if flag_detected or kwargs.get('flag'):
        params['flag'] = 'true'
        
    estimate = parse_duration(task_name)
    if estimate:
        params['estimate'] = estimate
    
    # Add task status and preferences
    status = detect_task_status(task_name)
    if status['completed']:
        params['completed'] = 'true'
    if not status['reveal']:
        params['reveal'] = 'false'
    if status['sequential']:
        params['sequential'] = 'true'
    
    # Add dependencies
    dependencies = detect_dependencies(task_name)
    if dependencies:
        params['dependencies'] = ','.join(dependencies)
    
    # Add location context
    location = detect_location(task_name)
    if location:
        params['context'] = location
    
    # Add energy level
    energy = detect_energy_level(task_name)
    if energy:
        params['energy'] = energy
    
    # Add repeat pattern
    repeat = parse_repeat_pattern(task_name)
    if repeat:
        params['repeat'] = repeat
    
    # Add other optional parameters if provided
    if kwargs.get('project'):  # Override detected project if explicitly provided
        params['project'] = kwargs['project']
    if kwargs.get('context'):  # Override detected context if explicitly provided
        params['context'] = kwargs['context']
    if kwargs.get('estimate'):  # Override detected estimate if explicitly provided
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
    url = f"omnifocus:///add?{'&'.join(encoded_params)}"
    logging.debug(f"Generated OmniFocus URL: {url}")
    return url

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
        
        logging.info(f"Processing transcript: {transcript}")
        
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
        
        # Detect folder first and log the result
        folder = detect_folder(transcript)
        if folder:
            logging.info(f"Detected folder: {folder}")
        else:
            logging.info("No folder detected in transcript")
        
        # Detect relevant tags
        detected_tags = detect_tags(transcript)
        
        # Join multiple tags with commas for OmniFocus
        context = ', '.join(detected_tags) if detected_tags else None
        
        # Create OmniFocus URL with default parameters and detected tags
        omnifocus_url = create_omnifocus_url(
            transcript,
            flag=True,  # Flag all voice tasks by default
            note="Created via Voice Transcription",  # Add a note about the source
            context=context,  # Add detected tags
            folder=folder  # Add detected folder
        )
        
        # Log the generated URL for debugging
        logging.debug(f"Generated OmniFocus URL: {omnifocus_url}")
        
        # Save URL to file
        with open(url_file, 'w') as f:
            f.write(omnifocus_url)
        
        if detected_tags:
            logging.info(f"Created OmniFocus URL with tags: {', '.join(detected_tags)}")
        else:
            logging.info("Created OmniFocus URL without tags")
            
        if folder:
            logging.info(f"Task will be created in folder: {folder}")
        else:
            logging.info("No folder specified for task")

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

def is_grocery_list(text: str) -> bool:
    """Check if the text contains multiple grocery items."""
    # Flatten the grocery items list
    all_groceries = set(item.lower() for sublist in GROCERY_ITEMS.values() for item in sublist)
    
    # Count how many grocery items are mentioned in the text
    words = set(word.lower().strip('.,!?') for word in text.split())
    grocery_count = sum(1 for word in words if word in all_groceries)
    
    # Consider it a grocery list if it contains at least 2 grocery items
    return grocery_count >= 2

def parse_task_attributes(text):
    """Parse task attributes from text using common patterns."""
    attributes = {
        'name': text,
        'project': None,
        'due': None,
        'defer': None,
        'flag': None,
        'tags': None,
        'note': None
    }
    
    # Extract project using #project or @project
    project_match = re.search(r'[#@]project[= ]([^\s]+)', text)
    if project_match:
        attributes['project'] = project_match.group(1)
        attributes['name'] = re.sub(r'[#@]project[= ][^\s]+', '', attributes['name'])

    # Extract due date using #due or @due
    due_match = re.search(r'[#@]due[= ]([^\s]+(?:\s+[^\s]+)*)', text)
    if due_match:
        attributes['due'] = due_match.group(1)
        attributes['name'] = re.sub(r'[#@]due[= ][^\s]+(?:\s+[^\s]+)*', '', attributes['name'])

    # Extract defer date using #defer or @defer
    defer_match = re.search(r'[#@]defer[= ]([^\s]+(?:\s+[^\s]+)*)', text)
    if defer_match:
        attributes['defer'] = defer_match.group(1)
        attributes['name'] = re.sub(r'[#@]defer[= ][^\s]+(?:\s+[^\s]+)*', '', attributes['name'])

    # Extract flag using #flag or @flag
    if re.search(r'[#@]flag', text):
        attributes['flag'] = 'true'
        attributes['name'] = re.sub(r'[#@]flag', '', attributes['name'])

    # Extract tags using #tag or @tag
    tags_matches = re.finditer(r'[#@]tag[= ]([^\s]+)', text)
    tags = [m.group(1) for m in tags_matches]
    if tags:
        attributes['tags'] = ','.join(tags)
        for tag in tags:
            attributes['name'] = re.sub(r'[#@]tag[= ]' + tag, '', attributes['name'])

    # Extract note using #note or @note
    note_match = re.search(r'[#@]note[= ](.+?)(?=[#@]|$)', text)
    if note_match:
        attributes['note'] = note_match.group(1).strip()
        attributes['name'] = re.sub(r'[#@]note[= ].+?(?=[#@]|$)', '', attributes['name'])

    # Clean up the name
    attributes['name'] = attributes['name'].strip()

    # Check if this is a grocery list and add the Sainsbury tag
    if is_grocery_list(text):
        if attributes['tags']:
            attributes['tags'] += ',Location : Sainsbury'
        else:
            attributes['tags'] = 'Location : Sainsbury'
    
    return attributes

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