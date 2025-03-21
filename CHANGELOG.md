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

### Fixed
- Fixed path resolution for process_recording.py script
- Added missing whisper package dependency
- Improved error handling and logging in processing scripts
- Fixed file cleanup after successful processing
- Fixed SSH key authentication issues
- Fixed ffmpeg dependency issues on remote server

### Changed
- Updated documentation to include offline workflow
- Enhanced logging for better debugging
- Improved error messages and handling
- Switched to direct SSH file transfer instead of iCloud sync
- Improved file naming with timestamps to prevent conflicts
- Enhanced error handling for SSH operations

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