#!/bin/bash

# Define colors for the conversational tone
CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
RESET='\033[0m'
BOLD='\033[1m'

echo -e "${CYAN}${BOLD}Installing poli-cli for the first time...${RESET}"

# 1. Check if the main script exists
if [[ ! -f "poli.py" ]]; then
    echo -e "${RED}[!] The script's not here. Try and clone the repository again.${RESET}"
    exit 1
fi

# 2. Make the python script executable
chmod +x poli.py

# 3. Copy to /usr/local/bin
echo -e "${CYAN}Moving poli to /usr/local/bin...${RESET}"
sudo cp poli.py /usr/local/bin/poli

# 4. Final Verification
if [[ -f "/usr/local/bin/poli" ]]; then
    echo -e "\n${GREEN}${BOLD}✅ Assembly complete!${RESET}"
    echo -e "You can now run me by simply typing ${CYAN}poli${RESET} in your terminal."
    echo -e "Try ${CYAN}poli update${RESET} to get started."
else
    echo -e "${RED}[!] Something went wrong during the copy process.${RESET}"
    exit 1
fi
