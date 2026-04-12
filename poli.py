#!/usr/bin/env python3
import sys
import subprocess
import os
import re
import itertools
import time
import urllib.request
import json
import shutil
import pty
import signal

CYAN, GREEN, YELLOW, RED = "\033[36m", "\033[32m", "\033[33m", "\033[31m"
RESET, BOLD, MAGENTA = "\033[0m", "\033[1m", "\033[35m"
HIDE_CURSOR, SHOW_CURSOR = "\033[?25l", "\033[?25h"
SPINNER = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

def signal_handler(sig, frame):
    sys.stdout.write(f"\r{YELLOW} [!] Interrupted. Cleaning up...{RESET}\n")
    sys.stdout.write(SHOW_CURSOR)
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
-
def query_aur(params):
    url = f"https://aur.archlinux.org/rpc/?v=5&{params}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode()).get('results', [])
    except: return []

def get_aur_info(pkg_names):
    if not pkg_names: return []
    query = "&".join([f"arg[]={name}" for name in pkg_names])
    return query_aur(f"type=info&{query}")

def resolve_deps(pkg_name, build_queue=None, visited=None):
    """Recursively finds AUR dependencies that aren't in official repos."""
    if build_queue is None: build_queue = []
    if visited is None: visited = set()
    
    if pkg_name in visited: return build_queue
    visited.add(pkg_name)

    if subprocess.run(["pacman", "-Si", pkg_name], capture_output=True).returncode == 0:
        return build_queue

    info = get_aur_info([pkg_name])
    if not info: return build_queue

    pkg_data = info[0]
    deps = pkg_data.get('Depends', []) + pkg_data.get('MakeDepends', [])
    
    for dep in deps:
        clean_dep = re.split('[>=<]', dep)[0]
        resolve_deps(clean_dep, build_queue, visited)

    if pkg_name not in build_queue:
        build_queue.append(pkg_name)
    return build_queue

def install_package(pkg_name):
    """Decides whether to use pacman or the recursive AUR builder."""
    if subprocess.run(["pacman", "-Si", pkg_name], capture_output=True).returncode == 0:
        run_poli_process(["-S", pkg_name], f"{pkg_name} assembled.")
        return

    print(f"{CYAN}🔍 Solving AUR dependencies for {BOLD}{pkg_name}{RESET}...")
    queue = resolve_deps(pkg_name)
    
    if not queue:
        print(f"{RED}[!] Could not find {pkg_name} anywhere.{RESET}")
        return

    print(f"{YELLOW}Assembly order: {' -> '.join(queue)}{RESET}")
    for target in queue:
        build_aur(target)

def build_aur(pkg_name):
    build_dir = f"/tmp/poli_{pkg_name}"
    try:
        if os.path.exists(build_dir): shutil.rmtree(build_dir)
        subprocess.run(["git", "clone", "--quiet", f"https://aur.archlinux.org/{pkg_name}.git", build_dir], check=True)
        subprocess.run(["makepkg", "-sirc", "--noconfirm"], cwd=build_dir, check=True)
    except:
        print(f"{RED}❌ Failed to build {pkg_name}{RESET}")
    finally:
        if os.path.exists(build_dir): shutil.rmtree(build_dir)

def draw_poli_ui(status, percent, start_time):
    elapsed = time.time() - start_time
    eta = f"{int(elapsed / (percent/100) - elapsed)}s" if percent > 0 else "--"
    sys.stdout.write(f"\r{CYAN}{next(SPINNER)} poli is assembling...{RESET} {BOLD}↳{RESET} {status[:30]}\033[K\n")
    sys.stdout.write(f"\r{YELLOW}█▓▒░ {percent}% {RESET} | {CYAN}ETA:{RESET} {eta}\033[K")
    sys.stdout.write("\033[A") 
    sys.stdout.flush()

