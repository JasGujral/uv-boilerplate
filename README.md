# 🚀 uv-boilerplate

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![UV](https://img.shields.io/badge/uv-0.1.0-orange.svg)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/ruff-0.1.0-red.svg)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-1.5.0-blue.svg)](http://mypy-lang.org/)
[![pytest](https://img.shields.io/badge/pytest-7.4.0-green.svg)](https://docs.pytest.org/)

> 🚀 The Ultimate Python Project Boilerplate that will supercharge your development! Built with UV for blazing fast dependency management and complete CI/CD workflows out of the box.

## 🌟 Why This Boilerplate Will Change Your Life

- ⚡ **Hypersonic Speed**: Powered by [UV](https://github.com/astral-sh/uv) - Say goodbye to slow package installations forever
- 🛠️ **Enterprise-Grade Setup**: Production-ready with industry best practices baked in
- 🔄 **CI/CD Ready**: Pre-configured GitHub Actions workflows for testing, linting, and security scanning
- 📦 **Cutting-Edge Stack**: Latest Python 3.12 with modern tooling
- 🛡️ **Battle-Tested Quality**: Comprehensive testing, linting, and type checking
- 🚀 **Zero-to-Hero**: Start building production-grade applications in minutes

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
├── .github/              # GitHub Actions workflows
├── src/                  # Your source code
│   └── your_project/    # Main package directory
├── tests/               # Test files
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml       # Project configuration
├── README.md           # This file
└── LICENSE             # MIT License
```

## 🛠️ Built-in Tools

- **UV**: Lightning-fast dependency management
- **mypy**: Static type checking
- **black**: Code formatting
- **ruff**: Fast Python linter
- **pytest**: Testing framework
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

## 🙏 Acknowledgments

- [UV](https://github.com/astral-sh/uv) - The amazing Python package installer
- [Python](https://www.python.org/) - The best programming language
- All the amazing open-source tools that make this possible

---

Made with ❤️ using UV | [Report Bug](https://github.com/JasGujral/uv-boilerplate/issues) | [Request Feature](https://github.com/JasGujral/uv-boilerplate/issues)
