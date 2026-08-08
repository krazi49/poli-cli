# poli-cli

An apt-like pacman wrapper for Arch Linux with AUR support. Pure Python.

This project was made for people who prefer apt, but don't want to deal with the endless garbled letters that go after "pacman". It combines the large library of the AUR, with the simple commands of apt.

## Features

- Live progress bar with ETA during installs
- AUR dependency resolution and auto-build
- `why` — find which package owns a file
- `tree` — dependency tree visualization
- `stats` — system package statistics
- `check` — verify package integrity
- `log` — recent package operations
- Orphan cleanup, reinstall, download-only, and more

## Commands

poli uses apt-like commands. Factory names on the left, canonical names in parens:

| Command | Description |
|---------|-------------|
| `assemble` (`get`) | Install packages from repos or AUR |
| `catalog` (`search`) | Search packages across all repos |
| `maintain` (`update`) | Full system upgrade |
| `disassemble` (`remove`) | Remove packages and orphans |
| `blueprint` (`info`) | Show detailed package info |
| `reforge` (`reinstall`) | Force rebuild and reinstall |
| `why` | Which package owns a file? |
| `tree` | Dependency tree for a package |
| `fetch` (`download`) | Download without installing |
| `audit` (`check`) | Verify package integrity |
| `floorplan` (`stats`) | System package statistics |
| `scrapheap` (`orphans`) | Clean up unused deps |
| `history` (`log`) | Recent package operations |

### Examples

```bash
poli assemble neovim          # install neovim
poli catalog 'web browser'    # search for browsers
poli why /usr/bin/nvim        # which package owns this?
poli tree neovim              # show dependency tree
poli maintain                 # full system upgrade
poli floorplan                # system stats
```

## Installation

### From source

```bash
git clone https://github.com/krazi49/poli-cli.git
cd poli-cli
chmod +x install.sh
./install.sh
```

### From AUR

Once published: `poli assemble poli-cli`

## Development

The package lives in `poli/`:

```
poli/
├── __init__.py    # version
├── __main__.py    # entrypoint
├── cli.py         # argument routing & dispatch
├── aur.py         # AUR RPC + dep resolution
├── pacman.py      # pacman wrapper + AUR builds
├── display.py     # colors, progress bar, tables
├── config.py      # config loading
├── stats.py       # system stats & diagnostics
├── tree.py        # dependency tree
└── why.py         # file → package ownership
```

## License

MIT
