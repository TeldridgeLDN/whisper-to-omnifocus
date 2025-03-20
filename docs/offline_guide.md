# Offline Voice Recording Guide

This guide provides step-by-step instructions for recording voice tasks when you're not connected to your home network.

## Prerequisites

1. Ensure you have the "Offline Voice to Task" shortcut installed
2. Check available storage space on your device
3. Make sure you're familiar with the voice command format

## Recording Steps

### When Away from Home Network

1. **Start Recording**
   - Open the Shortcuts app
   - Tap the "Offline Voice to Task" shortcut
   - Or use Siri: "Hey Siri, Offline Voice to Task"

2. **Record Your Task**
   - Wait for the recording interface to appear
   - Speak your task clearly, using the standard format:
     ```
     "Task description hashtag project ProjectName hashtag due tomorrow"
     ```
   - Tap "Done" when finished

3. **Confirm Recording**
   - You'll see a notification: "Recording Saved"
   - The message will confirm: "Recording saved locally. Will process when you return home."
   - The recording is now safely stored on your device

### When Returning Home

1. **Connect to Home Network**
   - Ensure your device is connected to your home WiFi
   - Wait for a stable connection

2. **Automatic Processing**
   - The sync process will automatically:
     * Detect your new recordings
     * Process them using Whisper
     * Create tasks in OmniFocus
     * Clean up processed files

3. **Verify Processing**
   - Check OmniFocus for your new tasks
   - Review the sync logs if needed:
     ```
     ~/whisper-logs/sync_YYYYMMDD.log
     ```

### Manual Sync (If Needed)

If automatic sync doesn't run:

1. **Open Terminal**
   - Navigate to the project directory:
     ```bash
     cd ~/whisper-to-omnifocus
     ```

2. **Run Sync Script**
   ```bash
   ./scripts/sync_recordings.py
   ```

3. **Check Results**
   - Review the sync logs
   - Verify tasks in OmniFocus

## Troubleshooting

### Common Issues

1. **Recording Not Saving**
   - Check device storage space
   - Verify shortcut permissions
   - Try recording again

2. **Sync Not Working**
   - Confirm home network connection
   - Check sync logs for errors
   - Try manual sync

3. **Tasks Not Appearing**
   - Verify OmniFocus is running
   - Check sync logs
   - Ensure proper command format

### Solutions

1. **Storage Issues**
   - Clear unnecessary files
   - Move recordings to cloud storage
   - Use manual sync

2. **Network Problems**
   - Check WiFi connection
   - Try manual sync
   - Review network settings

3. **Processing Errors**
   - Check sync logs
   - Verify Whisper installation
   - Try reprocessing recordings

## Best Practices

1. **Before Recording**
   - Check available storage
   - Ensure quiet environment
   - Plan your task description

2. **During Recording**
   - Speak clearly and at moderate pace
   - Use consistent command format
   - Keep recordings brief

3. **After Recording**
   - Verify notification received
   - Note number of recordings
   - Check sync when home

4. **Regular Maintenance**
   - Monitor storage usage
   - Clean up old recordings
   - Update shortcuts as needed

## Example Commands

### Basic Task
```
"Buy groceries"
```

### Task with Project
```
"Review code hashtag project Development"
```

### Task with Due Date
```
"Call client hashtag due tomorrow 2pm"
```

### Complex Task
```
"Prepare presentation hashtag project Work hashtag due friday hashtag tag important hashtag note Include budget section"
```

## Tips for Success

1. **Storage Management**
   - Keep track of pending recordings
   - Clear processed recordings
   - Monitor device storage

2. **Network Handling**
   - Wait for stable connection
   - Use manual sync if needed
   - Keep sync logs for reference

3. **Command Format**
   - Use consistent hashtag format
   - Keep descriptions clear
   - Include all necessary attributes

4. **Verification**
   - Check notifications
   - Review sync logs
   - Verify in OmniFocus 