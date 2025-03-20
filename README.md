# 🎙️ Whisper to OmniFocus

A powerful integration that converts voice commands into OmniFocus tasks using OpenAI's Whisper speech recognition.

## ✨ Features

- 🎙️ **Voice to Task**: Record voice commands and instantly create OmniFocus tasks
- 🔄 **Offline Support**: Record tasks without network connection
- ⚡ **Automatic Sync**: Process offline recordings when back online
- 🎯 **Smart Parsing**: Automatically extracts task details from voice commands
- 🔍 **Flexible Commands**: Support for projects, due dates, defer dates, flags, and tags
- 📱 **iOS Integration**: Works seamlessly with iOS Shortcuts
- 🔄 **Background Processing**: Automatic task creation in OmniFocus

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   ./install.sh
   ```

2. **Set Up Shortcuts**:
   - Install the "Voice to Task" shortcut for online use
   - Install the "Offline Voice to Task" shortcut for offline recording
   - Follow the setup guide in `docs/shortcuts.md`

3. **Configure Automator**:
   - Set up the folder action to watch the temp directory
   - Follow the setup guide in `docs/configuration.md`

4. **Start Processing**:
   ```bash
   ./scripts/process_icloud_recording.py
   ```

## 💡 Example Commands

### Basic Task
```
Create a task to buy groceries tomorrow
```

### Complex Task
```
Create a task to finish the project report due next Friday at 5pm in the Work project with high priority and tags for documentation and urgent
```

## 🛠️ Technologies

- Python 3.10+
- OpenAI Whisper
- macOS Shortcuts
- Automator
- OmniFocus URL Scheme

## 📋 Requirements

- macOS 13.0 or later
- iOS 16.0 or later (for Shortcuts)
- Python 3.10 or later
- OmniFocus 3
- iCloud Drive enabled

## 📱 Platform Support

- macOS (primary)
- iOS (via Shortcuts)

## 📚 Documentation

- [Configuration Guide](docs/configuration.md)
- [Shortcuts Setup](docs/shortcuts.md)
- [Example Commands](docs/example_commands.md)
- [Offline Guide](docs/offline_guide.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the Whisper model
- OmniGroup for OmniFocus
- Apple for Shortcuts and Automator

## 🔗 Links

- [OpenAI Whisper](https://github.com/openai/whisper)
- [OmniFocus URL Scheme](https://inside.omnifocus.com/url-schemes)
- [macOS Shortcuts](https://support.apple.com/guide/shortcuts-mac/welcome/mac)
- [Automator Guide](https://support.apple.com/guide/automator/welcome/mac) 