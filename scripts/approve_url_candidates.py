from pathlib import Path
import pandas as pd

CANDIDATES_PATH = Path("metadata/url_candidates.csv")
REGISTRY_PATH = Path("metadata/url_registry.csv")

REGISTRY_COLUMNS = [
    "url",
    "title",
    "domain",
    "country",
    "category",
    "subcategory",
    "query",
    "priority",
    "status",
    "notes",
]

def clean(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in ["nan", "none", "null"]:
        return ""
    return value

def main():
    if not CANDIDATES_PATH.exists():
        raise SystemExit("metadata/url_candidates.csv not found")

    candidates = pd.read_csv(CANDIDATES_PATH).fillna("")

    approved = candidates[
        candidates["review_status"].astype(str).str.strip().str.lower().eq("approved")
    ].copy()

    approved_registry = pd.DataFrame({
        "url": approved["url"],
        "title": approved["title"],
        "domain": approved["domain"],
        "country": approved["country"],
        "category": approved["category"],
        "subcategory": approved["subcategory"],
        "query": approved["query"],
        "priority": approved["priority"],
        "status": "new",
        "notes": approved["notes"],
    })

    if REGISTRY_PATH.exists():
        registry = pd.read_csv(REGISTRY_PATH).fillna("")
    else:
        registry = pd.DataFrame(columns=REGISTRY_COLUMNS)

    for col in REGISTRY_COLUMNS:
        if col not in registry.columns:
            registry[col] = ""

    combined = pd.concat(
        [registry[REGISTRY_COLUMNS], approved_registry[REGISTRY_COLUMNS]],
        ignore_index=True,
    )

    for col in combined.columns:
        combined[col] = combined[col].apply(clean)

    before = len(combined)
    combined = combined.drop_duplicates(subset=["url"], keep="last")
    after = len(combined)

    combined.to_csv(REGISTRY_PATH, index=False, encoding="utf-8-sig")

    print("[OK] Approved candidates added to registry")
    print("Approved candidates:", len(approved_registry))
    print("Registry rows:", after)
    print("Removed duplicates:", before - after)

if __name__ == "__main__":
    main()
