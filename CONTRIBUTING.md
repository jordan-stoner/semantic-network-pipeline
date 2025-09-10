# Contributing to MLX Chat

Thank you for your interest in contributing to MLX Chat! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
2. **Set up the development environment:**
   ```bash
   python initial_setup.py
   conda activate mlx-qwa
   ```
3. **Download a test model for development**

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and modular

## Design Principles

- **"Less is more"** - Prefer simple, efficient solutions
- **Dark mode only** - All interfaces use dark themes
- **Local processing** - No external API dependencies
- **User privacy** - All processing happens locally

## Project Structure

- `web_chat.py` - Main Flask server
- `config_launcher.py` - Configuration interface
- `create_wordcloud.py` - Text analysis engine
- `templates/` - HTML templates
- `static/` - CSS, JS, and assets
- `model/` - User data directories (excluded from git)

## Making Changes

1. **Create a feature branch:** `git checkout -b feature-name`
2. **Make your changes** following the coding standards
3. **Test thoroughly** with different models and configurations
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

## Testing

- Test with multiple MLX models
- Verify text analysis with various document types
- Check both configuration and direct launch methods
- Test on different system configurations

## Documentation

When making changes:
- Update relevant .md files
- Add inline comments for complex logic
- Update the README if adding new features
- Document any new dependencies

## Reporting Issues

When reporting bugs:
- Include your system information (OS, Python version)
- Describe steps to reproduce the issue
- Include error messages and logs
- Mention which models you're using

## Feature Requests

For new features:
- Explain the use case and benefit
- Consider how it fits with existing functionality
- Discuss implementation approach if possible

## Questions?

Feel free to open an issue for questions about:
- Development setup
- Architecture decisions
- Feature implementation
- Code organization

We appreciate all contributions, from bug fixes to new features to documentation improvements!