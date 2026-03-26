from mxtools.core.deps import ensure
ensure()

from rich.console import Console
from rich.text import Text
from rich.align import Align

from mxtools.core import menu, updater
from mxtools.core.utils import clear
from mxtools.modules import MODULES

console = Console()


def main():
    updater.check(console)

    while True:
        chosen = menu.show(MODULES)
        if chosen is None:
            clear()
            console.print()
            console.print(Align.center(Text("Goodbye! 👋", style="bold cyan")))
            console.print()
            break
        chosen.run()


if __name__ == "__main__":
    main()
