# 🎙️ Whisper to OmniFocus

Transform voice commands into structured OmniFocus tasks using OpenAI's Whisper speech recognition. This integration brings powerful voice automation to your task management workflow.

## ✨ Features

- 🗣️ **Natural Speech Recognition** - Powered by OpenAI's Whisper AI
- 📋 **Rich Task Creation** - Projects, tags, due dates, defer dates, and notes
- 🔄 **Seamless Integration** - Works with OmniFocus on macOS and iOS via iCloud
- 🎯 **Smart Parsing** - Understands natural language commands and dates
- 🚀 **Quick Capture** - Record tasks on the go with Shortcuts integration
- 🔔 **Instant Feedback** - Real-time notifications when tasks are created

## 🚀 Quick Start

1. Clone this repository:
```bash
git clone https://github.com/TeldridgeLDN/whisper-to-omnifocus.git
cd whisper-to-omnifocus
```

2. Run the setup script:
```bash
./scripts/setup.sh
```

3. Import the shortcut and configure paths (see [configuration guide](docs/configuration.md))

## 💡 Example Commands

Simple task:
```
"Buy groceries"
```

Task with project and due date:
```
"Buy groceries hashtag project Errands hashtag due tomorrow"
```

Complex task:
```
"Schedule team meeting hashtag project Work hashtag due monday 2pm hashtag tag meetings,important hashtag note Prepare quarterly slides"
```

## 🛠️ Technologies

- OpenAI Whisper (Speech Recognition)
- OmniFocus URL Schemes
- macOS Shortcuts & Automator
- Python with Natural Language Processing
- iCloud Integration

## 📋 Requirements

- macOS (Primary platform)
- Python 3.7+
- OmniFocus Pro
- iCloud enabled for OmniFocus

## 📱 Platform Support

- macOS (Primary)
- iOS (via iCloud sync)
- Requires OmniFocus Pro

## 📚 Documentation

- [Configuration Guide](docs/configuration.md)
- [Example Commands](examples/example_commands.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the amazing speech recognition
- [The Omni Group](https://www.omnigroup.com/) for OmniFocus and their URL scheme documentation
- All contributors and users of this project

## 🔗 Links

- [Project Homepage](https://github.com/TeldridgeLDN/whisper-to-omnifocus)
- [Issue Tracker](https://github.com/TeldridgeLDN/whisper-to-omnifocus/issues)
- [OmniFocus URL Scheme Documentation](https://inside.omnifocus.com/url-schemes) 