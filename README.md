# docsum

[![Flake8](https://img.shields.io/badge/code%20style-flake8-blue.svg)](https://flake8.pycqa.org/)
[![Doctests](https://img.shields.io/badge/doctests-passing-brightgreen.svg)](https://docs.python.org/3/library/doctest.html)
[![Integration Tests](https://img.shields.io/badge/integration%20tests-passing-brightgreen.svg)](https://docs.pytest.org/en/stable/)

## Overview

docsum is a Python project for command-line chat and file tools, including calculation, file listing, file reading, and pattern search. It supports both local tools and optional Groq LLM integration.

## Features
- Command-line chat interface
- Calculate math expressions
- List files in directories
- Read file contents
- Search files with regex
- Optional LLM support via Groq

## Testing & Linting

- **Flake8**: Run `flake8 .` to check code style.
- **Doctests**: Run `python -m doctest chat.py tools/cat.py tools/grep.py tools/ls.py` to verify doctests.
- **Integration Tests**: Run `python -m unittest discover` to run integration and CLI tests.

## Badges

- Flake8: ![Flake8](https://img.shields.io/badge/code%20style-flake8-blue.svg)
- Doctests: ![Doctests](https://img.shields.io/badge/doctests-passing-brightgreen.svg)
- Integration Tests: ![Integration Tests](https://img.shields.io/badge/integration%20tests-passing-brightgreen.svg)

---

Feel free to contribute or open issues!
