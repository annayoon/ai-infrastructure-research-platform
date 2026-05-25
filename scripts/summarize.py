from pathlib import Path
import csv
import re

SOURCE = Path("corpus_text")
OUT = Path("metadata/summaries.csv")

KEYWORDS = [
    "AI",
    "GPU",
    "power",
    "electricity",
    "transmission",
    "subsea",
    "fiber",
    "latency",
    "cooling",
    "PUE",
    "Arctic",
    "Cascadia",
    "hyperscale",
    "compute",
]

rows = []

for file in SOURCE.glob("*.txt"):

    try:
        text = file.read_text(errors="ignore")

        # clean
        clean = re.sub(r"\\s+", " ", text)

        # first 500 chars
        summary = clean[:500]

        # keyword detection
        found = []

        for kw in KEYWORDS:
            if kw.lower() in clean.lower():
                found.append(kw)

        rows.append({
            "file": file.name,
            "summary": summary,
            "keywords": ", ".join(found)
        })

    except Exception as e:
        print(f"ERROR: {file} / {e}")

with OUT.open("w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=["file", "summary", "keywords"]
    )

    writer.writeheader()

    writer.writerows(rows)

print(f"Generated summaries for {len(rows)} files")