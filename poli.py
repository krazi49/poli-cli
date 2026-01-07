#!/usr/bin/env python3
import sys
import subprocess
import os
import re
import itertools
import time
import urllib.request
import xml.etree.ElementTree as ET
import pty

# colours because you need them in life
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

SPINNER = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

def check_arch_news():
    print(f"{CYAN}📡 Checking Arch Linux News for manual interventions...{RESET}")
    news_url = "https://archlinux.org/feeds/news/"
    try:
        with urllib.request.urlopen(news_url, timeout=5) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            latest_item = root.find(".//item")
            title = latest_item.find("title").text
            link = latest_item.find("link").text
            
            if any(word in title.lower() for word in ["intervention", "required", "manual", "breaking"]):
                print(f"\n{RED}{BOLD}⚠️  ATTENTION: IMPORTANT NEWS DETECTED{RESET}")
                print(f"{YELLOW}Title: {title}{RESET}")
                print(f"{CYAN}Read more: {link}{RESET}")
                confirm = input(f"\n{BOLD}Have you read the news and wish to proceed? [y/N]: {RESET}").lower()
                return confirm == 'y'
            else:
                print(f"{GREEN}✅ No urgent manual interventions found.{RESET}")
                return True
    except Exception:
        print(f"{YELLOW}[!] Could not reach Arch News. Proceeding with caution...{RESET}")
        return True

def check_lock():
    if os.path.isfile("/var/lib/pacman/db.lck"):
        print(f"{YELLOW}[!] Stop! poli's locked by something else. Check other pacman processes.{RESET}")
        sys.exit(1)

def show_help():
    print(rf"{CYAN}{BOLD}")
    print(r"  ____  ____  __    ____ ")
    print(r" / __ \/ __ \/ /    /  _/")
    print(r" / /_/ / / / / /     / /  ")
    print(r" / ____/ /_/ / /____/ /   ")
    print(r"/_/    \____/_____/___/   ")
    print(f"{RESET}")
    print(f"{YELLOW}{BOLD}Commands:{RESET}")
    print(f"  {CYAN}update{RESET}          - Updates packages & checks for orphans")
    print(f"  {CYAN}search <query>{RESET}  - Search for a package")
    print(f"  {CYAN}install <pkg>{RESET}  - Installs a package")
    print(f"  {CYAN}remove <pkg>{RESET}   - Uninstalls/Removes a package")
    print(f"  {CYAN}orphans{RESET}         - Clean unused dependencies")

def draw_poli_ui(status, percent, start_time):
    elapsed = time.time() - start_time
    if percent > 0:
        total_est = elapsed / (percent / 100)
        remaining = max(0, total_est - elapsed)
        mins, secs = divmod(int(remaining), 60)
        eta_str = f"{mins:02d}:{secs:02d}"
    else:
        eta_str = "--:--"

    bar_anim = ["░▒▓", "▒▓▒", "▓▒░", "█▓▒"]
    speed_bar = bar_anim[int(time.time() * 5) % 4] * 4

    sys.stdout.write(f"\r{CYAN}{next(SPINNER)} poli is assembling...{RESET} {BOLD}↳{RESET} {status[:40]}\033[K\n")
    sys.stdout.write(f"\r{YELLOW}[{speed_bar}] {percent}% {RESET} | {CYAN}ETA:{RESET} {eta_str}\033[K")
    sys.stdout.write("\033[A") 
    sys.stdout.flush()

def search_package(query):
    print(f"{CYAN}Searching for '{query}'...{RESET}\n")
    # -Ss searches the sync databases
    result = subprocess.run(["pacman", "-Ss", query], capture_output=True, text=True)
    if result.stdout:
        # We split the output to make it look a bit cleaner
        lines = result.stdout.split('\n')
        for line in lines:
            if "/" in line:
                print(f"{CYAN}{BOLD}{line}{RESET}")
            else:
                print(f"  {line}")
        
        target = input(f"\n{BOLD}Found something? Type package name to install (or Enter to skip): {RESET}").strip()
        if target:
            run_poli_process(["-S", target], "Package assembled and installed.")
    else:
        print(f"{RED}'{query}' doesn't exist in this land.{RESET}")

def run_poli_process(command, success_msg):
    check_lock()
    sys.stdout.write(HIDE_CURSOR)
    start_time = time.time()
    current_pct = 0
    current_status = "Processing..."
    error_log = []

    try:
        master_fd, slave_fd = pty.openpty()
        full_cmd = ["sudo", "pacman", "--noconfirm"] + command
        
        process = subprocess.Popen(full_cmd, stdout=slave_fd, stderr=slave_fd, text=True)
        os.close(slave_fd)
        
        with os.fdopen(master_fd, 'r') as pipe:
            try:
                for line in pipe:
                    error_log.append(line)
                    pct_match = re.search(r'(\d+)%', line)
                    if pct_match:
                        current_pct = int(pct_match.group(1))
                    
                    keys = ["cloning", "building", "installing", "checking", "downloading", "removing", "upgrading"]
                    if any(k in line.lower() for k in keys):
                        current_status = line.strip().split('::')[-1].split('..')[0].strip()

                    draw_poli_ui(current_status, current_pct, start_time)
            except OSError:
                # This catches the Errno 5 when pacman finishes and closes the pty
                pass

        process.wait()
        sys.stdout.write(f"\r\033[K\n\r\033[K\033[A{SHOW_CURSOR}")
        
        if process.returncode == 0:
            print(f"\n{GREEN}✅ {success_msg} ({int(time.time() - start_time)}s){RESET}")
        else:
            print(f"\n{RED}{BOLD}[!] Couldn't assemble the package, this error may help:{RESET}")
            for err_line in error_log[-5:]:
                print(f" {RED}»{RESET} {err_line.strip()}")
    except KeyboardInterrupt:
        print(f"\n{SHOW_CURSOR}{BOLD}[!] Stopped.{RESET}")
    finally:
        sys.stdout.write(SHOW_CURSOR)

def main():
    if len(sys.argv) < 2:
        show_help()
        return

    action = sys.argv[1]
    if action == "install":
        run_poli_process(["-S"] + sys.argv[2:], "Package assembled!")
    elif action == "remove":
        run_poli_process(["-Rs"] + sys.argv[2:], "Package disassembled and cleaned.")
    elif action == "search":
        if len(sys.argv) > 2:
            search_package(sys.argv[2])
        else:
            print(f"{YELLOW}What should I search for? Usage: poli search <query>{RESET}")
    elif action == "update":
        if check_arch_news():
            run_poli_process(["-Syu"], "System updated. Remember to restart your PC.")
    elif action == "orphans":
        subprocess.run("sudo pacman -Rs $(pacman -Qqdt)", shell=True)
    else:
        show_help()

if __name__ == "__main__":
    main()
