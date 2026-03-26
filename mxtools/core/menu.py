import curses

from mxtools.core.utils import BANNER_LINES, SUBTITLE, VERSION


def _draw(stdscr, modules, selected):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,  -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(4, 8, -1)

    CYAN  = curses.color_pair(1) | curses.A_BOLD
    WHITE = curses.color_pair(2)
    SEL   = curses.color_pair(3) | curses.A_BOLD
    DIM   = curses.color_pair(4)

    stdscr.erase()
    h, w = stdscr.getmaxyx()
    row = 1

    for line in BANNER_LINES:
        x = max(0, (w - len(line)) // 2)
        if row < h:
            try: stdscr.addstr(row, x, line, CYAN)
            except curses.error: pass
        row += 1

    row += 1
    for text, style in [(SUBTITLE, DIM), (VERSION, curses.color_pair(1))]:
        if row < h:
            x = max(0, (w - len(text)) // 2)
            try: stdscr.addstr(row, x, text, style)
            except curses.error: pass
        row += 1
    row += 1

    box_w   = 62
    box_x   = max(0, (w - box_w) // 2)
    inner_w = box_w - 4

    def hline(r):
        if r >= h: return
        try:
            stdscr.addstr(r, box_x,          "+", CYAN)
            stdscr.addstr(r, box_x + 1,       "-" * (box_w - 2), CYAN)
            stdscr.addstr(r, box_x + box_w-1, "+", CYAN)
        except curses.error: pass

    hline(row); row += 1

    if row < h:
        header = " Select a function"
        try:
            stdscr.addstr(row, box_x,          "|",  CYAN)
            stdscr.addstr(row, box_x+1,         " ",  WHITE)
            stdscr.addstr(row, box_x+2,          header.ljust(inner_w), curses.color_pair(1)|curses.A_BOLD)
            stdscr.addstr(row, box_x+2+inner_w, " |", CYAN)
        except curses.error: pass
    row += 1

    hline(row); row += 1

    items = modules + [None]
    for i, mod in enumerate(items):
        if row >= h: break
        label = mod.LABEL if mod else "Exit"
        desc  = mod.DESC  if mod else "Goodbye!"
        is_sel = (i == selected)
        lline  = (("  > " if is_sel else "    ") + label).ljust(inner_w)
        try:
            stdscr.addstr(row, box_x,          "| ",  CYAN)
            stdscr.addstr(row, box_x+2,         lline, SEL if is_sel else WHITE)
            stdscr.addstr(row, box_x+2+inner_w, " |",  CYAN)
        except curses.error: pass
        row += 1
        if row < h:
            dline = ("   " + desc)[:inner_w].ljust(inner_w)
            try:
                stdscr.addstr(row, box_x,          "| ",  CYAN)
                stdscr.addstr(row, box_x+2,         dline, DIM)
                stdscr.addstr(row, box_x+2+inner_w, " |",  CYAN)
            except curses.error: pass
            row += 1
        if i < len(items) - 1 and row < h:
            hline(row); row += 1

    hline(row); row += 2

    hint = "↑/↓  navigate    Enter  select    q  quit"
    if row < h:
        x = max(0, (w - len(hint)) // 2)
        try: stdscr.addstr(row, x, hint, DIM)
        except curses.error: pass

    stdscr.refresh()


def show(modules):
    items = modules + [None]
    selected = [0]

    def _loop(stdscr):
        while True:
            _draw(stdscr, modules, selected[0])
            key = stdscr.getch()
            n = len(items)
            if   key in (curses.KEY_UP,   ord('k')): selected[0] = (selected[0] - 1) % n
            elif key in (curses.KEY_DOWN, ord('j')): selected[0] = (selected[0] + 1) % n
            elif key in (curses.KEY_ENTER, 10, 13, ord(' ')): return items[selected[0]]
            elif key in (ord('q'), ord('Q'), 27):    return None

    return curses.wrapper(_loop)
