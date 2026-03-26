import sys
import subprocess
import importlib.util

from mxtools.core.utils import IS_WINDOWS

DEPS = {
    "requests": "requests",
    "bs4":      "beautifulsoup4",
    "rich":     "rich",
    "yt_dlp":   "yt-dlp",
}


def ensure():
    missing = [DEPS[mod] for mod in DEPS if not importlib.util.find_spec(mod)]
    if IS_WINDOWS and not importlib.util.find_spec("_curses"):
        missing.append("windows-curses")
    if missing:
        print(f"\033[36mInstalling dependencies: {', '.join(missing)}\033[0m")
        flags = [] if IS_WINDOWS else ["--break-system-packages"]
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q"] + flags + missing
        )
