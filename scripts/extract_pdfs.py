from pathlib import Path
import hashlib
import subprocess

Path("corpus_text").mkdir(exist_ok=True)

for pdf in Path("downloads").rglob("*.pdf"):
    h = hashlib.sha256(str(pdf).encode("utf-8")).hexdigest()[:10]
    out = Path("corpus_text") / f"{pdf.stem}_{h}.txt"

    try:
        subprocess.run(["pdftotext", "-layout", str(pdf), str(out)], check=True)
        print(f"[PDF TEXT] {out}")
    except Exception as e:
        print(f"[PDF ERROR] {pdf} / {e}")
