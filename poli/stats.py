"""System package statistics and diagnostics."""
import re
import subprocess
from .display import CYAN, GREEN, YELLOW, RED, MAGENTA, BOLD, RESET


def _to_bytes(val, unit):
    return val * {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3}.get(unit, 0)


def _pacman_q(flag):
    r = subprocess.run(["pacman", "-Q", flag, "--color", "never"], capture_output=True, text=True)
    return [l for l in r.stdout.strip().split("\n") if l]


def cmd_stats():
    """Show system package statistics."""
    try:
        total = _pacman_q("")
        explicit = _pacman_q("-e")
        deps = _pacman_q("-d")
        aur_lines = _pacman_q("-m")

        total_count = len(total)
        explicit_count = len(explicit)
        dep_count = len(deps)
        aur_count = len(aur_lines)

        size_result = subprocess.run(["pacman", "-Qi", "--color", "never"], capture_output=True, text=True)
        total_size = 0
        for line in size_result.stdout.split("\n"):
            m = re.search(r"Installed Size\s*:\s*([\d.]+)\s*(\w+)", line)
            if m:
                total_size += _to_bytes(float(m.group(1)), m.group(2))

        size_gb = total_size / (1024**3)
        size_mb = total_size / (1024**2)

        print(f"{BOLD}{'=' * 40}{RESET}")
        print(f"{BOLD}  📊 poli system stats{RESET}")
        print(f"{BOLD}{'=' * 40}{RESET}")
        print(f"  {CYAN}Total packages{RESET}      : {total_count}")
        print(f"  {GREEN}Explicitly installed{RESET} : {explicit_count}")
        print(f"  {YELLOW}Dependencies{RESET}        : {dep_count}")
        print(f"  {MAGENTA}AUR packages{RESET}        : {aur_count}")
        print(f"  {CYAN}Total size{RESET}           : {size_gb:.2f} GiB ({size_mb:.1f} MiB)")

        if total_count > 0:
            print(f"\n{BOLD}  Top 5 largest packages:{RESET}")
            pkgs = []
            cur_name, cur_size, cur_unit = None, 0, ""
            for line in size_result.stdout.split("\n"):
                n = re.match(r"Name\s*:\s*(.+)", line)
                if n:
                    if cur_name and cur_size > 0:
                        pkgs.append((cur_size, cur_unit, cur_name))
                    cur_name = n.group(1).strip()
                    cur_size = 0
                m = re.search(r"Installed Size\s*:\s*([\d.]+)\s*(\w+)", line)
                if m and cur_name:
                    cur_size, cur_unit = float(m.group(1)), m.group(2)
            if cur_name and cur_size > 0:
                pkgs.append((cur_size, cur_unit, cur_name))

            pkgs.sort(key=lambda x: _to_bytes(x[0], x[1]), reverse=True)
            for size_val, unit, name in pkgs[:5]:
                print(f"    {YELLOW}{size_val:.1f} {unit}{RESET}  {name}")

        if aur_lines:
            print(f"\n{BOLD}  AUR packages:{RESET}")
            for line in aur_lines[:10]:
                parts = line.split()
                if parts:
                    print(f"    {MAGENTA}{parts[0]}{RESET}")
            if len(aur_lines) > 10:
                print(f"    ... and {len(aur_lines) - 10} more")

        print()
    except Exception as e:
        from .display import log_error
        log_error(f"Failed to gather stats: {e}")


def cmd_check():
    """Verify system package integrity."""
    from .display import CYAN, GREEN, YELLOW
    print(f"{CYAN}Checking package integrity...{RESET}")
    result = subprocess.run(["pacman", "-Dk"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{GREEN}✅ All dependencies satisfied. System is healthy.{RESET}")
    else:
        for line in result.stdout.split("\n") + result.stderr.split("\n"):
            if line.strip():
                print(line)


def cmd_log(n=20):
    """Show last n pacman operations from the log."""
    import os
    pacman_log = "/var/log/pacman.log"
    if not os.path.exists(pacman_log):
        print(f"{RED}[!] {pacman_log} not found.{RESET}")
        return

    try:
        with open(pacman_log, "r") as f:
            lines = f.readlines()
    except PermissionError:
        print(f"{RED}[!] Permission denied. Try: sudo poli log{RESET}")
        return

    action_lines = []
    for line in reversed(lines):
        if any(k in line for k in [" installed ", " upgraded ", " removed "]):
            action_lines.append(line.strip())
            if len(action_lines) >= n:
                break

    if not action_lines:
        print(f"{YELLOW}No recent package operations found.{RESET}")
        return

    print(f"{BOLD}Last {len(action_lines)} package operations:{RESET}\n")
    for line in reversed(action_lines):
        match = re.match(r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})\]", line)
        if match:
            for action_word, colour in [
                ("installed ", f"{GREEN}installed{RESET} "),
                ("upgraded ", f"{YELLOW}upgraded{RESET} "),
                ("removed ", f"{RED}removed{RESET} "),
            ]:
                if action_word in line:
                    disp = line.replace(action_word.strip(), colour.strip())
                    disp = disp.replace(f"[{match.group(1)}", f"[{CYAN}{match.group(1)}{RESET}")
                    print(f"  {disp}")
                    break
        else:
            print(f"  {line}")
