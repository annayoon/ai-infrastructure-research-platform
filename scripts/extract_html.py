from pathlib import Path
import trafilatura

Path("corpus_text").mkdir(exist_ok=True)

for html in Path("downloads").glob("*.html"):
    try:
        raw = html.read_text(errors="ignore")

        text = trafilatura.extract(
            raw,
            include_links=True,
            include_tables=True
        )

        if text:
            out = Path("corpus_text") / (html.stem + ".txt")
            out.write_text(text)

            print(f"[OK] {out}")

    except Exception as e:
        print(f"[ERROR] {html} / {e}")
