"""Pacman wrapper with clean progress display and AUR build support."""
import os
import re
import shutil
import subprocess
import sys
import time
from .display import (
    log_error, ProgressBar, CYAN, GREEN, YELLOW, RED, BOLD, RESET,
)
from .aur import resolve_deps, get_aur_info
from .config import load


"""Pacman wrapper with clean progress display and AUR build support."""
import os
import pty
import re
import select
import shutil
import subprocess
import sys
import time
from .display import (
    log_error, ProgressBar, CYAN, GREEN, YELLOW, RED, BOLD, RESET,
)
from .aur import resolve_deps, get_aur_info, aur_upgrade
from .config import load


class PacmanStreamParser:
    """Parses incoming pacman output from PTY to update progress and emit terminal logs."""

    def __init__(self, progress_bar):
        self.prog = progress_bar
        self.buffer = ""

    def feed(self, data):
        self.buffer += data
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            self._process_line(line, is_complete=True)
        if self.buffer:
            self._process_line(self.buffer, is_complete=False)

    def flush(self):
        if self.buffer:
            self._process_line(self.buffer, is_complete=True)
            self.buffer = ""

    def _process_line(self, line, is_complete=False):
        if "\r" in line:
            parts = line.split("\r")
            for part in parts:
                self._parse_progress(part)
        else:
            self._parse_progress(line)

        if is_complete:
            cleaned = self._clean_line(line)
            if cleaned:
                self.prog.print_log(f"  {cleaned}\n")

    def _parse_progress(self, text):
        pct = None
        m = re.search(r"(\d+)%", text)
        if m:
            pct = int(m.group(1))

        status = text
        status = re.sub(r"\s*\[[#=\-·\s\u00b7]*\]\s*", " ", status)
        status = re.sub(r"\s*\d+%\s*", " ", status)
        status = status.strip()

        if status or pct is not None:
            self.prog.update(pct=pct, status=status if status else None)

    def _clean_line(self, line):
        if "\r" in line:
            line = line.split("\r")[-1]
        line = line.strip()
        if not line:
            return None

        cleaned = re.sub(r"\s*\[[#=\-·\s\u00b7]*\]\s*", " ", line)
        cleaned = re.sub(r"\s*\d+%\s*", " ", cleaned)
        cleaned = cleaned.strip()

        return cleaned if cleaned else None


def run_pacman(command, success_msg):
    """Run pacman with live progress and terminal log output via PTY."""
    prog = ProgressBar()
    prog.start()
    parser = PacmanStreamParser(prog)

    try:
        master_fd, slave_fd = pty.openpty()
        proc = subprocess.Popen(
            ["sudo", "pacman", "--noconfirm"] + command,
            stdout=slave_fd, stderr=slave_fd, text=True,
        )
        os.close(slave_fd)

        deadline = time.time() + 600

        while True:
            r, _, _ = select.select([master_fd], [], [], 0.1)
            if master_fd in r:
                try:
                    data = os.read(master_fd, 4096).decode("utf-8", errors="replace")
                except OSError:
                    break
                if not data:
                    break
                parser.feed(data)
            else:
                if proc.poll() is not None:
                    break
                if time.time() > deadline:
                    log_error("pacman timed out")
                    proc.kill()
                    break

        try:
            while True:
                r, _, _ = select.select([master_fd], [], [], 0.05)
                if master_fd in r:
                    data = os.read(master_fd, 4096).decode("utf-8", errors="replace")
                    if not data:
                        break
                    parser.feed(data)
                else:
                    break
        except OSError:
            pass

        parser.flush()
        proc.wait()
        os.close(master_fd)

        prog.finish(success_msg if proc.returncode == 0 else None)
        if proc.returncode != 0:
            log_error(f"pacman exited with code {proc.returncode}")
    except Exception as e:
        log_error(f"pacman error: {e}")
    finally:
        sys.stderr.write("\033[?25h")
        sys.stderr.flush()


def build_aur(pkg_name):
    """Clone, build, and install an AUR package."""
    build_dir = f"/tmp/poli_{pkg_name}"
    try:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        subprocess.run(
            ["git", "clone", "--quiet", f"https://aur.archlinux.org/{pkg_name}.git", build_dir],
            check=True, capture_output=True,
        )
        if os.geteuid() == 0 and "SUDO_USER" in os.environ:
            subprocess.run(
                ["sudo", "-u", os.environ["SUDO_USER"], "makepkg", "-sirc", "--noconfirm"],
                cwd=build_dir, check=True,
            )
        else:
            subprocess.run(["makepkg", "-sirc", "--noconfirm"], cwd=build_dir, check=True)
        print(f"{GREEN}✅ {pkg_name} built and installed.{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}❌ Failed to build {pkg_name}{RESET}")
    finally:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)


def install_package(pkg_name):
    """Install from official repos or resolve AUR deps and build."""
    if subprocess.run(["pacman", "-Si", pkg_name], capture_output=True).returncode == 0:
        run_pacman(["-S", pkg_name], f"{pkg_name} assembled.")
        return

    cfg = load()
    print(f"{CYAN}🔍 Solving AUR dependencies for {BOLD}{pkg_name}{RESET}...")
    queue = resolve_deps(pkg_name, depth_limit=cfg.get("aur_depth_limit", 10))

    if not queue:
        print(f"{RED}[!] Could not find {pkg_name} anywhere.{RESET}")
        return

    print(f"{YELLOW}Assembly order: {' → '.join(queue)}{RESET}")
    for target in queue:
        build_aur(target)


def download_package(pkg_names):
    """Download packages without installing."""
    for pkg in pkg_names:
        run_pacman(["-Sw", pkg], f"{pkg} downloaded.")


def reinstall_package(pkg_names):
    """Force reinstall — rebuild AUR packages from source."""
    for pkg in pkg_names:
        if subprocess.run(["pacman", "-Qi", pkg], capture_output=True).returncode != 0:
            print(f"{YELLOW}⚠ {pkg} not installed — installing fresh.{RESET}")
            install_package(pkg)
            continue
        if subprocess.run(["pacman", "-Si", pkg], capture_output=True).returncode == 0:
            run_pacman(["-S", pkg], f"{pkg} reinstalled.")
        else:
            print(f"{CYAN}🔍 Rebuilding AUR package {BOLD}{pkg}{RESET}...")
            build_aur(pkg)


def remove_packages(pkg_names):
    """Remove packages and unused dependencies."""
    run_pacman(["-Rs"] + pkg_names, "Packages disassembled.")


def remove_orphans():
    """Remove orphaned packages."""
    orphans = subprocess.run(
        ["pacman", "-Qqdt"], capture_output=True, text=True
    ).stdout.strip()
    if orphans:
        run_pacman(["-Rs"] + orphans.split(), "System cleaned.")
    else:
        print(f"{GREEN}No orphans found. System is lean.{RESET}")


def upgrade_system(pkg_names=None):
    """Full system upgrade, optionally specific packages."""
    if pkg_names:
        for p in pkg_names:
            install_package(p)
    else:
        run_pacman(["-Syu"], "System updated.")
        updates = aur_upgrade()
        for u in updates:
            install_package(u)
