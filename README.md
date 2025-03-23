# 🎙️ Whisper to OmniFocus

A powerful integration that converts voice commands into OmniFocus tasks using OpenAI's Whisper speech recognition.

## ✨ Features

- 🎙️ **Voice to Task**: Record voice commands and instantly create OmniFocus tasks
- 🔄 **Offline Support**: Record tasks without network connection
- ⚡ **Automatic Sync**: Process offline recordings when back online
- 🎯 **Smart Parsing**: Automatically extracts task details from voice commands
- 📅 **Date/Time Understanding**: Intelligently parses natural language dates and times
- 🏷️ **Automatic Tagging**: Detects and applies relevant tags based on context
- 🔍 **Flexible Commands**: Support for projects, due dates, defer dates, flags, and tags
- 📝 **Structured Notes**: Create formatted bullet point lists in task notes
- 🔄 **Smart Formatting**: Automatic bullet point formatting and cleanup
- 📱 **iOS Integration**: Works seamlessly with iOS Shortcuts
- 🔄 **Background Processing**: Automatic task creation in OmniFocus
- 🛡️ **Robust Processing**: Duplicate detection and error recovery built-in

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   ./install.sh
   ```

2. **Configure Environment**:
   - Copy `.env.template` to `~/.whisper-to-omnifocus.env`
   - Update the environment variables with your settings:
     ```bash
     cp .env.template ~/.whisper-to-omnifocus.env
     nano ~/.whisper-to-omnifocus.env
     ```

3. **Set Up Shortcuts**:
   - Install the "Voice to Task" shortcut for online use
   - Install the "Offline Voice to Task" shortcut for offline recording
   - Follow the setup guide in `docs/shortcuts.md`

4. **Configure Automator**:
   - Set up the folder action to watch the temp directory
   - Follow the setup guide in `docs/configuration.md`

5. **Start Processing**:
   ```bash
   ./scripts/process_icloud_recording.py
   ```

## 💡 Example Commands

### Basic Task
```
Create a task to buy groceries tomorrow
```

### Time-Specific Task
```
Remind me to call John at 3pm
```

### Date and Time Task
```
Schedule team meeting for next Friday at 2:30pm
```

### Tagged Task
```
Write documentation for the project with coding and admin tags
```

### Task with Bullet Points
```
Create a task Review Project with note: check progress bullet update timeline bullet schedule meeting bullet
```

### Shopping List
```
Groceries list: apples bullet bananas bullet milk bullet bread bullet
```

### Complex Task with Notes
```
Plan weekly review in the Work folder with note: review calendar bullet check emails bullet plan next week bullet update status bullet
```

## 🛠️ Technologies

- Python 3.10+
- OpenAI Whisper
- macOS Shortcuts
- Automator
- OmniFocus URL Scheme
- python-dateutil

## 📋 Requirements

- macOS 13.0 or later
- iOS 16.0 or later (for Shortcuts)
- Python 3.10 or later
- OmniFocus 3
- iCloud Drive enabled
- python-dateutil library
- ffmpeg (installed automatically)

## 📱 Platform Support

- macOS (primary)
- iOS (via Shortcuts)

## 📚 Documentation

- [Configuration Guide](docs/configuration.md)
- [Shortcuts Setup](docs/shortcuts.md)
- [Example Commands](docs/example_commands.md)
- [Offline Guide](docs/offline_guide.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Changelog](CHANGELOG.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Check our [CHANGELOG.md](CHANGELOG.md) for recent changes and improvements.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the Whisper model
- OmniGroup for OmniFocus
- Apple for Shortcuts and Automator
- python-dateutil contributors

## 🔗 Links

- [OpenAI Whisper](https://github.com/openai/whisper)
- [OmniFocus URL Scheme](https://inside.omnifocus.com/url-schemes)
- [macOS Shortcuts](https://support.apple.com/guide/shortcuts-mac/welcome/mac)
- [Automator Guide](https://support.apple.com/guide/automator/welcome/mac) 