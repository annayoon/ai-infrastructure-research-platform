from pathlib import Path
import csv
import hashlib

ROOT = Path("corpus_text")
OUT = Path("metadata/source_index.csv")

KEYWORDS = {
    "power": ["power", "electricity", "grid", "transmission"],
    "fiber": ["fiber", "subsea", "cable", "latency", "bandwidth"],
    "cooling": ["cooling", "PUE", "WUE", "water"],
    "government": ["DOE", "DoD", "government", "policy"],
    "hyperscaler": ["AWS", "Microsoft", "Google", "Meta", "Oracle"],
    "AI": ["AI", "GPU", "compute", "inference", "training"],
    "Arctic": ["Arctic", "Alaska", "Cascadia"],
}

def detect_category(text):
    text = text.lower()

    scores = {}

    for cat, words in KEYWORDS.items():

        score = 0

        for w in words:
            if w.lower() in text:
                score += 1

        scores[cat] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "uncategorized"

    return best

rows = []

for file in ROOT.glob("*.txt"):

    try:
        content = file.read_text(errors="ignore")[:10000]

        category = detect_category(content)

        domain = file.name.split("_")[2] if "___" in file.name else "unknown"

        source_id = hashlib.md5(file.name.encode()).hexdigest()[:8]

        rows.append({
            "source_id": source_id,
            "title": file.stem[:120],
            "domain": domain,
            "country": "unknown",
            "category": category,
            "subcategory": "",
            "file_type": "txt",
            "file_path": str(file),
            "url": ""
        })

    except Exception as e:
        print(f"ERROR: {file} / {e}")

with OUT.open("w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "source_id",
            "title",
            "domain",
            "country",
            "category",
            "subcategory",
            "file_type",
            "file_path",
            "url"
        ]
    )

    writer.writeheader()

    writer.writerows(rows)

print(f"Indexed {len(rows)} files")