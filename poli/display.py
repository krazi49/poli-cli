"""ANSI colors, spinner, progress bar, and table formatting."""
import sys
import time
import itertools

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
BOLD = "\033[1m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
SPINNER = itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")


def log_error(msg):
    sys.stderr.write(f"{RED}[ERROR]{RESET} {msg}\n")
    sys.stderr.flush()


class ProgressBar:
    """Live two-line progress display — replaces the old pty hack."""

    def __init__(self):
        self.start_time = None
        self.pct = 0
        self.status = ""

    def start(self):
        self.start_time = time.time()
        sys.stderr.write(HIDE_CURSOR)

    def update(self, pct=None, status=None):
        if pct is not None:
            self.pct = pct
        if status is not None:
            self.status = status
        elapsed = time.time() - self.start_time
        eta = f"{int(elapsed * (100 - self.pct) / max(self.pct, 1))}s" if self.pct > 0 else "--"
        filled = int(30 * self.pct / 100)
        bar = f"{YELLOW}{'█' * filled}{'░' * (30 - filled)}{RESET}"
        sys.stderr.write(f"\r {CYAN}{next(SPINNER)}{RESET} {self.status[:40]}\033[K")
        sys.stderr.write(f"\n {bar} {self.pct:3d}% {CYAN}ETA:{RESET} {eta}\033[K")
        sys.stderr.write("\033[A")
        sys.stderr.flush()

    def finish(self, msg="done"):
        sys.stderr.write(f"\r\033[K\033[A\033[K")
        sys.stderr.write(SHOW_CURSOR)
        sys.stderr.flush()
        print(f"{GREEN}✓ {msg}{RESET}")


def table(headers, rows, indent=2):
    """Print a simple formatted table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    sep = "─"
    header_line = " │ ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    div_line = "─┼─".join(sep * w for w in widths)
    prefix = " " * indent
    print(f"{prefix}{BOLD}{header_line}{RESET}")
    print(f"{prefix}{div_line}")
    for row in rows:
        print(f"{prefix}{' │ '.join(str(c).ljust(widths[i]) for i, c in enumerate(row))}")


def tree_print(label, children, prefix="", last=True):
    """Recursive tree-printer for dependency trees."""
    connector = "└── " if last else "├── "
    print(f"{prefix}{connector}{label}")
    child_prefix = prefix + ("    " if last else "│   ")
    for i, child in enumerate(children):
        tree_print(child[0], child[1], child_prefix, i == len(children) - 1)
