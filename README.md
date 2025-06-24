# AI Rails TDD

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![n8n compatible](https://img.shields.io/badge/n8n-compatible-orange.svg)](https://n8n.io)

A bounded, human-controlled AI agent orchestration system that implements Test-Driven Development (TDD) with anti-mesa-optimization measures.

## 🚀 Features

- **🧪 TDD-First Architecture**: Tests are generated before implementation
- **👤 Human-in-the-Loop**: All critical outputs require human approval
- **🛡️ Anti-Mesa-Optimization**: Prevents AI from gaming the tests
- **📦 Portable System**: Works with any Python/JavaScript project
- **✅ Real Test Execution**: Uses pytest to actually validate code
- **🗂️ Standardized Structure**: Consistent file organization across projects

## 📖 Documentation

- [**Getting Started**](docs/getting-started.md) - Installation, quick start, and configuration

- **User Guide**
  - [Basic Usage](docs/user-guide/basic-usage.md)
  - [Workflows](docs/user-guide/workflows.md)
  - [Prompt Management](docs/user-guide/prompt-management.md)
  - [Troubleshooting](docs/user-guide/troubleshooting.md)

- **Developer Guide**
  - [Architecture](docs/developer/architecture.md)
  - [API Reference](docs/developer/api-reference.md)
  - [Testing](docs/developer/testing.md)

## 🎯 Quick Start

```bash
# Clone the repository
git clone https://github.com/Auldsyababua/ai-rails-tdd.git
cd ai-rails-tdd

# Install the CLI
sudo ./install.sh

# Initialize in your project
cd /your/project
ai-rails init

# Start services
ai-rails-start

# Open n8n and import a workflow!
```

See the [Getting Started Guide](docs/getting-started.md) for detailed instructions.

## 🏗️ How It Works

```
Planning Doc → Generate Tests → Human Approval → Generate Code → Run Tests
     ↓              ↓                 ↓                ↓             ↓
  You write    AI creates      You review       AI writes    Tests validate
```

1. **Define** your feature or app using our planning template
2. **Generate** comprehensive tests with AI assistance
3. **Review** and approve the tests
4. **Implement** code that passes all tests
5. **Validate** with real test execution

## 🤝 Contributing

We love contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

- 📋 [Report bugs](https://github.com/Auldsyababua/ai-rails-tdd/issues)
- 💡 [Request features](https://github.com/Auldsyababua/ai-rails-tdd/issues)
- 🔧 [Submit pull requests](https://github.com/Auldsyababua/ai-rails-tdd/pulls)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

Please see our [Security Policy](SECURITY.md) for reporting vulnerabilities.

## 🗺️ Roadmap

Check out our [Roadmap](docs/misc/roadmap.md) for upcoming features and improvements.

## 💬 Community

- [GitHub Discussions](https://github.com/Auldsyababua/ai-rails-tdd/discussions)
- [Issue Tracker](https://github.com/Auldsyababua/ai-rails-tdd/issues)

## 🙏 Acknowledgments

- Built with [n8n](https://n8n.io) workflow automation
- Powered by [Ollama](https://ollama.ai) and [OpenAI](https://openai.com)
- Inspired by the TDD methodology and AI safety principles

---

Made with ❤️ by the AI Rails community