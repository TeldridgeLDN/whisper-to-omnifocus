# Shortcuts Setup Guide

This guide explains how to set up the necessary shortcuts for the Whisper to OmniFocus integration.

## Quick Voice to Task Shortcut

### Setup Instructions

1. Open the Shortcuts app on your device
2. Create a new shortcut named "Quick Voice to Task"
3. Add the following actions in sequence:

```
1. Record Audio
   - Show Recording Interface: On
   - Save to Variable: "Recording"

2. Save File
   - File: Recording (from previous step)
   - Destination: whisper-temp folder
   - Name: "recording_{random number between 1000-9999}.m4a"

3. Show Notification
   - Title: "Processing Voice Recording"
   - Message: "Your task is being created..."
```

### Usage

1. Trigger the shortcut (via widget, Siri, etc.)
2. Record your task with the command format:
   - Basic: "Task description"
   - With attributes: "Task description hashtag project Work hashtag due tomorrow"
3. Wait for the notification confirming processing

## Offline Voice Recording Shortcut

### Setup Instructions

1. Open the Shortcuts app
2. Create a new shortcut named "Offline Voice to Task"
3. Add these actions:

```
1. Record Audio
   - Show Recording Interface: On
   - Save to Variable: "Recording"

2. Save File
   - File: Recording (from previous step)
   - Destination: whisper-local folder
   - Name: "recording_{random number between 1000-9999}.m4a"

3. Show Notification
   - Title: "Recording Saved"
   - Message: "Recording saved locally. Will process when you return home."
```

### Usage

1. Use this shortcut when you're not on your home network
2. Record your task as usual
3. The recording will be saved locally on your device
4. When you return home and connect to your network:
   - The sync process will automatically run
   - Your recordings will be processed
   - Tasks will be created in OmniFocus

## Voice Memo to Task Shortcut

### Setup Instructions

1. Open the Shortcuts app
2. Create a new shortcut named "Voice Memo to Task"
3. Add these actions:

```
1. Accept Voice Memo Input
   - Input: Voice Memo

2. Copy File
   - Source: Shortcut Input
   - Destination: whisper-temp folder
   - Name: "recording_{random number between 1000-9999}.m4a"

3. Show Notification
   - Title: "Processing Voice Memo"
   - Message: "Converting memo to task..."
```

### Usage

1. Record a voice memo in the Voice Memos app
2. Share the memo
3. Select the "Voice Memo to Task" shortcut
4. Wait for processing notification

## Installation Tips

### iOS/iPadOS

1. Enable "Allow Untrusted Shortcuts" in Settings:
   - Settings → Shortcuts → Advanced
   - Toggle "Allow Untrusted Shortcuts"

2. Add shortcuts to Home Screen:
   - Open shortcut details
   - Tap Share
   - Select "Add to Home Screen"

3. Configure Siri Trigger:
   - In shortcut details
   - Tap the ⓘ button
   - Select "Add to Siri"
   - Record your trigger phrase

### macOS

1. Enable Shortcuts in System Settings:
   - System Settings → Privacy & Security
   - Allow Shortcuts Automation

2. Add to Menu Bar:
   - Open Shortcuts preferences
   - Enable "Show in Menu Bar"

3. Set Keyboard Shortcuts:
   - System Settings → Keyboard → Shortcuts
   - Add shortcut for quick access

## Offline Workflow

### When Away from Home Network

1. Use the "Offline Voice to Task" shortcut
2. Record your task as normal
3. The recording will be saved locally
4. You'll receive a confirmation notification

### When Returning Home

1. Connect to your home network
2. The sync process will automatically:
   - Detect new recordings
   - Process them using Whisper
   - Create tasks in OmniFocus
   - Clean up processed files

### Manual Sync

If automatic sync doesn't run, you can manually trigger it:
1. Open Terminal
2. Navigate to the project directory
3. Run: `./scripts/sync_recordings.py`

## Troubleshooting

### Common Issues

1. **Recording Not Saving**
   - Check whisper-temp folder permissions
   - Verify folder path in shortcut
   - Ensure sufficient storage space

2. **Shortcut Not Running**
   - Check Shortcuts app permissions
   - Verify microphone access
   - Restart Shortcuts app

3. **Task Not Creating**
   - Check OmniFocus installation
   - Verify URL scheme handling
   - Check process_recording.py logs

4. **Offline Sync Issues**
   - Verify local storage permissions
   - Check network connectivity
   - Review sync logs

### Solutions

1. **Permission Issues**
   - Open System Settings
   - Navigate to Privacy & Security
   - Enable necessary permissions:
     * Microphone
     * Files and Folders
     * Automation

2. **Path Problems**
   - Verify whisper-temp location
   - Check folder permissions
   - Run setup.py to recreate folders

3. **Integration Errors**
   - Check .env file configuration
   - Verify OmniFocus installation
   - Review log files in whisper-logs

4. **Sync Problems**
   - Check local storage space
   - Verify network connection
   - Review sync logs
   - Try manual sync

## Best Practices

1. **Recording Quality**
   - Speak clearly and at moderate pace
   - Use consistent command format
   - Avoid background noise

2. **Task Management**
   - Use standard project names
   - Keep task descriptions concise
   - Use consistent tag naming

3. **Maintenance**
   - Regularly check logs
   - Update shortcuts as needed
   - Clean temp folders periodically
   - Monitor local storage space

4. **Offline Usage**
   - Check available storage before recording
   - Use consistent naming for offline recordings
   - Verify sync after returning home
   - Keep track of pending recordings

## Advanced Configuration

### Custom Shortcuts

1. **Batch Processing**
   ```
   1. Find Files in whisper-temp
   2. Repeat with Each
   3. Run process_recording.py
   4. Delete Original File
   ```

2. **Status Monitor**
   ```
   1. Get Contents of whisper-logs
   2. Filter Recent Entries
   3. Show Notification
   ```

### Integration Options

1. **Watch Folder Setup**
   - Configure folder action
   - Set up automatic processing
   - Monitor for new recordings

2. **Custom URL Schemes**
   - Define custom parameters
   - Add special handling
   - Create workflow triggers

3. **Offline Storage**
   - Configure local storage location
   - Set up sync triggers
   - Monitor storage usage 