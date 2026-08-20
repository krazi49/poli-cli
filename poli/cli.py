"""Argparse routing, command dispatch, and factory aliases."""
import os
import re
import signal
import subprocess
import sys

from . import __version__
from .display import CYAN, GREEN, YELLOW, RED, MAGENTA, BOLD, RESET, log_error
from .aur import get_aur_info, search_aur, aur_upgrade
from .pacman import (
    install_package, download_package, reinstall_package,
    remove_packages, remove_orphans, upgrade_system, run_pacman,
)
from .stats import cmd_stats, cmd_check, cmd_log
from .tree import cmd_tree

NO_SUDO = {"help", "--help", "-h", "search", "info", "log", "stats", "why", "tree"}


def _needs_sudo():
    if len(sys.argv) < 2:
        return False
    return sys.argv[1].lower() not in NO_SUDO


def _ensure_sudo():
    if not _needs_sudo():
        return True
    try:
        subprocess.run(["sudo", "-v"], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{RED}[!] Sudo authorization failed.{RESET}")
        return False


def cmd_info(pkg_names):
    for pkg in pkg_names:
        result = subprocess.run(["pacman", "-Si", pkg], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    print(line)
            print()
            continue

        aur_data = get_aur_info([pkg])
        if not aur_data:
            print(f"{RED}[!] {pkg} not found anywhere.{RESET}")
            continue

        p = aur_data[0]
        print(f"{BOLD}Repository{RESET}   : AUR")
        print(f"{BOLD}Name{RESET}         : {p.get('Name', 'N/A')}")
        print(f"{BOLD}Version{RESET}      : {p.get('Version', 'N/A')}")
        print(f"{BOLD}Description{RESET}  : {p.get('Description', 'N/A')}")
        print(f"{BOLD}URL{RESET}          : {p.get('URL', 'N/A')}")
        print(f"{BOLD}License{RESET}      : {', '.join(p.get('License', ['N/A']))}")
        print(f"{BOLD}Depends{RESET}      : {', '.join(p.get('Depends', []))}")
        print(f"{BOLD}MakeDepends{RESET}  : {', '.join(p.get('MakeDepends', []))}")
        print(f"{BOLD}Votes{RESET}        : {p.get('NumVotes', 0)}")
        print(f"{BOLD}Popularity{RESET}   : {p.get('Popularity', 0):.2f}")
        print(f"{BOLD}Maintainer{RESET}   : {p.get('Maintainer', 'N/A')}")
        print()


def cmd_search(query):
    subprocess.run(["pacman", "-Ss", query])
    results = search_aur(query)
    if results:
        print(f"\n{BOLD}{MAGENTA}--- AUR ---{RESET}")
        for p in results[:10]:
            print(f"{MAGENTA}{p['Name']}{RESET} {GREEN}{p['Version']}{RESET}")
            print(f"  {p.get('Description', '')}")


def cmd_why(filepath):
    """Which package owns this file?"""
    result = subprocess.run(["pacman", "-Qo", filepath], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"{RED}[!] No package owns '{filepath}'{RESET}")


def show_help():
    print(f"{YELLOW}{BOLD}poli v{__version__}{RESET} — apt-like pacman wrapper with AUR\n")
    print(f"{BOLD}Commands:{RESET}")
    items = [
        ("assemble", "get", "Install packages from repos or AUR"),
        ("catalog", "search", "Search packages across all repos"),
        ("maintain", "update", "Full system upgrade"),
        ("disassemble", "remove", "Remove packages and orphans"),
        ("blueprint", "info", "Show detailed package info"),
        ("reforge", "reinstall", "Force rebuild and reinstall"),
        ("why", "", "Which package owns a file?"),
        ("tree", "", "Dependency tree for a package"),
        ("fetch", "download", "Download without installing"),
        ("audit", "check", "Verify package integrity"),
        ("floorplan", "stats", "System package statistics"),
        ("scrapheap", "orphans", "Clean up unused deps"),
        ("history", "log", "Recent package operations"),
    ]
    for primary, alias, desc in items:
        alias_str = f" ({alias})" if alias else ""
        print(f"  {CYAN}{primary:<14}{RESET}{alias_str:<12} {desc}")

    print(f"\n{BOLD}Examples:{RESET}")
    print(f"  poli assemble neovim          install neovim")
    print(f"  poli catalog 'web browser'    search for browsers")
    print(f"  poli why /usr/bin/nvim        which package owns this?")
    print(f"  poli tree neovim              show dependency tree")
    print(f"  poli maintain                 full system upgrade")
    print(f"  poli floorplan                system stats")


# Aliases: factory name -> canonical command
ALIASES = {
    "assemble": "get", "catalog": "search", "maintain": "update",
    "disassemble": "remove", "blueprint": "info", "reforge": "reinstall",
    "audit": "check", "floorplan": "stats", "scrapheap": "orphans",
    "fetch": "download", "history": "log",
}


def main():
    signal.signal(signal.SIGINT, lambda *_: (print(f"\n{YELLOW}Interrupted.{RESET}"), sys.exit(1)))

    if len(sys.argv) < 2:
        show_help()
        return

    cmd = sys.argv[1].lower()
    cmd = ALIASES.get(cmd, cmd)

    if cmd not in NO_SUDO:
        if not _ensure_sudo():
            return

    args = sys.argv[2:]

    dispatch = {
        "help": lambda: show_help(),
        "get": lambda: [install_package(p) for p in args] if args else print(f"{RED}Specify packages.{RESET}"),
        "search": lambda: cmd_search(args[0]) if args else print(f"{YELLOW}usage: poli search <query>{RESET}"),
        "update": lambda: upgrade_system(args) if args else (upgrade_system(), aur_upgrade()),
        "remove": lambda: remove_packages(args) if args else print(f"{RED}Specify packages.{RESET}"),
        "orphans": lambda: remove_orphans(),
        "info": lambda: cmd_info(args) if args else print(f"{RED}Specify packages.{RESET}"),
        "reinstall": lambda: reinstall_package(args) if args else print(f"{RED}Specify packages.{RESET}"),
        "check": lambda: cmd_check(),
        "log": lambda: cmd_log(int(args[0]) if args else 20),
        "stats": lambda: cmd_stats(),
        "why": lambda: cmd_why(args[0]) if args else print(f"{RED}Specify a file path.{RESET}"),
        "tree": lambda: cmd_tree(args[0]) if args else print(f"{RED}Specify a package.{RESET}"),
        "download": lambda: download_package(args) if args else print(f"{RED}Specify packages.{RESET}"),
    }

    handler = dispatch.get(cmd)
    if handler:
        handler()
    else:
        print(f"{RED}Unknown command: {cmd}{RESET}")
        print(f"Run {CYAN}poli help{RESET} for usage.")
