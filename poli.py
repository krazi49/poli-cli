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
            # Get the latest news item
            latest_item = root.find(".//item")
            title = latest_item.find("title").text
            link = latest_item.find("link").text
            
            # Common keywords indicating a system-breaking change
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
    print(r" / __ \/ __ \/ /   /  _/")
    print(r" / /_/ / / / / /    / /  ")
    print(r" / ____/ /_/ / /____/ /   ")
    print(r"/_/    \____/_____/___/   CLI")
    print(f"{RESET}")
    print(f"{YELLOW}{BOLD}I don't know what to do. Try and use these commands instead.{RESET}")
    print(f"  {CYAN}update{RESET}          - Updates your packages and checks for any orphans")
    print(f"  {CYAN}install{RESET}         - Installs what you want")
    print(f"  {CYAN}search install{RESET}  - Search and pick for what you want")
    print(f"  {CYAN}orphans{RESET}         - Clean unused dependencies")

def draw_poli_ui(status, percent, start_time):
    """
    Line 1: Spinner + Action
    Line 2: Speed Bar + ETA
    """
    elapsed = time.time() - start_time
    
    # calculate the ETA based on percentage
    if percent > 0:
        total_est = elapsed / (percent / 100)
        remaining = total_est - elapsed
        mins, secs = divmod(int(remaining), 60)
        eta_str = f"{mins:02d}:{secs:02d}"
    else:
        eta_str = "--:--"

    # create a progress bar
    bar_anim = ["░▒▓", "▒▓▒", "▓▒░", "█▓▒"]
    speed_bar = bar_anim[int(time.time() * 5) % 4] * 4

    sys.stdout.write(f"\r{CYAN}{next(SPINNER)} Poli is assembling packages...{RESET} {BOLD}↳{RESET} {status[:40]}\033[K\n")
    sys.stdout.write(f"\r{YELLOW}[{speed_bar}] {percent}% {RESET} | {CYAN}Finished in:{RESET} {eta_str}\033[K")
    sys.stdout.write("\033[A") # move back up one line
    sys.stdout.flush()

def get_package_info(packages):
    print(f"{CYAN}Checking what you'll need...{RESET}")
    cmd = ["pacman", "-Si"] + packages
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0: return True

    name = re.search(r'^Name\s+:\s+(.+)', result.stdout, re.M).group(1)
    size = re.search(r'^Download Size\s+:\s+(.+)', result.stdout, re.M).group(1)
    
    print(f"\n{BOLD}Package:{RESET} {name} | {BOLD}Download size:{RESET} {YELLOW}{size}{RESET}")
    confirm = input(f"{BOLD}Should I start? [Y/n]: {RESET}").lower()
    return confirm in ['', 'y', 'yes']

def run_poli_process(command, success_msg, is_install=False):
    verbose = "--verbose" in sys.argv
    check_lock()
    if verbose:
        sys.argv.remove("--verbose")
    full_cmd = ["sudo", "pacman", "--noconfirm"] + command
    
    if is_install and not get_package_info(command[1:]): return

    sys.stdout.write(HIDE_CURSOR)
    start_time = time.time()
    current_pct = 0
    current_status = "Starting..."

    try:
        if verbose:
            # if user really wants verbose, they will get it. showing raw output
            print(f"{YELLOW}>>> You'll see everything. Verbose mode is activated...{RESET}")
            subprocess.run(full_cmd)
        else:

        # forcing pacman to output progress EVEN while piped! how crazy is that guys
        process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            # parse percentage
            pct_match = re.search(r'(\d+)%', line)
            if pct_match:
                current_pct = int(pct_match.group(1))
            
            # parse status keywords
            keys = ["cloning", "building", "installing", "checking", "downloading"]
            if any(k in line.lower() for k in keys):
                current_status = line.strip().split('::')[-1].split('..')[0].strip()

            draw_poli_ui(current_status, current_pct, start_time)

        process.wait()
        # clear the lines when it's done
        sys.stdout.write(f"\r\033[K\n\r\033[K\033[A{SHOW_CURSOR}")
        
        if process.returncode == 0:
            total_time = int(time.time() - start_time)
            print(f"\n{GREEN}✅ {success_msg} ({total_time}s){RESET}")
      else:
            # --- ERROR DISPLAY SECTION ---
            print(f"\n{RED}{BOLD}[!] Assembly failed!{RESET}")
            print(f"{YELLOW}I couldn't install the package. Here's the last thing I saw:{RESET}")
            print("-" * 40)
            # Show the last 5 lines of the error log to avoid flooding the screen
            for err_line in error_log[-5:]:
                print(f" {RED}»{RESET} {err_line.strip()}")
            print("-" * 40)
            print(f"{CYAN}Tip:{RESET} Check your internet or if the package name is correct.")    except KeyboardInterrupt:
        print(f"\n{SHOW_CURSOR}{BOLD}[!] Stopped.{RESET}")

def main():
    if len(sys.argv) < 2:
        show_help()
        return

    action = sys.argv[1]
    if action == "install":
        run_poli_process(["-S"] + sys.argv[2:], "Your package is ready!", is_install=True)
    elif action == "update":
        # New: Check news BEFORE starting the update process
        if check_arch_news():
            print(f"{CYAN}Checking your system for orphans...{RESET}")
            run_poli_process(["-Syu"], "System up to date!")
            # Check for orphans after
            orphans = subprocess.run(["pacman", "-Qqdt"], capture_output=True, text=True).stdout
            if orphans:
                print(f"\n{YELLOW}I found unused packages (orphans). Run 'poli orphans' to find them a home.{RESET}")
        else:
            print(f"{YELLOW}Update cancelled, so you can check the news.{RESET}")t if needed.")
    elif action == "orphans":
        subprocess.run("sudo pacman -Rs $(pacman -Qqdt)", shell=True)
    else:
        show_help()

if __name__ == "__main__":
    main()
