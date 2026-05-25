from pathlib import Path
from urllib.parse import urlparse
import hashlib
import mimetypes
import time

import pandas as pd
import requests


REGISTRY_PATH = Path("metadata/url_registry.csv")
MANIFEST_PATH = Path("metadata/download_manifest.csv")
DOWNLOAD_DIR = Path("downloads")

DOWNLOAD_DIR.mkdir(exist_ok=True)


def make_source_id(url):
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]


def infer_extension(url, content_type=""):
    content_type = (content_type or "").lower()
    path = urlparse(url).path.lower()

    if path.endswith(".pdf") or "application/pdf" in content_type:
        return "pdf"

    if path.endswith(".html") or path.endswith(".htm"):
        return "html"

    if "text/html" in content_type:
        return "html"

    if "pdf" in content_type:
        return "pdf"

    guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
    if guessed:
        return guessed.lstrip(".")

    return "html"


def main():
    if not REGISTRY_PATH.exists():
        raise SystemExit("metadata/url_registry.csv not found")

    registry = pd.read_csv(REGISTRY_PATH).fillna("")

    rows = []

    for _, item in registry.iterrows():
        url = str(item.get("url", "")).strip()

        if not url:
            continue

        source_id = make_source_id(url)

        print(f"[DOWNLOAD] {url}")

        status = "failed"
        error = ""
        content_type = ""
        file_type = ""
        download_path = ""

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 research-portal/1.0"
            }

            response = requests.get(url, headers=headers, timeout=30)
            content_type = response.headers.get("content-type", "")
            file_type = infer_extension(url, content_type)

            if response.status_code >= 400:
                status = f"http_{response.status_code}"
                error = f"HTTP {response.status_code}"
            else:
                download_path = DOWNLOAD_DIR / f"{source_id}.{file_type}"
                download_path.write_bytes(response.content)
                status = "downloaded"

        except Exception as e:
            error = str(e)

        rows.append({
            "source_id": source_id,
            "url": url,
            "title": item.get("title", ""),
            "domain": item.get("domain", ""),
            "country": item.get("country", ""),
            "category": item.get("category", ""),
            "subcategory": item.get("subcategory", ""),
            "query": item.get("query", ""),
            "priority": item.get("priority", ""),
            "status": status,
            "content_type": content_type,
            "file_type": file_type,
            "download_path": str(download_path),
            "error": error,
        })

        time.sleep(1)

    manifest = pd.DataFrame(rows)
    manifest.to_csv(MANIFEST_PATH, index=False, encoding="utf-8-sig")

    print()
    print("[OK] Saved:", MANIFEST_PATH)
    print("Rows:", len(manifest))
    print(manifest["status"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
