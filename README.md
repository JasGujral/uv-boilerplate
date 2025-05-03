# 🚀 uv-boilerplate

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![UV](https://img.shields.io/badge/uv-0.1.0-orange.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/ruff-0.1.0-red.svg)](https://github.com/astral-sh/ruff)
[![docformatter](https://img.shields.io/badge/docformatter-1.7.5-purple.svg)](https://github.com/PyCQA/docformatter)
[![mypy](https://img.shields.io/badge/mypy-1.5.0-blue.svg)](http://mypy-lang.org/)
[![pytest](https://img.shields.io/badge/pytest-7.4.0-green.svg)](https://docs.pytest.org/)

> 🚀 The Python Project Boilerplate that will supercharge your development! Built with UV for blazing fast dependency management, static type checking, code formatting, logging and complete CI/CD workflows out of the box.

## 🌟 Why Choose This Boilerplate?

- ⚡ **Modern Package Management**: Powered by [UV](https://github.com/astral-sh/uv) for significantly faster dependency handling
- 🛠️ **Production-Ready**: Built with industry best practices and a focus on maintainability
- 🔄 **Automated Workflows**: Pre-configured GitHub Actions for testing, code quality, and security
- 📦 **Modern Stack**: Built on Python 3.12 with carefully selected development tools
- 🛡️ **Quality First**: Integrated testing, type checking, and code analysis
- 🚀 **Quick Setup**: Get started with a well-structured Python project in minutes
- 🔍 **Static Type Testing**: Comprehensive type checking with mypy for better code reliability and maintenance.
- ✨ **Code Formatting**: Automated code formatting with ruff and docformatter for consistent style

## 🚀 Quick Start

1. **Clone and Setup**

```bash
# Clone the repository
git clone https://github.com/JasGujral/uv-boilerplate
cd uv-boilerplate

# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup Python and virtual environment
uv python install 3.12
uv venv --python=3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies**

```bash
uv sync
```

3. **Start Coding!** 🎉

## 📦 Project Structure

```
uv-boilerplate/
├── .github/                               # 🔄 GitHub Actions workflows
├── src/                                     # 📦 Your source code
│   └── your_project/               # 🎯 Main package directory
├── tests/                                   # 🧪 Test files
├── .pre-commit-config.yaml   # 🔍 Pre-commit hooks
├── pyproject.toml                    # ⚙️ Project configuration
├── README.md                    # 📝 This file
└── LICENSE                           # ⚖️ MIT License
```

## 🛠️ Built-in Tools

- **UV**: Lightning-fast dependency management
- **mypy**: Static type checking
- **ruff**: Code formatting
- **ruff**: Fast Python linter
- **pytest**: Testing framework
- **docformatter**: Python docstring formatter
- **pre-commit**: Git hooks for code quality

## 🔍 Running Checks Manually

You can run the following checks manually to ensure code quality:

```bash
# Run pre-commit checks on all files
uv run pre-commit run --all-files

# Run pre-commit on staged files only
uv run pre-commit run

# Run type checking with mypy
uv run mypy

# Run linting with ruff
uv run ruff check .

# Run tests with pytest
uv run pytest

# Run tests with coverage
uv run pytest --cov=src
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Show Your Support

If you find this boilerplate helpful, please:

- ⭐ Star the repository
- 🔄 Share it with your network
- 🐛 Report any issues
- 💡 Suggest improvements

## 👨‍💻 Developers
This project is maintained by:

- [Jasmeet Gujral](https://github.com/JasGujral) - Creator and maintainer

---

Built with UV | [Submit Issue](https://github.com/JasGujral/uv-boilerplate/issues) | [Suggest Enhancement](https://github.com/JasGujral/uv-boilerplate/issues)
