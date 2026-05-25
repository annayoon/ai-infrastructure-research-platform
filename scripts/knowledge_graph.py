from pathlib import Path
import csv
import re

SOURCE = Path("corpus_text")
OUT = Path("metadata/knowledge_graph.csv")

ENTITIES = [
    "DOE",
    "DoD",
    "AFCEC",
    "MTA",
    "TECC",
    "Alaska",
    "Korea",
    "Japan",
    "Taiwan",
    "AI",
    "GPU",
    "hyperscale",
    "power",
    "transmission",
    "fiber",
    "subsea",
    "Cascadia",
    "cooling",
    "PUE",
]

RELATION_PATTERNS = [
    "supports",
    "requires",
    "drives",
    "increases",
    "reduces",
    "enables",
    "improves",
    "creates",
]

rows = []

for file in SOURCE.glob("*.txt"):

    try:

        text = file.read_text(errors="ignore")

        sentences = re.split(r"[\\.!?]", text)

        for s in sentences:

            found_entities = []

            for e in ENTITIES:

                if e.lower() in s.lower():
                    found_entities.append(e)

            if len(found_entities) >= 2:

                relation = "related_to"

                for r in RELATION_PATTERNS:

                    if r.lower() in s.lower():
                        relation = r
                        break

                rows.append({
                    "source": found_entities[0],
                    "relation": relation,
                    "target": found_entities[1],
                    "sentence": s[:500],
                    "file": file.name
                })

    except Exception as e:
        print(f"ERROR: {file} / {e}")

with OUT.open("w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "source",
            "relation",
            "target",
            "sentence",
            "file"
        ]
    )

    writer.writeheader()

    writer.writerows(rows)

print(f"Generated {len(rows)} graph relations")