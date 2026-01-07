#!/usr/bin/env python3
import sys
import subprocess
import os
import re
import shutil
import itertools
import time
import urllib.request
import xml.etree.ElementTree as ET

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
    """Fetches the latest news from Arch Linux to check for manual interventions."""
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
        print(f"{YELLOW}[!] Stop! Poli's locked by something else. Try and check if any pacman processes are being used.{RESET}")
        sys.exit(1)

def show_help():
    print(rf"{CYAN}{BOLD}")
    print(r"  ____  ____  __    ____ ")
    print(r" / __ \/ __ \/ /    /  _/")
    print(r" / /_/ / / / / /     / /  ")
    print(r" / ____/ /_/ / /____/ /   ")
    print(r"/_/    \____/_____/___/   CLI")
    print(f"{RESET}")
    print(f"{YELLOW}{BOLD}I don't know what to do. Try and use these commands instead.{RESET}")
    print(f"  {CYAN}update{RESET}          - Updates your packages and checks for any orphans")
    print(f"  {CYAN}search install{RESET}  - Finds packages you want and installs them")
    print(f"  {CYAN}search{RESET}          - Queries the AUR for packages")
    print(f"  {CYAN}install{RESET}         - Installs what you want")
    print(f"  {CYAN}orphans{RESET}         - Clean unused dependencies")
    print(f"  {CYAN}uninstall{RESET}       - Removes Poli from your system")

def draw_poli_ui(status, percent, start_time):
    elapsed = time.time() - start_time
    if percent > 0:
        total_est = elapsed / (percent / 100)
        remaining = total_est - elapsed
        mins, secs = divmod(int(remaining), 60)
        eta_str = f"{mins:02d}:{secs:02d}"
    else:
        eta_str = "--:--"

    bar_anim = ["░▒▓", "▒▓▒", "▓▒░", "█▓▒"]
    speed_bar = bar_anim[int(time.time() * 5) % 4] * 4

    sys.stdout.write(f"\r{CYAN} {next(SPINNER)} poli is assembling packages...{RESET} {BOLD}↳{RESET} {status[:40]}\033[K\n")
    sys.stdout.write(f"\r{YELLOW}[{speed_bar}] {percent}% {RESET} | {CYAN}Finished in:{RESET} {eta_str}\033[K")
    sys.stdout.write("\033[A")
    sys.stdout.flush()

def get_package_info(packages):
    print(f"{CYAN}Checking what you'll need...{RESET}")
    cmd = ["pacman", "-Si"] + packages
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0: return False

    name_match = re.search(r'^Name\s+:\s+(.+)', result.stdout, re.M)
    size_match = re.search(r'^Download Size\s+:\s+(.+)', result.stdout, re.M)
    
    name = name_match.group(1) if name_match else "Unknown"
    size = size_match.group(1) if size_match else "Unknown"
    
    print(f"\n{BOLD}Package:{RESET} {name} | {BOLD}Download size:{RESET} {YELLOW}{size}{RESET}")
    confirm = input(f"{BOLD}Should I start? [Y/n]: {RESET}").lower()
    return confirm in ['', 'y', 'yes']

def run_poli_process(command, success_msg, is_install=False):
    verbose = "--verbose" in sys.argv
    check_lock()
    if verbose:
        sys.argv.remove("--verbose")
    
    if is_install and not get_package_info(command[1:]): return

    full_cmd = ["sudo", "pacman", "--noconfirm"] + command
    sys.stdout.write(HIDE_CURSOR)
    start_time = time.time()
    current_pct = 0
    current_status = "Starting..."
    error_log = []

    try:
        if verbose:
            print(f"{YELLOW}>>> You'll see everything. Verbose mode is activated...{RESET}")
            subprocess.run(full_cmd)
        else:
            process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                error_log.append(line)
                pct_match = re.search(r'(\d+)%', line)
                if pct_match:
                    current_pct = int(pct_match.group(1))
                
                keys = ["cloning", "building", "installing", "checking", "downloading"]
                if any(k in line.lower() for k in keys):
                    current_status = line.strip().split('::')[-1].split('..')[0].strip()

                draw_poli_ui(current_status, current_pct, start_time)

            process.wait()
            sys.stdout.write(f"\r\033[K\n\r\033[K\033[A{SHOW_CURSOR}")
            
            if process.returncode == 0:
                total_time = int(time.time() - start_time)
                print(f"\n{GREEN}✅ {success_msg} ({total_time}s){RESET}")
            else:
                print(f"\n{RED}{BOLD}[!] Assembly failed!{RESET}")
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
        run_poli_process(["-S"] + sys.argv[2:], "Your package is ready!", is_install=True)
    elif action == "update":
        if check_arch_news():
            print(f"{CYAN}Checking your system for orphans...{RESET}")
            run_poli_process(["-Syu"], "System up to date!")
            orphans_check = subprocess.run(["pacman", "-Qqdt"], capture_output=True, text=True)
            if orphans_check.stdout:
                print(f"\n{YELLOW}I found unused packages (orphans). Run 'poli orphans' to find them a home.{RESET}")
        else:
            print(f"{YELLOW}Update cancelled, so you can check the news.{RESET}")
    elif action == "orphans":
        subprocess.run("sudo pacman -Rs $(pacman -Qqdt)", shell=True)
    elif action == "uninstall":
        print(f"{RED}{BOLD}Poli: Disassembling...{RESET}")
        if os.path.exists("/usr/local/bin/poli"):
            subprocess.run(["sudo", "rm", "/usr/local/bin/poli"])
            print(f"{GREEN}✅ poli has been removed from your system. See you some other time...{RESET}")
        else:
            print(f"{YELLOW}[!] poli wasn't found in /usr/local/bin/.{RESET}")
    else:
        show_help()

if __name__ == "__main__":
    main()
