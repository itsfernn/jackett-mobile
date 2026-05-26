import os
import re
import json
import httpx
from urllib.parse import urlparse, parse_qs
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

app = FastAPI(title="Jackett Mobile")

JACKETT_URL = os.environ.get("JACKETT_URL", "http://localhost:9117").rstrip("/")
JACKETT_API_KEY = os.environ.get("JACKETT_API_KEY", "")

APP_TITLE = os.environ.get("APP_TITLE", "Jackett Mobile").strip()

INDEXERS_RAW = os.environ.get("INDEXERS", "").strip()
INDEXERS = INDEXERS_RAW if INDEXERS_RAW else "all"
try:
    parsed = json.loads(INDEXERS_RAW)
    if isinstance(parsed, list):
        INDEXERS = ",".join(str(i).strip() for i in parsed if str(i).strip())
except (json.JSONDecodeError, TypeError):
    pass


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html") as f:
        html = f.read()
    return html.replace("{{APP_TITLE}}", APP_TITLE)


def _extract(r: dict) -> dict:
    return {
        "title": r.get("Title"),
        "guid": r.get("Guid"),
        "link": r.get("Link"),
        "size": r.get("Size", 0),
        "seeders": r.get("Seeders", 0),
        "peers": r.get("Peers", 0),
        "indexer": r.get("Tracker"),
        "trackerId": r.get("TrackerId"),
        "bannerUrl": r.get("BannerUrl"),
        "poster": r.get("Poster"),
        "publishDate": r.get("PublishDate"),
    }


@app.get("/api/search")
async def search(q: str = Query(...)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{JACKETT_URL}/api/v2.0/indexers/{INDEXERS}/results",
                params={"apikey": JACKETT_API_KEY, "Query": q},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json().get("Results", [])
        except httpx.TimeoutException:
            raise HTTPException(504, "Jackett request timed out")
        except httpx.HTTPStatusError as e:
            raise HTTPException(502, f"Jackett error: {e.response.status_code}")

    return {"results": [_extract(r) for r in data]}


@app.get("/api/download")
async def download(link: str = Query(...)):
    return RedirectResponse(url=link)


@app.post("/api/blackhole")
async def blackhole(body: dict):
    link = body.get("link")
    tracker_id = body.get("trackerId")
    title = body.get("title", "torrent")
    if not link or not tracker_id:
        raise HTTPException(400, "Missing 'link' or 'trackerId' in request body")

    qs = parse_qs(urlparse(link).query)
    path = qs.get("path", [None])[0]
    if not path:
        raise HTTPException(400, "Could not extract path from download link")

    file_param = qs.get("file", [None])[0]
    if file_param:
        filename = file_param
    else:
        filename = re.sub(r'[^\w\s.-]', '', title).strip() or "torrent"
        filename = re.sub(r'\s+', '_', filename) + ".torrent"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{JACKETT_URL}/bh/{tracker_id}/",
                params={
                    "jackett_apikey": JACKETT_API_KEY,
                    "path": path,
                    "file": filename,
                },
                timeout=30,
                follow_redirects=True,
            )
            resp.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(504, "Jackett black hole request timed out")
        except httpx.HTTPStatusError as e:
            raise HTTPException(502, f"Jackett black hole error: {e.response.status_code}")

    return {"status": "ok", "filename": filename}
