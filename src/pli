#!/usr/bin/env python3
import sys
import subprocess
import os
import re
import shutil
import itertools
import time

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

def check_lock():
    if os.path.isfile("/var/lib/pacman/db.lck"):
        print(f"{YELLOW}[!] Stop! Poli's locked by something else. Try and check if any pacman processes are being used. If you're sure there aren't, remove the db.lck file with "rm /var/lib/pacman/db.lck"{RESET}")
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
    check_lock()
    full_cmd = ["sudo", "pacman", "--noconfirm"] + command
    
    if is_install and not get_package_info(command[1:]): return

    sys.stdout.write(HIDE_CURSOR)
    start_time = time.time()
    current_pct = 0
    current_status = "Starting..."

    try:
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
            print(f"\n{RED}{BOLD}[!] Assembly Failed{RESET}")
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
        run_poli_process(["-Syu"], "Your system has been updated, remember to restart if needed.")
    elif action == "orphans":
        subprocess.run("sudo pacman -Rs $(pacman -Qqdt)", shell=True)
    else:
        show_help()

if __name__ == "__main__":
    main()
