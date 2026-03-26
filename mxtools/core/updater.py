import sys
import os
import io
import zipfile
import shutil
import tempfile
import subprocess
from urllib.request import urlopen, Request
from urllib.error import URLError

from mxtools import VERSION
from mxtools.core.utils import IS_WINDOWS

_REPO_USER   = "Szabomate1111"
_REPO_NAME   = "mxtools"
_VERSION_URL = f"https://raw.githubusercontent.com/{_REPO_USER}/{_REPO_NAME}/main/mxtools/__init__.py"
_ZIP_URL     = f"https://github.com/{_REPO_USER}/{_REPO_NAME}/archive/refs/heads/main.zip"


def _parse(v):
    return tuple(int(x) for x in v.lstrip("v").split("."))


def _fetch_remote_version():
    try:
        req = Request(_VERSION_URL, headers={"User-Agent": "mxtools-updater"})
        with urlopen(req, timeout=5) as r:
            for line in r.read().decode().splitlines():
                if line.startswith("VERSION"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        return None


def _install_dir():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _restart():
    if IS_WINDOWS:
        subprocess.Popen([sys.executable, "-m", "mxtools"], env=os.environ.copy())
        sys.exit(0)
    else:
        os.execv(sys.executable, [sys.executable, "-m", "mxtools"])


def check(console):
    remote = _fetch_remote_version()
    if not remote:
        return

    if _parse(remote) <= _parse(VERSION):
        return

    console.print()
    console.print(f"  [cyan]New version available:[/cyan]  [dim]{VERSION}[/dim]  →  [bold cyan]{remote}[/bold cyan]")
    console.print(f"  [dim]Updating...[/dim]")

    try:
        req = Request(_ZIP_URL, headers={"User-Agent": "mxtools-updater"})
        with urlopen(req, timeout=30) as r:
            data = r.read()
    except Exception as e:
        console.print(f"  [red]✗[/red]  Update failed: {e}\n")
        return

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            zf.extractall(tmp)
        extracted = next(os.scandir(tmp)).path
        src = os.path.join(extracted, "mxtools")
        dst = os.path.join(_install_dir(), "mxtools")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    console.print(f"  [green]✓[/green]  Updated to [bold cyan]{remote}[/bold cyan] — restarting...\n")
    _restart()
