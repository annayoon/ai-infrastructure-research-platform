from pathlib import Path
import csv
import re

SOURCE = Path("corpus_text")
OUT = Path("metadata/insights.csv")

PATTERNS = {
    "power": [
        "power demand",
        "electricity demand",
        "transmission bottleneck",
        "grid congestion",
    ],

    "fiber": [
        "subsea",
        "Cascadia",
        "fiber diversification",
        "geo-diverse",
    ],

    "cooling": [
        "PUE",
        "cooling efficiency",
        "water usage",
        "cold climate",
    ],

    "government": [
        "critical infrastructure",
        "national security",
        "strategic infrastructure",
    ],

    "AI": [
        "AI infrastructure",
        "GPU demand",
        "hyperscale",
        "compute demand",
    ]
}

rows = []

for file in SOURCE.glob("*.txt"):

    try:

        text = file.read_text(errors="ignore")

        lower = text.lower()

        insights = []

        for topic, patterns in PATTERNS.items():

            for p in patterns:

                if p.lower() in lower:

                    insights.append(
                        f"{topic.upper()}: {p}"
                    )

        summary = "; ".join(insights[:10])

        rows.append({
            "file": file.name,
            "insights": summary
        })

    except Exception as e:
        print(f"ERROR: {file} / {e}")

with OUT.open("w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=["file", "insights"]
    )

    writer.writeheader()

    writer.writerows(rows)

print(f"Generated insights for {len(rows)} files")
