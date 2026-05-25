from pathlib import Path
import shutil

SOURCE = Path("corpus_text")
TARGET = Path("categorized")

CATEGORIES = {
    "power": ["power", "electricity", "grid", "transmission"],
    "fiber": ["fiber", "subsea", "latency", "bandwidth", "cable"],
    "cooling": ["cooling", "PUE", "WUE", "water"],
    "government": ["DOE", "DoD", "government", "policy"],
    "hyperscaler": ["AWS", "Microsoft", "Google", "Meta", "Oracle"],
    "AI": ["AI", "GPU", "compute", "training", "inference"],
    "Arctic": ["Arctic", "Alaska", "Cascadia"],
}

TARGET.mkdir(exist_ok=True)

for cat in CATEGORIES:
    (TARGET / cat).mkdir(exist_ok=True)

(TARGET / "uncategorized").mkdir(exist_ok=True)

for file in SOURCE.glob("*.txt"):

    try:
        text = file.read_text(errors="ignore").lower()

        matched = False

        for cat, keywords in CATEGORIES.items():

            for kw in keywords:

                if kw.lower() in text:

                    shutil.copy(
                        file,
                        TARGET / cat / file.name
                    )

                    matched = True
                    break

            if matched:
                break

        if not matched:

            shutil.copy(
                file,
                TARGET / "uncategorized" / file.name
            )

    except Exception as e:
        print(f"ERROR: {file} / {e}")

print("Categorization complete")