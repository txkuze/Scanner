#!/bin/bash

echo "Starting Vulnerability Scanner Bot..."
echo ""

if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your credentials."
    exit 1
fi

if ! command -v nmap &> /dev/null; then
    echo "Warning: nmap is not installed!"
    echo "Please install nmap: sudo apt install nmap"
    exit 1
fi

if [ ! -d "reports" ]; then
    mkdir reports
fi

python3 main.py
