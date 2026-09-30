import os
import sys
import time
from typing import List
import downloader_core

# Terminal ANSI colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner():
    banner = f"""
{RED}{BOLD}=======================================================
          YOUTUBE DOWNLOADER PRO (CLI)
======================================================={RESET}
{CYAN}Options: Auto • Video • Both • Quality • Mass Download{RESET}
FFmpeg: {downloader_core.FFMPEG_PATH}
Default Directory: {downloader_core.get_default_download_dir()}
-------------------------------------------------------
"""
    print(banner)

def get_urls() -> List[str]:
    print(f"\n{BOLD}[1] Enter YouTube URLs:{RESET}")
    print(" - Single URL: https://www.youtube.com/watch?v=...")
    print(" - Multiple URLs: separated by commas or spaces")
    print(" - Mass Download from File: enter path like 'urls.txt'")
    print(" - Playlist: enter playlist link")
    user_input = input(f"{YELLOW}URL(s) or file path: {RESET}").strip()

    if not user_input:
        print(f"{RED}No input provided. Exiting.{RESET}")
        sys.exit(1)

    urls = []
    if os.path.exists(user_input) and os.path.isfile(user_input):
        print(f"{CYAN}Reading URLs from file: {user_input}{RESET}")
        with open(user_input, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        # Check comma or space separated
        urls = [u.strip() for u in user_input.replace(',', ' ').split() if u.strip()]

    print(f"{GREEN}Identified {len(urls)} target URL(s).{RESET}")
    return urls

def get_mode() -> str:
    print(f"\n{BOLD}[2] Select Download Mode:{RESET}")
    print(" 1) Auto  (Best video + audio combined)")
    print(" 2) Both  (High-Res Video + Audio merged into MP4)")
    print(" 3) Video (Video only stream, no audio)")
    print(" 4) Audio (Audio only, converted to MP3 192k)")
    choice = input(f"{YELLOW}Select mode [1-4, default=1]: {RESET}").strip()
    mapping = {
        '1': 'auto',
        '2': 'both',
        '3': 'video',
        '4': 'audio'
    }
    mode = mapping.get(choice, 'auto')
    print(f"{GREEN}Selected Mode: {mode.upper()}{RESET}")
    return mode

def get_quality(mode: str) -> str:
    if mode == 'audio':
        return 'best'

    print(f"\n{BOLD}[3] Select Quality Target:{RESET}")
    print(" 1) Best (Highest available resolution)")
    print(" 2) 2160p (4K UHD)")
    print(" 3) 1440p (2K QHD)")
    print(" 4) 1080p (Full HD)")
    print(" 5) 720p  (HD)")
    print(" 6) 480p  (SD)")
    print(" 7) 360p  (Low)")
    choice = input(f"{YELLOW}Select quality [1-7, default=1]: {RESET}").strip()
    mapping = {
        '1': 'best',
        '2': '2160',
        '3': '1440',
        '4': '1080',
        '5': '720',
        '6': '480',
        '7': '360'
    }
    q = mapping.get(choice, 'best')
    print(f"{GREEN}Selected Quality: {q}{RESET}")
    return q

def get_output_dir() -> str:
    default_dir = downloader_core.get_default_download_dir()
    print(f"\n{BOLD}[4] Save Directory:{RESET}")
    print(f" Default: {default_dir}")
    custom = input(f"{YELLOW}Press ENTER for default or enter custom path: {RESET}").strip()
    if custom:
        os.makedirs(custom, exist_ok=True)
        return custom
    return default_dir

def cli_progress(update: dict):
    status = update.get('status')
    if status == 'downloading':
        title = update.get('title', '')
        pct = update.get('percent', 0.0)
        speed = update.get('speed', '--')
        eta = update.get('eta', '--')
        size = update.get('size', '')
        sys.stdout.write(f"\r{CYAN}[{pct:5.1f}%]{RESET} {size} | Speed: {speed} | ETA: {eta}   ")
        sys.stdout.flush()
    elif status == 'processing':
        sys.stdout.write(f"\r{YELLOW}[Processing]{RESET} Merging video and audio with FFmpeg...    \n")
        sys.stdout.flush()
    elif status == 'fetching_info':
        title = update.get('title', '')
        print(f"\n{YELLOW}{title}{RESET}")

def main():
    # Enable ANSI escape sequences on Windows
    os.system("")
    print_banner()

    urls = get_urls()
    mode = get_mode()
    quality = get_quality(mode)
    output_dir = get_output_dir()

    print(f"\n{BOLD}{GREEN}Starting Download Job...{RESET}\n")

    task = downloader_core.DownloadTask(
        task_id="cli_task",
        urls=urls,
        mode=mode,
        quality=quality,
        output_dir=output_dir,
        progress_callback=cli_progress
    )

    task.run()

    print(f"\n\n{BOLD}{GREEN}=========================================={RESET}")
    print(f"{BOLD}{GREEN}All Tasks Completed!{RESET}")
    print(f"Files saved in: {CYAN}{output_dir}{RESET}")
    print(f"{BOLD}{GREEN}=========================================={RESET}")

    # Ask if user wants to open the folder
    ans = input("\nOpen downloads folder in File Explorer? (y/n): ").strip().lower()
    if ans == 'y':
        if sys.platform == 'win32':
            os.startfile(output_dir)

if __name__ == "__main__":
    main()
