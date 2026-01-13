#!/usr/bin/env python3
"""Sidecar entry point for BabelDOC Tauri application."""

import sys
import os

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(__file__))

from server import main

if __name__ == '__main__':
    main()
