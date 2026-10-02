<div align="center">

# 🎬 YouTube Downloader Pro

**A modern, production-ready YouTube video & audio downloader with real-time progress, batch processing, and bundled FFmpeg support.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![yt-dlp](https://img.shields.io/badge/Powered%20By-yt--dlp-red.svg)](https://github.com/yt-dlp/yt-dlp)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

[Features](#-key-features) • [Quick Start](#-quick-start) • [Download Modes](#-download-options--modes) • [Docker](#-docker-setup) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## ✨ Key Features

- 🔄 **Auto Mode**: Automatically selects and merges the best available video + audio stream.
- 🎬 **Both (Merged)**: Merges ultra-high-definition video (up to 4K) and high-bitrate audio into clean `.mp4` containers using FFmpeg.
- 🎥 **Video Only**: Extracts video stream without audio (ideal for video editors and B-roll creators).
- 🎵 **Audio Only (MP3)**: Extracts high-fidelity 192 kbps audio directly to `.mp3`.
- 📺 **Resolution Target**: Supports **Best**, **4K (2160p)**, **2K (1440p)**, **1080p FHD**, **720p HD**, **480p**, and **360p**.
- ⚡ **Mass & Playlist Download**:
  - Paste dozens of URLs simultaneously (separated by line breaks or commas).
  - Full YouTube Playlist parsing.
  - One-click import from `.txt` list files.
- 📊 **Real-Time Progress Tracking**: Live percentage, download speed (MB/s), ETA countdown, and file sizes streamed via Server-Sent Events (SSE).
- 📁 **Native OS Integration**: One-click "Open Downloads" button reveals your files directly in Windows Explorer, macOS Finder, or Linux file manager.
- 🎨 **Modern Dark Web UI + Interactive CLI**: Enjoy a polished glassmorphism web dashboard or an interactive terminal CLI.
- 📦 **Zero-Config FFmpeg**: Automatically utilizes system FFmpeg or bundles static FFmpeg so no manual system PATH editing is required.

---

## 🚀 Quick Start

### Windows (1-Click)
1. Clone or download this repository:
   ```cmd
   git clone https://github.com/justyadav/youtube-downloader-pro.git
   cd youtube-downloader-pro
   ```
2. Double-click **`run_downloader.bat`** (for Web GUI) or **`run_cli.bat`** (for Terminal).
3. The Web UI will automatically launch in your browser at `http://localhost:8000`.

---

### macOS & Linux
```bash
git clone https://github.com/justyadav/youtube-downloader-pro.git
cd youtube-downloader-pro

# Make scripts executable
chmod +x run_downloader.sh run_cli.sh

# Run Web GUI
./run_downloader.sh

# Or run interactive CLI
./run_cli.sh
```

---

### Manual Python Setup (Any Platform)
```bash
# 1. Create and activate a virtual environment
python3 -m venv venv

# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the Web App
python server.py

# Or start the CLI
python downloader_cli.py
```

---

## 🎛️ Download Options & Modes

| Option | Description | Output Format |
| :--- | :--- | :--- |
| **`Auto`** | Best video & audio stream combined without configuration | `.mp4` |
| **`Both`** | Merges target resolution video track + crisp audio stream | `.mp4` |
| **`Video`** | Pure video stream without sound | `.mp4` / `.mkv` |
| **`Audio`** | Extracts high-fidelity audio track | `.mp3` (192kbps) |
| **`Quality`** | Select resolution: Best, 2160p (4K), 1440p (2K), 1080p, 720p, 480p, 360p | Respective video |
| **`Mass Download`**| Download multiple URLs, channels, or full playlists in batch | Batch |

---

## 🐳 Docker Setup

Run YouTube Downloader Pro anywhere with Docker:

```bash
# Using docker-compose (Recommended)
docker compose up -d

# Access the Web Dashboard at http://localhost:8000
# Downloaded videos will be saved into the ./downloads directory on your host machine.
```

Or build manually:
```bash
docker build -t youtube-downloader-pro .
docker run -d -p 8000:8000 -v $(pwd)/downloads:/downloads youtube-downloader-pro
```

---

## 📂 Project Architecture

```text
youtube-downloader-pro/
├── .github/
│   ├── workflows/ci.yml           # Cross-platform GitHub Actions CI
│   └── ISSUE_TEMPLATE/            # Bug report & feature templates
├── downloader_core.py             # Download engine (yt-dlp, FFmpeg detection)
├── server.py                      # FastAPI server with SSE real-time events
├── downloader_cli.py              # Colorized interactive terminal CLI
├── index.html                     # Responsive dark-theme Web GUI
├── Dockerfile                     # Container definition
├── docker-compose.yml             # 1-command Docker deployment
├── pyproject.toml                 # Standard Python packaging (PEP 518/621)
├── requirements.txt               # Pinned dependencies
├── run_downloader.bat             # 1-Click Windows Web Launcher
├── run_cli.bat                    # 1-Click Windows CLI Launcher
├── run_downloader.sh              # 1-Click Linux/macOS Web Launcher
├── run_cli.sh                     # 1-Click Linux/macOS CLI Launcher
├── sample_urls.txt                # Example mass download file
├── CONTRIBUTING.md                # Contribution guidelines
├── SECURITY.md                    # Security policy
└── LICENSE                        # MIT License
```

---

## ⚖️ Disclaimer

This software is developed for personal, educational, and archival purposes. Please respect copyright laws and the terms of service of any platform from which you download content. The authors and contributors assume no liability for misuse of this tool.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