def run_poli_process(command, success_msg):
    sys.stdout.write(HIDE_CURSOR)
    start_time, current_pct, current_status = time.time(), 0, "Processing..."
    try:
        master_fd, slave_fd = pty.openpty()
        process = subprocess.Popen(["sudo", "pacman", "--noconfirm"] + command, stdout=slave_fd, stderr=slave_fd, text=True)
        os.close(slave_fd)
        with os.fdopen(master_fd, 'r') as pipe:
            try:
                for line in pipe:
                    if '%' in line:
                        match = re.search(r'(\d+)%', line)
                        if match: current_pct = int(match.group(1))
                    if any(k in line.lower() for k in ["installing", "downloading", "upgrading"]):
                        current_status = line.strip().split('::')[-1].split('..')[0].strip()
                    draw_poli_ui(current_status, current_pct, start_time)
            except OSError: pass
        process.wait()
        sys.stdout.write(f"\r\033[K\n\r\033[K\033[A{SHOW_CURSOR}")
        if process.returncode == 0: print(f"\n{GREEN}✅ {success_msg}{RESET}")
    finally: sys.stdout.write(SHOW_CURSOR)

def search(query):
    subprocess.run(["pacman", "-Ss", query])
    results = query_aur(f"type=search&arg={query}")
    if results:
        print(f"\n{BOLD}{MAGENTA}--- AUR ---{RESET}")
        for p in results[:10]:
            print(f"{MAGENTA}{p['Name']}{RESET} {GREEN}{p['Version']}{RESET}\n  {p.get('Description','')}")

def aur_upgrade():
    """Checks for updates for all installed AUR packages."""
    print(f"{CYAN}Checking AUR for updates...{RESET}")
    local = subprocess.run(["pacman", "-Qm"], capture_output=True, text=True).stdout.strip().split('\n')
    pkgs = [l.split()[0] for l in local if l]
    
    remote_data = get_aur_info(pkgs)
    remote_versions = {p['Name']: p['Version'] for p in remote_data}
    local_versions = {l.split()[0]: l.split()[1] for l in local if l}

    updates = []
    for name, v_remote in remote_versions.items():
        if v_remote != local_versions.get(name):
            updates.append(name)

    if not updates:
        print(f"{GREEN}All AUR packages are up to date.{RESET}")
        return

    print(f"{YELLOW}Updates found: {', '.join(updates)}{RESET}")
    for u in updates:
        install_package(u)

def show_help():
    print(f"{YELLOW}{BOLD}Usage:{RESET}")
    print(f"  poli <action> [arguments]")
    print(f"\n{YELLOW}{BOLD}Actions:{RESET}")
    
    help_items = [
        ("get <pkg>", "Install packages from official repos or AUR"),
        ("search <query>", "Search for packages across all repositories"),
        ("update", "Full system upgrade (Pacman + AUR)"),
        ("remove <pkg>", "Disassemble (remove) a package and its dependencies"),
        ("orphans", "Clean up unused dependencies (bloat)"),
        ("help", "Show this assembly manual")
    ]

    for action, desc in help_items:
        print(f"  {CYAN}{action:<18}{RESET} - {desc}")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
        
    try:
        subprocess.run(["sudo", "-v"], check=True)
    except subprocess.CalledProcessError:
        print(f"{RED}[!] Sudo authorization failed.{RESET}")
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd in ["help", "--help", "-h"]:
        show_help()
    elif cmd == "get":
        if not args:
            print(f"{RED}Specify packages to get.{RESET}")
        else:
            for p in args: install_package(p)
    elif cmd == "search":
        if not args:
            print(f"{YELLOW}usage: poli search <query>{RESET}")
        else:
            search(args[0])
    elif cmd == "update":
        run_poli_process(["-Syu"], "System updated.")
        aur_upgrade()
    elif cmd == "remove":
        if not args:
            print(f"{RED}Specify packages to remove.{RESET}")
        else:
            run_poli_process(["-Rs"] + args, "Packages disassembled.")
    elif cmd == "orphans":
        orphans = subprocess.run(["pacman", "-Qqdt"], capture_output=True, text=True).stdout.strip()
        if orphans:
            run_poli_process(["-Rs"] + orphans.split(), "System cleaned.")
        else:
            print(f"{GREEN}No orphans found. System is lean.{RESET}")
    else:
        print(f"{RED}Unknown command: {cmd}{RESET}")
        show_help()
        
if __name__ == "__main__":
    main()