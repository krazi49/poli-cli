"""AUR RPC queries and recursive dependency resolution."""
import re
import subprocess
import urllib.request
import json
from .display import log_error, CYAN, GREEN, YELLOW, RED, BOLD, RESET

AUR_RPC = "https://aur.archlinux.org/rpc/?v=5"
AUR_DEPTH_LIMIT = 10


def query_aur(params):
    url = f"{AUR_RPC}&{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode()).get("results", [])
    except Exception as e:
        log_error(f"AUR RPC failed: {e}")
        return []


def get_aur_info(pkg_names):
    if not pkg_names:
        return []
    query = "&".join(f"arg[]={name}" for name in pkg_names)
    return query_aur(f"type=info&{query}")


def search_aur(query):
    return query_aur(f"type=search&arg={query}")


def resolve_deps(pkg_name, build_queue=None, visited=None, depth=0):
    if build_queue is None:
        build_queue = []
    if visited is None:
        visited = set()
    if pkg_name in visited:
        return build_queue
    visited.add(pkg_name)

    if depth > AUR_DEPTH_LIMIT:
        log_error(f"Dep depth limit ({AUR_DEPTH_LIMIT}) exceeded for {pkg_name}")
        return build_queue

    if subprocess.run(["pacman", "-Si", pkg_name], capture_output=True).returncode == 0:
        return build_queue

    info = get_aur_info([pkg_name])
    if not info:
        log_error(f"Could not find AUR package: {pkg_name}")
        return build_queue

    pkg = info[0]
    deps = pkg.get("Depends", []) + pkg.get("MakeDepends", [])
    for dep in deps:
        clean = re.split(r"[>=<]", dep)[0]
        resolve_deps(clean, build_queue, visited, depth + 1)

    if pkg_name not in build_queue:
        build_queue.append(pkg_name)
    return build_queue


def aur_upgrade():
    """Check for updates to all installed AUR packages."""
    print(f"{CYAN}Checking AUR for updates...{RESET}")
    local = subprocess.run(["pacman", "-Qm"], capture_output=True, text=True).stdout.strip().split("\n")
    pkgs = [l.split()[0] for l in local if l]

    if not pkgs:
        print(f"{GREEN}No AUR packages installed.{RESET}")
        return []

    remote_data = get_aur_info(pkgs)
    remote_versions = {p["Name"]: p["Version"] for p in remote_data}
    local_versions = {l.split()[0]: l.split()[1] for l in local if l}

    updates = [n for n, v in remote_versions.items() if v != local_versions.get(n)]

    if not updates:
        print(f"{GREEN}All AUR packages are up to date.{RESET}")
    else:
        print(f"{YELLOW}AUR updates: {', '.join(updates)}{RESET}")
    return updates
