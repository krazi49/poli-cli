# poli-cli

pacman wrapper made entirely with python

now, you can talk to pacman like you do apt, `poli` comes with aliases and a search tool, built to help you install packages faster. not that you weren't fast with yay or paru anyway

## it comes with

- eta and progress bar
- dependency resolution from the aur + aur support
- dependency tree visualization through `tree`
- system package statistics through `stats`
- verify package integrity with `check`
- and a `log` of recent package operations
- you can also clean up orphans, reinstall packages, and more below

## how do i use it?

same structure as apt, `poli + [command] + (package)`, 
so to install neovim, you'd
`poli assemble neovim`

| command | what it does |
|---------|-------------|
| `assemble` (`get`) | install packages from repos the aur |
| `catalog` (`search`) | search packages across everything |
| `maintain` (`update`) | updates everything |
| `disassemble` (`remove`) | gets rid of packages and orphans |
| `blueprint` (`info`) | detailed info on a package |
| `reforge` (`reinstall`) | force rebuild and install |
| `why` | see which packages own this package |
| `tree` | dependency trees for a package |
| `fetch` (`download`) | download without installing |
| `audit` (`check`) | verify package integrity |
| `floorplan` (`stats`) | system package statistics |
| `scrapheap` (`orphans`) | clean up unused deps |
| `history` (`log`) | see recent package operations |

### more examples...

```bash
poli catalog 'web browser'    # search for browsers
poli why /usr/bin/nvim        # which package owns this?
poli tree neovim              # show dependency tree
poli maintain                 # full system upgrade
poli floorplan                # system stats
```

## to install it, just do this

```bash
git clone https://github.com/krazi49/poli-cli.git
cd poli-cli
chmod +x install.sh
./install.sh
```

## development, if you care enough

whole thing's in `poli/`, like this:

```
poli/
├── __init__.py
├── __main__.py
├── cli.py
├── aur.py
├── pacman.py
├── display.py
├── config.py
├── stats.py
├── tree.py
└── why.py
```

## license

MIT
