#!/bin/bash
CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
RESET='\033[0m'
BOLD='\033[1m'
echo -e "${CYAN}${BOLD}Installing poli for the first time...${RESET}"

if [[ ! -f "poli.py" ]]; then
    echo -e "${RED}[!] The script's not here. Try and clone the repository again.${RESET}"
    exit 1
fi

chmod +x poli.py

echo -e "${CYAN}Moving poli to /usr/local/bin...${RESET}"
sudo cp -r poli.py /usr/local/bin/poli


if [[ -f "/usr/local/bin/poli" ]]; then
    echo -e "\n${GREEN}${BOLD}✅ Assembly complete!${RESET}"
    echo -e "You can now run me by simply typing ${CYAN}poli${RESET} in your terminal."
    echo -e "Try ${CYAN}poli update${RESET} to get started."
else
    echo -e "${RED}[!] Something went wrong during the copy process.${RESET}"
    exit 1
fi
