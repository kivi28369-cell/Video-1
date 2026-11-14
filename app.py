"""MASTER ALL VIDEO DOWNLOADER backend. Free, ad-free, no accounts needed to download."""
import os, uuid, threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp

APP = "MASTER ALL VIDEO DOWNLOADER"
DL_DIR = os.environ.get("DL_DIR", "downloads"); os.makedirs(DL_DIR, exist_ok=True)
app = FastAPI(title=APP)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
JOBS: dict[str, dict] = {}

class UrlIn(BaseModel):
    url: str
class DlIn(UrlIn):
    format_id: str | None = None
    audio_only: bool = False
    title: str | None = None

@app.post("/api/analyze")
def analyze(b: UrlIn):
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as y:
            i = y.extract_info(b.url, download=False)
    except Exception as e:
        raise HTTPException(400, f"Could not read this link: {str(e)[:200]}")
    fm = {}
    for f in i.get("formats", []):
        if f.get("vcodec") != "none" and f.get("height"):
            fm[f["height"]] = f["format_id"]
    return {"title": i.get("title"), "thumbnail": i.get("thumbnail"), "duration": i.get("duration"),
            "qualities": [{"height": h, "format_id": fm[h]} for h in sorted(fm, reverse=True)]}

def run(job_id: str, b: DlIn):
    j = JOBS[job_id]
    def hook(d):
        if j.get("cancel"): raise yt_dlp.utils.DownloadCancelled()
        if d["status"] == "downloading":
            t = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            j["progress"] = round(100 * d.get("downloaded_bytes", 0) / t, 1) if t else 0
        elif d["status"] == "finished":
            j["file"] = d["filename"]
    fmt = "bestaudio/best" if b.audio_only else (f"{b.format_id}+bestaudio/best" if b.format_id else "best")
    opts = {"quiet": True, "noplaylist": True, "format": fmt, "continuedl": True,
            "outtmpl": f"{DL_DIR}/{job_id}-%(title).80s.%(ext)s", "progress_hooks": [hook]}
    try:
        with yt_dlp.YoutubeDL(opts) as y: y.download([b.url])
        j["status"] = "done"; j["progress"] = 100
    except Exception as e:
        j["status"] = "cancelled" if j.get("cancel") else "error"; j["error"] = str(e)[:200]

@app.post("/api/download")
def download(b: DlIn):
    jid = uuid.uuid4().hex[:10]
    JOBS[jid] = {"id": jid, "status": "running", "progress": 0}
    threading.Thread(target=run, args=(jid, b), daemon=True).start()
    return JOBS[jid]

@app.get("/api/job/{jid}")
def job(jid: str):
    if jid not in JOBS: raise HTTPException(404, "Unknown download")
    return JOBS[jid]

@app.post("/api/job/{jid}/cancel")
def cancel(jid: str):
    if jid in JOBS: JOBS[jid]["cancel"] = True
    return {"ok": True}

@app.get("/api/file/{jid}")
def file(jid: str):
    f = JOBS.get(jid, {}).get("file")
    if not f or not os.path.exists(f): raise HTTPException(404, "File not ready")
    return FileResponse(f, filename=os.path.basename(f).split("-", 1)[-1])

app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "web"), html=True), name="web")
