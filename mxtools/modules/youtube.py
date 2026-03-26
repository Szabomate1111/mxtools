import os
import shutil

import yt_dlp
from rich.console import Console
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from rich.rule import Rule
from rich.padding import Padding

from mxtools.core.utils import clear

LABEL = "YouTube downloader"
DESC  = "Download video or audio using yt-dlp"

console = Console()

_FORMATS_FFMPEG = {
    "1": ("Best quality video (mp4)", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"),
    "2": ("1080p video",              "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"),
    "3": ("720p video",               "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"),
    "4": ("Audio only (mp3)",         "bestaudio/best"),
}

_FORMATS_NO_FFMPEG = {
    "1": ("Best quality (pre-merged mp4)", "best[ext=mp4]/best"),
    "2": ("720p (pre-merged mp4)",         "best[height<=720][ext=mp4]/best[height<=720]"),
    "3": ("Audio only (m4a/webm)",         "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio"),
}


def run():
    clear()
    console.print()
    console.print(Rule("[bold cyan]YouTube Downloader[/bold cyan]", style="cyan"))
    console.print()

    has_ffmpeg = shutil.which("ffmpeg") is not None
    formats = _FORMATS_FFMPEG if has_ffmpeg else _FORMATS_NO_FFMPEG

    if not has_ffmpeg:
        console.print("  [yellow]⚠[/yellow]  ffmpeg not found — showing pre-merged formats only.\n")

    url = Prompt.ask("  [bold cyan]YouTube URL[/bold cyan]", console=console)

    fmt_tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 2), border_style="dim")
    fmt_tbl.add_column("", style="bold yellow", width=3)
    fmt_tbl.add_column("", style="white")
    for key, (label, _) in formats.items():
        fmt_tbl.add_row(key, label)
    console.print()
    console.print(Padding(fmt_tbl, (0, 2)))
    console.print()

    choice  = Prompt.ask("  [bold cyan]Format[/bold cyan]", choices=list(formats), default="1", console=console)
    out_dir = Prompt.ask("  [bold cyan]Save to[/bold cyan]", default=os.path.expanduser("~/Downloads"), console=console)
    os.makedirs(out_dir, exist_ok=True)

    ydl_opts = {
        "format":      formats[choice][1],
        "outtmpl":     os.path.join(out_dir, "%(title)s.%(ext)s"),
        "quiet":       False,
        "no_warnings": True,
    }
    if has_ffmpeg and choice == "4":
        ydl_opts["postprocessors"] = [{
            "key":              "FFmpegExtractAudio",
            "preferredcodec":   "mp3",
            "preferredquality": "192",
        }]

    console.print()
    console.print(Rule("[dim]Downloading[/dim]", style="dim"))
    console.print()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        console.print()
        console.print(f"  [green]✓[/green]  Done! Saved to: [cyan]{out_dir}[/cyan]")
    except Exception as e:
        console.print(f"\n  [red]✗[/red]  Error: [red]{e}[/red]")

    console.print()
    Prompt.ask("  [dim]Press Enter to go back[/dim]", default="", show_default=False, console=console)
