
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from PIL import Image, ImageDraw, ImageFont
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


def valid_tiktok_url(raw):
    host = (urlparse(raw).hostname or "").lower()
    return host == "tiktok.com" or host.endswith(".tiktok.com")


def create_watermark(path):
    image = Image.new("RGBA", (620, 90), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38
    )

    draw.rounded_rectangle(
        (5, 5, 615, 85),
        radius=16,
        fill=(0, 0, 0, 105)
    )

    draw.text(
        (22, 17),
        "@theclipscolombia",
        font=font,
        fill=(255, 255, 255, 210)
    )

    image.save(path)


def apply_watermark(source, destination, workdir):
    watermark = workdir / "marca.png"
    create_watermark(watermark)

    command = [
        "ffmpeg", "-y",
        "-threads", "1",
        "-filter_threads", "1",
        "-filter_complex_threads", "1",
        "-i", str(source),
        "-i", str(watermark),
        "-filter_complex",
        "[0:v]scale=w='min(720,iw)':h=-2[base];"
        "[1:v][base]scale2ref=w=main_w*0.42:h=-1[wm][base2];"
        "[base2][wm]overlay=x=W-w-16:y=H-h-16:format=auto[v]",
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-threads", "1",
        "-preset", "ultrafast",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "96k",
        "-movflags", "+faststart",
        str(destination)
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300
    )


@app.get("/api/health")
def health():
    return {"ok": True, "service": "TikTok Downloader"}


@app.post("/api/download")
def download_video(body: DownloadRequest):
    url = str(body.url)

    if not valid_tiktok_url(url):
        raise HTTPException(
            status_code=400,
            detail="Pega un enlace válido de TikTok."
        )

    tmp = tempfile.TemporaryDirectory(prefix="tiktok_dl_")
    outdir = Path(tmp.name)

    opts = {
        "outtmpl": str(outdir / "%(title).60B-%(id)s.%(ext)s"),
        "format": "best[height<=720][ext=mp4]/best[height<=720]/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "socket_timeout": 20,
        "retries": 1,
        "max_filesize": 100 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = Path(ydl.prepare_filename(info))

        if not filename.exists():
            candidates = [
                p for p in outdir.glob("*")
                if p.is_file() and p.suffix.lower() in
                {".mp4", ".mov", ".mkv", ".webm"}
            ]

            if not candidates:
                raise RuntimeError("No se encontró el video.")

            filename = candidates[0]

        watermarked = outdir / "video_theclipscolombia.mp4"

        apply_watermark(filename, watermarked, outdir)

        safe_name = re.sub(
            r"[^A-Za-z0-9._-]+", "_", filename.stem
        )[:60]

        return FileResponse(
            watermarked,
            media_type="video/mp4",
            filename=f"{safe_name}_theclipscolombia.mp4",
            background=BackgroundTask(tmp.cleanup)
        )

    except yt_dlp.utils.DownloadError:
        tmp.cleanup()
        raise HTTPException(
            status_code=422,
            detail="TikTok no permitió obtener este video público."
        )

    except subprocess.TimeoutExpired:
        tmp.cleanup()
        raise HTTPException(
            status_code=504,
            detail="El video tardó demasiado en procesarse."
        )

    except Exception:
        tmp.cleanup()
        raise HTTPException(
            status_code=500,
            detail="No se pudo procesar el video con la marca de agua."
        )


app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
