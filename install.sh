#!/bin/bash

# Define colors for the conversational tone
CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
RESET='\033[0m'
BOLD='\033[1m'

echo -e "${CYAN}${BOLD}Installing poli-cli...${RESET}"

# 1. Check if the package directory exists
if [[ ! -d "poli" ]] || [[ ! -f "poli/__init__.py" ]]; then
    echo -e "${RED}[!] The poli package isn't here. Try and clone the repository again.${RESET}"
    exit 1
fi

# 2. Install the package to /usr/local/lib
echo -e "${CYAN}Installing poli package to /usr/local/lib...${RESET}"
sudo rm -rf /usr/local/lib/poli
sudo cp -r poli /usr/local/lib/poli

# 3. Create the executable shim in /usr/local/bin
echo -e "${CYAN}Creating poli command...${RESET}"
sudo tee /usr/local/bin/poli > /dev/null << 'EOF'
#!/usr/bin/env bash
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}/usr/local/lib"
exec python3 -m poli "$@"
EOF
sudo chmod +x /usr/local/bin/poli

# 4. Final Verification
if [[ -f "/usr/local/bin/poli" ]] && [[ -f "/usr/local/lib/poli/__main__.py" ]]; then
    echo -e "\n${GREEN}${BOLD}✅ Assembly complete!${RESET}"
    echo -e "You can now run me by simply typing ${CYAN}poli${RESET} in your terminal."
    echo -e "Try ${CYAN}poli update${RESET} to get started."
else
    echo -e "${RED}[!] Something went wrong during the copy process.${RESET}"
    exit 1
fi
