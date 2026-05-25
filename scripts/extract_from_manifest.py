from pathlib import Path
import re

import pandas as pd
from bs4 import BeautifulSoup
from pypdf import PdfReader


MANIFEST_PATH = Path("metadata/download_manifest.csv")
CORPUS_DIR = Path("corpus_text")
CORPUS_DIR.mkdir(exist_ok=True)


def clean_text(text):
    text = text or ""
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_html(path):
    html = Path(path).read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "form", "nav", "footer", "header"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    text = soup.get_text("\n")
    text = clean_text(text)

    if title:
        return f"{title}\n\n{text}"

    return text


def extract_pdf(path):
    reader = PdfReader(str(path))
    pages = []

    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")

    return clean_text("\n\n".join(pages))


def main():
    if not MANIFEST_PATH.exists():
        raise SystemExit("metadata/download_manifest.csv not found")

    df = pd.read_csv(MANIFEST_PATH).fillna("")

    output_rows = []

    for _, row in df.iterrows():
        source_id = str(row.get("source_id", "")).strip()
        status = str(row.get("status", "")).strip()
        file_type = str(row.get("file_type", "")).strip().lower()
        download_path = str(row.get("download_path", "")).strip()

        corpus_path = ""
        extract_status = "skipped"
        error = ""

        if status != "downloaded" or not download_path:
            output_rows.append({
                **row.to_dict(),
                "corpus_path": corpus_path,
                "extract_status": extract_status,
                "extract_error": error,
            })
            continue

        path = Path(download_path)

        if not path.exists():
            extract_status = "missing_download"
            error = "download file not found"
            output_rows.append({
                **row.to_dict(),
                "corpus_path": corpus_path,
                "extract_status": extract_status,
                "extract_error": error,
            })
            continue

        try:
            if file_type == "pdf":
                text = extract_pdf(path)
            else:
                text = extract_html(path)

            corpus_file = CORPUS_DIR / f"{source_id}.txt"

            text_with_meta = "\n".join([
                f"Title: {row.get('title', '')}",
                f"URL: {row.get('url', '')}",
                f"Domain: {row.get('domain', '')}",
                f"Country: {row.get('country', '')}",
                f"Category: {row.get('category', '')}",
                f"Subcategory: {row.get('subcategory', '')}",
                "",
                "----- BEGIN EXTRACTED TEXT -----",
                "",
                text,
            ])

            corpus_file.write_text(text_with_meta, encoding="utf-8")

            corpus_path = str(corpus_file)
            extract_status = "extracted"

        except Exception as e:
            extract_status = "failed"
            error = str(e)

        output_rows.append({
            **row.to_dict(),
            "corpus_path": corpus_path,
            "extract_status": extract_status,
            "extract_error": error,
        })

    out = pd.DataFrame(output_rows)
    out.to_csv(MANIFEST_PATH, index=False, encoding="utf-8-sig")

    print("[OK] Updated:", MANIFEST_PATH)
    print("Rows:", len(out))
    print()
    print("Extract status counts:")
    print(out["extract_status"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
