#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -f "venv/bin/python" ]; then
    echo "Virtual environment not found. Setting up..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python downloader_cli.py
