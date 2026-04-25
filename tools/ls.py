"""File listing tool for the chat program.

This module lists files in the current directory or a relative subdirectory.
"""

import glob
import json
import os
from pathlib import PurePath


def ls(path=None):
    """List files in the current directory or in the given relative directory.

    >>> ls()
    '{"files": ["README.md", "__pycache__", "chat.py", "demo.gif", "demo.yml", "htmlcov", "package-lock.json", "package.json", "requirements.txt", "scratch.txt", "setup.py", "test_files", "test_projects", "testtext.txt", "tools", "venv"]}'
    >>> ls('nonexistent_dir')
    '{"error": "Directory does not exist."}'
    >>> ls('.')
    '{"files": ["./README.md", "./__pycache__", "./chat.py", "./demo.gif", "./demo.yml", "./htmlcov", "./package-lock.json", "./package.json", "./requirements.txt", "./scratch.txt", "./setup.py", "./test_files", "./test_projects", "./testtext.txt", "./tools", "./venv"]}'
    >>> ls('/')
    '{"error": "Absolute paths and directory traversal are not allowed."}'
    >>> ls('../')
    '{"error": "Absolute paths and directory traversal are not allowed."}'
    """
    try:
        if path is not None and path != "":
            if os.path.isabs(path) or any(part == ".." for part in PurePath(path).parts):
                raise ValueError("Absolute paths and directory traversal are not allowed.")
            if not os.path.isdir(path):
                raise ValueError("Directory does not exist.")

        if path is None or path == "":
            files = sorted(glob.glob("*"))
        else:
            files = sorted(glob.glob(f"{path}/*"))

        return json.dumps({"files": files})
    except Exception as e:
        return json.dumps({"error": str(e)})
