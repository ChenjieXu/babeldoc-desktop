"""Lightweight spawned-process target used by frozen application smoke tests."""

import os
import time
from pathlib import Path


def smoke_worker(ready_file: str, hold_seconds: float = 0) -> None:
    """Prove a spawned child runs without importing or initializing the GUI."""
    if ready_file:
        Path(ready_file).write_text(str(os.getpid()), encoding="utf-8")
    if hold_seconds > 0:
        time.sleep(hold_seconds)
