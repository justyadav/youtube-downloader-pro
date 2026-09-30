import os
import sys
import json
import argparse
import asyncio
import subprocess
import threading
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

import downloader_core

app = FastAPI(
    title="YouTube Downloader Pro",
    description="High-performance YouTube downloader with Auto, Video, Both, Audio, Quality, and Mass Download options.",
    version="1.0.0"
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_task: Optional[downloader_core.DownloadTask] = None
task_lock = threading.Lock()
subscribers = []

class DownloadRequest(BaseModel):
    urls: List[str]
    mode: str = "both"       # 'auto', 'both', 'video', 'audio'
    quality: str = "best"    # 'best', '2160', '1440', '1080', '720', '480', '360'
    output_dir: Optional[str] = None

class InfoRequest(BaseModel):
    url: str

def notify_subscribers(data: dict):
    msg = f"data: {json.dumps(data)}\n\n"
    for queue in list(subscribers):
        try:
            queue.put_nowait(msg)
        except Exception:
            pass

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/config")
def get_config():
    return {
        "default_dir": downloader_core.get_default_download_dir(),
        "ffmpeg": downloader_core.FFMPEG_PATH,
        "is_busy": current_task is not None and current_task.status in ["queued", "fetching_info", "downloading", "processing"]
    }

@app.post("/api/info")
def get_video_info(req: InfoRequest):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Empty URL provided")
    if not downloader_core.sanitize_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")

    try:
        info = downloader_core.extract_info(url, extract_flat=False)
        if 'entries' in info:
            entries = list(info['entries'])
            return {
                "type": "playlist",
                "title": info.get("title", "YouTube Playlist"),
                "count": len(entries),
                "thumbnail": entries[0].get("thumbnail") if entries else None,
                "first_title": entries[0].get("title") if entries else None,
                "urls": [e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}" for e in entries if e]
            }
        else:
            formats = info.get("formats", [])
            heights = sorted(list(set(f.get("height") for f in formats if f.get("height"))), reverse=True)
            return {
                "type": "video",
                "title": info.get("title", "Unknown Title"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown Channel"),
                "thumbnail": info.get("thumbnail"),
                "available_resolutions": heights
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/download")
def start_download(req: DownloadRequest):
    global current_task
    cleaned_urls = [u.strip() for u in req.urls if downloader_core.sanitize_url(u.strip())]
    if not cleaned_urls:
        raise HTTPException(status_code=400, detail="No valid URLs provided")

    with task_lock:
        if current_task and current_task.status in ["queued", "fetching_info", "downloading", "processing"]:
            raise HTTPException(status_code=409, detail="A download task is already running")

        task_id = str(int(asyncio.get_event_loop_policy().get_event_loop().time() * 1000))
        target_dir = os.path.abspath(req.output_dir.strip()) if req.output_dir and req.output_dir.strip() else downloader_core.get_default_download_dir()
        os.makedirs(target_dir, exist_ok=True)

        def progress_cb(update: dict):
            notify_subscribers(update)

        current_task = downloader_core.DownloadTask(
            task_id=task_id,
            urls=cleaned_urls,
            mode=req.mode,
            quality=req.quality,
            output_dir=target_dir,
            progress_callback=progress_cb
        )

        worker = threading.Thread(target=current_task.run, daemon=True)
        worker.start()

        return {"status": "started", "task_id": task_id, "total_urls": len(cleaned_urls)}

@app.post("/api/cancel")
def cancel_download():
    global current_task
    with task_lock:
        if current_task and current_task.status in ["queued", "fetching_info", "downloading", "processing"]:
            current_task.cancel()
            notify_subscribers({
                "status": "cancelled",
                "title": "Download cancelled by user"
            })
            return {"status": "cancelled"}
        return {"status": "no_active_task"}

@app.get("/api/events")
async def events():
    queue = asyncio.Queue()
    subscribers.append(queue)
    async def event_generator():
        try:
            if current_task:
                yield f"data: {json.dumps({'status': current_task.status, 'title': current_task.current_title, 'percent': current_task.current_percent, 'speed': current_task.current_speed, 'eta': current_task.current_eta, 'size': current_task.current_size})}\n\n"
            while True:
                msg = await queue.get()
                yield msg
        except asyncio.CancelledError:
            pass
        finally:
            if queue in subscribers:
                subscribers.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/open-folder")
def open_folder(req: Optional[dict] = None):
    folder = downloader_core.get_default_download_dir()
    if req and "path" in req and os.path.exists(req["path"]):
        folder = req["path"]

    try:
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
        return {"status": "opened", "path": folder}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>YouTube Downloader Web GUI</h1>"

def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader Web Server")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"), help="Host IP to bind to")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8000)), help="Port to listen on")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    args = parser.parse_args()

    import uvicorn
    import webbrowser

    if not args.no_browser and args.host in ["127.0.0.1", "localhost"]:
        def open_browser():
            import time
            time.sleep(1.2)
            webbrowser.open(f"http://{args.host}:{args.port}")
        threading.Thread(target=open_browser, daemon=True).start()

    print(f"Starting YouTube Downloader Pro at http://{args.host}:{args.port} ...")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()
