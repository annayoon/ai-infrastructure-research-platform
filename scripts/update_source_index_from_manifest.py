from pathlib import Path
import pandas as pd

SOURCE_INDEX_PATH = Path("metadata/source_index.csv")
MANIFEST_PATH = Path("metadata/download_manifest.csv")


def clean(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in ["nan", "none", "null"]:
        return ""
    return value


def main():
    if not MANIFEST_PATH.exists():
        raise SystemExit("metadata/download_manifest.csv not found")

    manifest = pd.read_csv(MANIFEST_PATH).fillna("")

    if SOURCE_INDEX_PATH.exists():
        source = pd.read_csv(SOURCE_INDEX_PATH).fillna("")
    else:
        source = pd.DataFrame()

    required_cols = [
        "source_id",
        "title",
        "domain",
        "country",
        "category",
        "subcategory",
        "file_type",
        "file_path",
        "url",
        "summary",
        "keywords",
        "insights",
    ]

    for col in required_cols:
        if col not in source.columns:
            source[col] = ""

    new_rows = []

    for _, row in manifest.iterrows():
        if clean(row.get("extract_status", "")) != "extracted":
            continue

        new_rows.append({
            "source_id": clean(row.get("source_id", "")),
            "title": clean(row.get("title", "")),
            "domain": clean(row.get("domain", "")),
            "country": clean(row.get("country", "")),
            "category": clean(row.get("category", "")),
            "subcategory": clean(row.get("subcategory", "")),
            "file_type": "txt",
            "file_path": clean(row.get("corpus_path", "")),
            "url": clean(row.get("url", "")),
            "summary": "",
            "keywords": "",
            "insights": "",
        })

    new_df = pd.DataFrame(new_rows, columns=required_cols)

    combined = pd.concat([source[required_cols], new_df], ignore_index=True)

    combined["_dedup_key"] = combined["url"].apply(clean)
    combined.loc[combined["_dedup_key"] == "", "_dedup_key"] = combined["source_id"].apply(clean)

    combined = combined.drop_duplicates(subset=["_dedup_key"], keep="last")
    combined = combined.drop(columns=["_dedup_key"])

    for col in combined.columns:
        combined[col] = combined[col].apply(clean)

    combined.to_csv(SOURCE_INDEX_PATH, index=False, encoding="utf-8-sig")

    print("[OK] Updated:", SOURCE_INDEX_PATH)
    print("Previous rows:", len(source))
    print("New extracted rows:", len(new_df))
    print("Total rows:", len(combined))
    print("Rows with URL:", combined["url"].astype(str).str.strip().ne("").sum())
    print("Rows missing URL:", combined["url"].astype(str).str.strip().eq("").sum())


if __name__ == "__main__":
    main()
