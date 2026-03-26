import os
import io
import zipfile
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.align import Align
from rich import box
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.padding import Padding

from mxtools.core.utils import clear

LABEL = "Download images from website"
DESC  = "Scrape all images from a URL and save them as a ZIP"

console = Console()

_IMG_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico', '.tiff'}


def _is_img(url):
    return any(urlparse(url).path.lower().endswith(e) for e in _IMG_EXTS)


def _scrape(url):
    hdrs = {"User-Agent": "Mozilla/5.0"}
    with console.status("[cyan]Loading page...[/cyan]", spinner="dots"):
        resp = requests.get(url, headers=hdrs, timeout=15)
        resp.raise_for_status()
    soup  = BeautifulSoup(resp.text, "html.parser")
    found = set()
    for tag in soup.find_all("img"):
        src = tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src")
        if src: found.add(urljoin(url, src))
    for tag in soup.find_all("a", href=True):
        h = urljoin(url, tag["href"])
        if _is_img(h): found.add(h)
    for tag in soup.find_all("meta"):
        c = tag.get("content", "")
        if c and _is_img(c): found.add(urljoin(url, c))
    return sorted(found)


def run():
    clear()
    console.print()
    console.print(Rule("[bold cyan]Image Downloader[/bold cyan]", style="cyan"))
    console.print()

    url = Prompt.ask("  [bold cyan]URL[/bold cyan]", console=console)
    if not url.startswith("http"):
        url = "https://" + url
    domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
    out = Prompt.ask("  [bold cyan]ZIP filename[/bold cyan]", default=f"{domain}_images.zip", console=console)
    if not out.endswith(".zip"):
        out += ".zip"
    console.print()

    try:
        images = _scrape(url)
    except Exception as e:
        console.print(f"  [red]✗[/red] Error: [red]{e}[/red]")
        Prompt.ask("\n  [dim]Press Enter to go back[/dim]", default="", show_default=False, console=console)
        return

    if not images:
        console.print("  [yellow]⚠[/yellow]  No images found.")
        Prompt.ask("\n  [dim]Press Enter to go back[/dim]", default="", show_default=False, console=console)
        return

    console.print(f"  [green]✓[/green]  [bold]{len(images)}[/bold] images found\n")

    prev = Table(box=box.SIMPLE, show_header=False, padding=(0, 1), border_style="dim")
    prev.add_column("", style="dim cyan", width=4)
    prev.add_column("", style="dim white")
    for i, img in enumerate(images[:8], 1):
        prev.add_row(f"{i}.", os.path.basename(urlparse(img).path)[:55] or "image")
    if len(images) > 8:
        prev.add_row("...", f"[dim]and {len(images)-8} more[/dim]")
    console.print(Padding(prev, (0, 2)))
    console.print()

    if not Confirm.ask(f"  Download → [cyan]{out}[/cyan]?", default=True, console=console):
        console.print("  [dim]Cancelled.[/dim]")
        Prompt.ask("\n  [dim]Press Enter to go back[/dim]", default="", show_default=False, console=console)
        return

    console.print()
    hdrs = {"User-Agent": "Mozilla/5.0"}
    downloaded = failed = skipped = 0
    buf = io.BytesIO()

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold white]{task.description}"),
        BarColumn(bar_width=28, style="cyan", complete_style="bold cyan"),
        TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
        TextColumn("[dim]{task.fields[fn]}[/dim]"),
        console=console,
    ) as prog:
        task = prog.add_task("  Downloading", total=len(images), fn="")
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            seen = {}
            for img_url in images:
                fn = os.path.basename(urlparse(img_url).path)
                if not fn or "." not in fn:
                    fn = f"image_{downloaded+skipped+failed+1}.jpg"
                if fn in seen:
                    seen[fn] += 1
                    nm, ex = os.path.splitext(fn)
                    fn = f"{nm}_{seen[fn]}{ex}"
                else:
                    seen[fn] = 0
                prog.update(task, fn=fn[:28])
                try:
                    r = requests.get(img_url, headers=hdrs, timeout=10)
                    r.raise_for_status()
                    if len(r.content) < 100:
                        skipped += 1
                    else:
                        zf.writestr(fn, r.content)
                        downloaded += 1
                except Exception:
                    failed += 1
                prog.advance(task)

    if downloaded > 0:
        with open(out, "wb") as f:
            f.write(buf.getvalue())
        sk = os.path.getsize(out) / 1024
        ss = f"{sk:.1f} KB" if sk < 1024 else f"{sk/1024:.2f} MB"
        console.print()
        res = Table(box=box.ROUNDED, border_style="green", padding=(0, 2), show_header=False, expand=False)
        res.add_column("", style="bold green")
        res.add_column("", style="white")
        res.add_row("✓ Downloaded", f"[bold]{downloaded}[/bold] images")
        if failed:  res.add_row("✗ Failed",  f"[red]{failed}[/red] images")
        if skipped: res.add_row("⊘ Skipped", f"[yellow]{skipped}[/yellow] images")
        res.add_row("📦 Size",  f"[cyan]{ss}[/cyan]")
        res.add_row("📁 Saved", f"[cyan]{os.path.abspath(out)}[/cyan]")
        console.print(Align.center(res))
    else:
        console.print("  [red]✗[/red]  Nothing could be downloaded.")

    console.print()
    Prompt.ask("  [dim]Press Enter to go back[/dim]", default="", show_default=False, console=console)
