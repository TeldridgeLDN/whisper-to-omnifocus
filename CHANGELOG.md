# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Offline voice recording support with local storage
- New "Offline Voice to Task" shortcut for recording without network connection
- Automatic sync mechanism for processing offline recordings
- Launch agent for continuous monitoring of new recordings
- Detailed offline recording guide with step-by-step instructions
- Support for multiple simultaneous recordings with timestamped filenames
- Date and time parsing for task due dates
- Automatic ffmpeg installation on remote server
- Added FileLock class back to prevent duplicate processing
- Added duplicate detection for transcripts within a one-minute window
- Added proper cleanup of temporary files after processing
- Added better error handling for file operations
- Added file existence verification at each step of processing
- Added detailed error logging for file operations
- Added environment variable configuration with template
- Added documentation for environment setup

### Fixed
- Fixed path resolution for process_recording.py script
- Added missing whisper package dependency
- Improved error handling and logging in processing scripts
- Fixed file cleanup after successful processing
- Fixed SSH key authentication issues
- Fixed ffmpeg dependency issues on remote server
- Fixed issue with duplicate task creation in OmniFocus
- Fixed error handling for file operations
- Fixed error when removing already cleaned up temporary files
- Fixed "Bad file descriptor" error by moving cleanup after FileLock release
- Fixed redundant file cleanup attempt causing "No such file" error
- Fixed error handling for transcription and file transfer failures
- Removed hardcoded personal details in favor of environment variables

### Changed
- Updated documentation to include offline workflow
- Enhanced logging for better debugging
- Improved error messages and handling
- Switched to direct SSH file transfer instead of iCloud sync
- Improved file naming with timestamps to prevent conflicts
- Enhanced error handling for SSH operations
- Improved logging for file operations and processing steps
- Enhanced error messages for better debugging
- Updated file handling logic to be more robust
- Improved error recovery to preserve audio files for retry
- Moved configuration to environment variables
- Updated documentation with environment setup instructions

## [0.1.0] - 2024-03-21

### Added
- Initial project setup
- Main Python script for processing voice recordings (`process_recording.py`)
- Installation script (`install.sh`) for easy setup
- Setup script (`setup.py`) for environment configuration
- Comprehensive documentation in `docs/` directory
- Example voice commands in `examples/` directory
- Shortcuts setup guide
- MIT License
- Basic project structure and organization
- Environment file configuration
- Automatic directory creation
- Python dependency management
- OmniFocus integration via URL scheme 