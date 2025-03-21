# Troubleshooting Guide

This guide helps you resolve common issues that may arise when using Whisper to OmniFocus.

## Common Issues

### Task Not Appearing in OmniFocus

1. **Check the Logs**
   - Look in `~/whisper-logs/` for the latest log file
   - Check for any error messages during processing

2. **Network Connectivity**
   - Verify you're on your home network for online processing
   - For offline recordings, ensure they're saved to the correct iCloud folder

3. **File Processing**
   - Confirm the audio file was created successfully
   - Check that the file is not still being written to
   - Verify the file permissions are correct

### Duplicate Tasks

The system has built-in duplicate detection that prevents the same task from being created multiple times within a one-minute window. If you're still seeing duplicates:

1. Check if multiple shortcuts are running simultaneously
2. Verify that the processing script isn't running multiple instances
3. Check the lock file in the temp directory

### SSH Connection Issues

1. **Key Authentication**
   - Verify the SSH key exists and has correct permissions (600)
   - Check the key is properly added to authorized_keys on the remote server
   - Test SSH connection manually using the same key

2. **Server Connectivity**
   - Confirm you're on the same network as the server
   - Verify the server IP address is correct
   - Check if the SSH port is accessible

### Transcription Issues

1. **Audio File Problems**
   - Ensure the audio file is not corrupted
   - Check that ffmpeg is installed and working
   - Verify the audio format is supported (m4a recommended)

2. **Processing Errors**
   - Check Python environment is activated
   - Verify Whisper model is downloaded
   - Check for sufficient disk space

### Date and Time Parsing

The system understands various date and time formats:
- "tomorrow at 3pm"
- "next Friday at 2:30"
- "this afternoon"
- "in 2 hours"

If dates aren't being recognized:
1. Check the format you're using
2. Verify python-dateutil is installed
3. Look for parsing errors in the logs

## Error Recovery

The system includes several error recovery mechanisms:

1. **File Preservation**
   - Failed recordings are moved back to iCloud for retry
   - Temporary files are cleaned up automatically
   - Lock files prevent concurrent processing

2. **Processing Recovery**
   - Failed transcriptions are logged and can be retried
   - Network disconnections are handled gracefully
   - Incomplete files are detected and skipped

## Getting Help

If you encounter an issue not covered here:

1. Check the latest logs in `~/whisper-logs/`
2. Review the [CHANGELOG.md](../CHANGELOG.md) for recent fixes
3. Open an issue on GitHub with:
   - Description of the problem
   - Relevant log entries
   - Steps to reproduce
   - System information 