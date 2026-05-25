import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
import pymupdf4llm


import requests

if len(sys.argv) < 2:
    raise SystemExit("사용법: python scripts/download_urls.py results/public_official_urls.txt [downloads]")

url_file = Path(sys.argv[1])
out_root = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("downloads")
out_root.mkdir(parents=True, exist_ok=True)

USER_AGENT = os.environ.get("CRAWL_USER_AGENT", "AlaskaAIDCResearchBot/0.1")
headers = {"Users-Agent": USER_AGENT}
DELAY = float(os.environ.get("CRAWL_DELAY", "0.3"))
MAX_MB = int(os.environ.get("MAX_MB", "80"))
MAX_BYTES = MAX_MB * 1024 * 1024




def ext_from_content_type(ct: str, url: str) -> str:
    ct = (ct or "").split(";")[0].strip().lower()
    path_ext = Path(urlparse(url).path).suffix.lower().replace(".", "")
    




    if "pdf" in ct:
        return "pdf"
    if "html" in ct:
        return "html"
    if path_ext:
        return path_ext
    return "bin"

meta_path = Path("results/download_manifest.jsonl")
meta_path.parent.mkdir(exist_ok=True)

with url_file.open("r", encoding="utf-8") as f, meta_path.open("a", encoding="utf-8") as meta:
    for raw in f:
        url = raw.strip()
        if not url or not url.startswith(("http://", "https://")):
            continue

        

        parsed = urlparse(url)
        domain_dir = out_root / parsed.netloc.replace(":", "_")
        domain_dir.mkdir(parents=True, exist_ok=True)

        try:
            r = requests.get(url, headers=headers, stream=True, timeout=15, allow_redirects=True)
            r.raise_for_status()

            content_type = r.headers.get("content-type", "")
            ext = ext_from_content_type(content_type, r.url)
            h = hashlib.sha256(r.url.encode("utf-8")).hexdigest()[:16]
            filename = domain_dir / f"{h}.{ext}"

            total = 0
            with filename.open("wb") as out:
                for chunk in r.iter_content(chunk_size=65536):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise RuntimeError(f"file too large > {MAX_MB}MB")
                    out.write(chunk)

            rec = {
                "source_url": url,
                "final_url": r.url,
                "domain": parsed.netloc,
                "file": str(filename),
                "content_type": content_type,
                "bytes": total,
                "status_code": r.status_code
            }
            meta.write(json.dumps(rec, ensure_ascii=False) + "\n")
            meta.flush()

            print(f"[DOWNLOADED] {filename} <- {url}")

        except Exception as e:
            print(f"[ERROR] {url} / {e}")

        time.sleep(DELAY)
