"""The 'why' command - which package owns a given file."""
import subprocess

from .display import RED, RESET


def why(filepath: str) -> None:
    """Print which package owns the given file."""
    result = subprocess.run(["pacman", "-Qo", filepath], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"{RED}[!] No package owns '{filepath}'{RESET}")