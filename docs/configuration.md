# Configuration Guide

## Directory Setup

The script uses the following directory structure by default:

```
$HOME/
└── Library/
    └── Mobile Documents/
        └── com~apple~CloudDocs/
            └── whisper/
                ├── temp/
                │   ├── audio_recording.m4a
                │   ├── whisper_transcript.txt
                │   └── whisper_transcript.txt_url
                └── logs/
                    └── automator.log
```

## Environment Variables

You can customize the paths by setting these environment variables in your `.zshrc` or `.bash_profile`:

```bash
export WHISPER_HOME="$HOME/whisper"  # Base directory for Whisper installation
export WHISPER_ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/whisper"  # iCloud directory
export WHISPER_TEMP_DIR="$WHISPER_ICLOUD_DIR/temp"  # Temporary files directory
export WHISPER_LOG_DIR="$WHISPER_ICLOUD_DIR/logs"  # Log files directory
```

## Installation Steps

1. **Install Python Dependencies**
   ```bash
   python3 -m pip install openai-whisper
   ```

2. **Configure Environment**
   - Copy the environment variables to your shell configuration file
   - Reload your shell or run `source ~/.zshrc` (or `~/.bash_profile`)

3. **Set Up Directories**
   ```bash
   mkdir -p "$WHISPER_HOME"
   mkdir -p "$WHISPER_TEMP_DIR"
   mkdir -p "$WHISPER_LOG_DIR"
   ```

4. **Install Whisper Model**
   The script will automatically download the base model on first run.

## Shortcut Configuration

The macOS Shortcut should be configured with these actions:

1. Record Audio
   - Save to: `$WHISPER_TEMP_DIR/audio_recording.m4a`

2. Run Shell Script
   - Shell: `/bin/zsh`
   - Input: as arguments
   - Script: `$WHISPER_HOME/whisper_to_omnifocus.sh "$WHISPER_TEMP_DIR/audio_recording.m4a" "$WHISPER_TEMP_DIR/whisper_transcript.txt"`

## Automator Configuration

The Automator folder action should be configured to:

1. Watch the temp directory for new files
2. Filter for .m4a files
3. Run the whisper script
4. Display a notification when complete

## Whisper Model Configuration

By default, the script uses Whisper's "base" model. You can modify this in the script:

```python
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

Choose based on your performance needs:
- tiny: Fastest, least accurate
- base: Good balance of speed and accuracy
- large: Most accurate, but slower and more resource-intensive

## OmniFocus URL Scheme

The script generates OmniFocus URLs with these parameters:

- name: Task name (required)
- project: Project name (optional)
- due: Due date (optional)
- defer: Defer date (optional)
- flag: true/false (optional)
- tags: Comma-separated tags (optional)
- note: Task note (optional)

Example URL:
```
omnifocus:///add?name=Buy%20groceries&project=Errands&due=tomorrow&tags=shopping&note=Get%20milk
```

## Troubleshooting

### Common Issues

1. **Audio File Not Found**
   - Check the permissions of the temp directory
   - Verify the audio file path in the shortcut

2. **Transcription Failed**
   - Ensure Whisper is properly installed
   - Check Python environment activation
   - Verify audio file format (should be m4a)

3. **OmniFocus Not Opening**
   - Verify OmniFocus is installed
   - Check URL scheme formatting
   - Ensure proper URL encoding

### Logs

Check these log files for troubleshooting:
- `$WHISPER_LOG_DIR/automator.log`: Automator processing logs
- `$WHISPER_TEMP_DIR/whisper_transcript.txt_debug`: Debugging output

## Updates and Maintenance

1. **Updating Whisper**
   ```bash
   python3 -m pip install --upgrade openai-whisper
   ```

2. **Clearing Temporary Files**
   ```bash
   rm -f "$WHISPER_TEMP_DIR"/*
   ```

3. **Rotating Logs**
   ```bash
   mv "$WHISPER_LOG_DIR/automator.log" "$WHISPER_LOG_DIR/automator.log.old"
   touch "$WHISPER_LOG_DIR/automator.log"
   ``` 