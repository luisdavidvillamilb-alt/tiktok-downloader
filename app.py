import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="TikTok Downloader")
BASE = Path(__file__).parent
STATIC = BASE / "static"

class DownloadRequest(BaseModel):
    url: HttpUrl

def valid_tiktok_url(raw: str) -> bool:
    host = (urlparse(raw).hostname or "").lower()
    return host == "tiktok.com" or host.endswith(".tiktok.com")

@app.get("/api/health")
def health():
    return {"ok": True, "service": "TikTok Downloader"}

@app.post("/api/download")
def download_video(body: DownloadRequest):
    url = str(body.url)
    if not valid_tiktok_url(url):
        raise HTTPException(status_code=400, detail="Pega un enlace válido de TikTok.")

    # Solo procesa enlaces públicos accesibles sin iniciar sesión ni eludir controles.
    tmp = tempfile.TemporaryDirectory(prefix="tiktok_dl_")
    outdir = Path(tmp.name)
    opts = {
        "outtmpl": str(outdir / "%(title).80B-%(id)s.%(ext)s"),
        "format": "best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "socket_timeout": 20,
        "retries": 1,
        "max_filesize": 250 * 1024 * 1024,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = Path(ydl.prepare_filename(info))
        if not filename.exists():
            candidates = list(outdir.glob("*"))
            candidates = [p for p in candidates if p.is_file() and p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"}]
            if not candidates:
                raise RuntimeError("No se encontró el archivo descargado.")
            filename = candidates[0]
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", filename.stem)[:70] + filename.suffix
        return FileResponse(
            filename,
            media_type="video/mp4" if filename.suffix.lower() == ".mp4" else "application/octet-stream",
            filename=safe_name,
            background=BackgroundTask(tmp.cleanup),
        )
    except yt_dlp.utils.DownloadError as exc:
        tmp.cleanup()
        raise HTTPException(status_code=422, detail="TikTok no permitió obtener este video. Comprueba que sea público y que tengas autorización para descargarlo.")
    except Exception:
        tmp.cleanup()
        raise HTTPException(status_code=500, detail="No se pudo procesar el video. Prueba con otro enlace público.")

app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
