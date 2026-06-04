# Contributing to Text-for-VUP

Thank you for your interest in Text-for-VUP! We welcome bug reports, feature requests, and pull requests.

## 🐛 Reporting Bugs

When submitting an issue, please include:
- Your operating system and Python version
- Complete error messages and stack traces
- Steps to reproduce the issue
- Your configuration file (if applicable)
- Screenshots of the problem (if relevant)

Example:
```
**OS:** Windows 11
**Python:** 3.10
**Issue:** Webcam not detected on startup

**Steps to reproduce:**
1. Run `python main.py`
2. See error message...

**Expected:** Webcam initializes successfully
**Actual:** RuntimeError: Cannot open webcam
```

## 💡 Suggesting Features

Have an idea? Submit an issue describing:
- What you want to implement
- Why you think it would be useful
- Potential implementation approach (if you have ideas)

## 🔧 Submitting Pull Requests

1. **Fork** the repository
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-amazing-feature
   ```
3. **Make your changes** and test thoroughly
4. **Commit with clear messages:**
   ```bash
   git commit -m "Add support for multiple webcams"
   ```
5. **Push to your fork:**
   ```bash
   git push origin feature/your-amazing-feature
   ```
6. **Open a Pull Request** with a clear description

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable names
- Add docstrings to functions
- Keep lines under 100 characters where possible

### Testing Your Changes

Before submitting a PR, test locally:

```bash
# Test main application
python main.py profiles/vup.json

# Test configuration editor
python config_editor.py

# Test keyboard fallback (without webcam)
python main.py
```

## 📚 Documentation

Documentation improvements are always welcome:
- Fix typos and clarify explanations
- Add usage tutorials or examples
- Improve code comments
- Create ASCII art character designs

## 🎨 Share Character Designs

Created a cool ASCII character? We'd love to include it!

1. Create a JSON configuration file
2. Submit a PR adding it to `profiles/` directory
3. Or open an issue to discuss it first

See [EXAMPLE_CHARACTERS.md](EXAMPLE_CHARACTERS.md) for inspiration.

## 🌍 Translations

Help us reach more people by translating:
- README and documentation
- Code comments (secondary priority)
- User-facing messages

## ⚖️ Code of Conduct

Be respectful and constructive in all interactions. We're all here to create something cool together!

---

Thank you for contributing! 🙏
