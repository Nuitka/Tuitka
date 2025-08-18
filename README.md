# Tuitka - A TUI for Nuitka

Tuitka is a Terminal User Interface (TUI) wrapper that leverages Nuitka under the hood to compile Python applications. It aims to simplify the compilation process for developers by providing:
- **Presets** for common compilation scenarios
- **Navigable TUI** for easy configuration without memorizing command-line flags
- **Intuitive interface** that makes Python compilation accessible to all developers

## Features

### Automatic Dependency Management
- Automatically detects and handles dependencies from requirements.txt, pyproject.toml, and PEP 723 inline script metadata
- Uses `uv` for fast, isolated dependency installation
- Smart plugin detection based on imported libraries

### Splash Screen
Shows the Nuitka branding on startup
![Splash Screen](https://raw.githubusercontent.com/Nuitka/Tuitka/refs/heads/main/images/Splash_screen.png)

### Script Selection
Browse and select Python scripts to compile with an interactive file dialog
![Script Input](https://raw.githubusercontent.com/Nuitka/Tuitka/refs/heads/main/images/script_input.png)

### Settings Configuration
Configure Nuitka compilation settings and flags through an intuitive UI
![Settings UI](https://raw.githubusercontent.com/Nuitka/Tuitka/refs/heads/main/images/settings_ui.png)

## Usage

### Dependency Detection
Tuitka requires one of the following to detect your script's dependencies if it contains third party libraries:
- `requirements.txt` file
- `pyproject.toml` file  
- **PEP 723 inline metadata (preferred)**

#### PEP 723 Example (Recommended)
Add this metadata block at the top of your Python script:
```python
# /// script
# dependencies = [
#   "requests>=2.31.0",
#   "numpy==1.24.0",
#   "pandas",
# ]
# ///

import requests
import numpy as np
import pandas as pd

# Your code here...
```

### Running Tuitka

Run the TUI interface:
```bash
tuitka
```

Or compile a Python file directly:
```bash
tuitka script.py
```
