#!/bin/bash
set -euo pipefail

CYAN='\033[36m'; GREEN='\033[32m'; RED='\033[31m'; YELLOW='\033[33m'
BOLD='\033[1m'; RESET='\033[0m'

cd "$(dirname "$0")"

# checks
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}[!] python3 not found${RESET}"; exit 1; }
python3 -c "import sys; assert sys.version_info >= (3, 11)" 2>/dev/null || {
    echo -e "${RED}[!] python3.11+ required (got $(python3 --version))${RESET}"; exit 1;
}
command -v pacman >/dev/null 2>&1 || { echo -e "${RED}[!] pacman not found — arch only${RESET}"; exit 1; }

[[ -d poli ]] || { echo -e "${RED}[!] poli/ directory not found in $(pwd)${RESET}"; exit 1; }

echo -e "${CYAN}${BOLD}Installing poli...${RESET}"

# install package
sudo install -d /usr/local/lib/poli
sudo cp -r poli/__init__.py poli/__main__.py poli/aur.py poli/cli.py \
            poli/config.py poli/display.py poli/pacman.py poli/stats.py \
            poli/tree.py /usr/local/lib/poli/

# install wrapper
sudo tee /usr/local/bin/poli > /dev/null << 'POLI_EOF'
#!/usr/bin/env bash
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}/usr/local/lib"
exec python3 -m poli "$@"
POLI_EOF
sudo chmod 755 /usr/local/bin/poli

# config dir
mkdir -p ~/.config/poli

echo ""
echo -e "${GREEN}${BOLD}✅ poli v3.0.0 assembled.${RESET}"
echo -e "   package:  ${CYAN}/usr/local/lib/poli/${RESET}"
echo -e "   wrapper:  ${CYAN}/usr/local/bin/poli${RESET}"
echo -e "   config:   ${CYAN}~/.config/poli/${RESET}"
echo ""
echo -e "   Run ${CYAN}poli help${RESET} to get started."
