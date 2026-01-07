# poli-cli
poli-cli is a pacman wrapper for Arch Linux. What sets this apart from other wrappers is that this is pure Python.

This project was made for people who prefer apt, but don't want to deal with the endless garbled letters that go after "pacman". It combines the large library of the AUR, with the simple commands of apt.

 - Adds a triple-line UI, made up of a spinner, a bar and the status
 - Adds a safety net for low-end, low storage computers with a bold red download string if the package exceeds 500MB
 - Adds a feature that tells you if orphaned packages are installed, and a command to remove them simpler than pacman
 - Checks the archlinux.org page for news on packages that need manual intervention before a system update
 - Has a "verbose mode" for people who need to see all information

poli uses apt-like commands seen below:

`poli install <pkg>`
**Assemble**
Fetches and installs a package with live ETA.

`poli update`
**Update packages on your PC**
Checks Arch News for any needed upgrades, finds orphaned packages and updates system.

`poli search <term>`
**Find and install**
Interactive search with selection.

`poli orphans`
**Remove orphans**
Lists and removes unused dependencies to save space.

`poli --verbose`
**Debug**
Bypasses the UI to show raw `pacman` output.

### Installation
Install  poli-cli easily in your terminal with an install script.
``git clone https://github.com/krazi49/poli-cli.git``
``cd poli-cli``
``chmod +x install.sh``
``./install.sh``

Or, if you want a quick one-line command, use this:
``bash curl -sO [https://raw.githubusercontent.com/krazi49/poli-cli/main/install.sh](https://raw.githubusercontent.com/krazi49/poli-cli/main/install.sh) && chmod +x install.sh && ./install.sh``
