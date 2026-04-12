# poli-cli
poli-cli is a powerful, minimalist `pacman` wrapper for Arch and Arch-based distributions written in pure Python. 

## Key features

### Hybrid repository support
poli automatically detects if a package is in the official repositories or the AUR. You no longer need to switch between `pacman` and a separate AUR helper.

### AUR solver
Unlike simple wrappers, **poli** can solve complex dependency trees. If an AUR package depends on another AUR package, poli will map the entire chain and build them in the correct logical order.

### APT parity
poli mirrors the behavior of the apt package manager while keeping some pacman functionality.
- Works as `poli`.
- Supports `get`, `update`, `search`, and `orphans` aliases.

## Commands

`poli get <pkg>`
**Assemble** Fetches and installs a package with a live terminal UI and ETA. If the package isn't in official repos, it automatically switches to AUR mode.

`poli update`
**System update** Performs a full system upgrade (`-Syu`) and then automatically scans your installed AUR packages for available updates.

`poli search <term>`
**Find and install** Searches both the official repositories and the AUR. AUR results are highlighted for clarity.

`poli remove <pkg>`
**Disassemble** Uninstalls a package and removes its dependencies.

`poli orphans`
**De-bloat** Lists and removes unused dependencies to keep your system lean and fast.

`poli help`
**Assembly manual** Displays the built-in help menu with a full list of actions and usage examples.

## Installation

### Manually
Run:
```bash
git clone https://github.com/krazi49/poli-cli.git
cd poli-cli
chmod +x install.sh
./install.sh
```

### Quickly
Paste:
```bash
curl -sO https://raw.githubusercontent.com/krazi49/poli-cli/main/install.sh && chmod +x install.sh && ./install.sh
```
and press enter.