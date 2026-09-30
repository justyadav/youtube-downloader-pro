#!/usr/bin/env bash
set -e

# Change directory to script directory
cd "$(dirname "$0")"

echo "========================================================"
echo "       Starting YouTube Downloader Pro (Web GUI)"
echo "========================================================"
echo ""

if [ ! -f "venv/bin/python" ]; then
    echo "Virtual environment not found. Setting up..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python server.py
