"""Dependency tree visualization for installed packages."""
import subprocess
from .display import tree_print, CYAN, GREEN, YELLOW, RED, BOLD, RESET


def _get_deps(pkg_name):
    """Get dependencies of a package. Returns list of (name, is_aur) tuples."""
    result = subprocess.run(
        ["pacman", "-Qi", pkg_name], capture_output=True, text=True
    )
    if result.returncode != 0:
        return []

    deps = []
    in_depends = False
    for line in result.stdout.split("\n"):
        if line.startswith("Depends On"):
            in_depends = True
            raw = line.split(":", 1)[1].strip()
            if raw == "None":
                return []
            parts = raw.split()
            for p in parts:
                clean = p.split(">=")[0].split("<=")[0].split("=")[0]
                if clean:
                    deps.append(clean)
        elif in_depends and line.startswith(" "):
            parts = line.strip().split()
            for p in parts:
                clean = p.split(">=")[0].split("<=")[0].split("=")[0]
                if clean:
                    deps.append(clean)
        else:
            in_depends = False

    return deps


def _is_aur(pkg_name):
    result = subprocess.run(
        ["pacman", "-Si", pkg_name], capture_output=True
    )
    return result.returncode != 0


def _build_tree(pkg_name, visited=None, depth=0):
    if visited is None:
        visited = set()
    if pkg_name in visited or depth > 6:
        return []
    visited.add(pkg_name)

    deps = _get_deps(pkg_name)
    children = []
    for dep in deps:
        sub = _build_tree(dep, visited, depth + 1)
        children.append((dep, sub))

    return children


def cmd_tree(pkg_name):
    """Display dependency tree for a package."""
    result = subprocess.run(
        ["pacman", "-Qi", pkg_name], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"{RED}[!] Package '{pkg_name}' not found.{RESET}")
        return

    version = ""
    for line in result.stdout.split("\n"):
        if line.startswith("Version"):
            version = line.split(":", 1)[1].strip()
            break

    is_aur = _is_aur(pkg_name)
    repo_tag = f"{YELLOW}[AUR]{RESET}" if is_aur else f"{GREEN}[official]{RESET}"

    print(f"\n{BOLD}{pkg_name}{RESET} {version} {repo_tag}\n")

    tree = _build_tree(pkg_name)

    if not tree:
        print(f"  {CYAN}(no dependencies){RESET}\n")
        return

    tree_print(pkg_name, tree)
    print()
