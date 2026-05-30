#!/bin/bash
echo -ne '\033]0;MS-NUKER v1.0.0\007'
clear

# Request root privileges
if [ "$EUID" -ne 0 ]; then
    echo "  [!] Requesting root privileges..."
    sudo "$0" "$@"
    exit $?
fi

if [ -f "dist/MS-NUKER" ]; then
    echo "  [+] Launching MS-NUKER (compiled)..."
    ./dist/MS-NUKER
else
    echo "  [*] Compiled build not found, running from source..."
    python3 main.py
fi
