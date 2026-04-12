#!/bin/bash
CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
YELLOW='\033[33m'
RESET='\033[0m'
BOLD='\033[1m'

cd "$(dirname "$0")" || exit

echo -e "${CYAN}${BOLD}Installing poli...${RESET}"

if [[ ! -f "poli.py" ]]; then
    echo -e "${RED}[!] Error: 'poli.py' not found in $(pwd)${RESET}"
    exit 1
fi

echo -e "${CYAN}Checking requirements...${RESET}"
REQS=("python3" "git" "sudo" "pacman")
for req in "${REQS[@]}"; do
    if ! command -v "$req" &> /dev/null; then
        echo -e "${RED}[!] Error: '$req' is not installed.${RESET}"
        exit 1
    fi
done

chmod +x poli.py
echo -e "${CYAN}Moving poli to /usr/local/bin...${RESET}"
sudo cp poli.py /usr/local/bin/poli

if [[ -f "/usr/local/bin/poli" ]]; then
    echo -e "\n${GREEN}${BOLD}✅ Assembly complete!${RESET}"
    echo -e "You can now run the tool by typing ${CYAN}poli${RESET}"
else
    echo -e "${RED}[!] Copy failed. Check permissions.${RESET}"
    exit 1
fi