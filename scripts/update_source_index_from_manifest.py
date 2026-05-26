from pathlib import Path
from datetime import datetime
import os
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

    today = datetime.now().strftime("%Y-%m-%d")
    update_batch = os.environ.get("UPDATE_BATCH", f"{today}-source-update")

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
        "added_at",
        "update_batch",
        "is_new",
        "is_latest_update",
    ]

    for col in required_cols:
        if col not in source.columns:
            source[col] = ""

    if not source.empty:
        source["is_new"] = "no"
        source["is_latest_update"] = "no"
        
    existing_keys = set()

    if not source.empty:
        for _, row in source.iterrows():
            key = clean(row.get("url", ""))
            if not key:
                key = clean(row.get("source_id", ""))
            if key:
                existing_keys.add(key)

    new_rows = []

    for _, row in manifest.iterrows():
        if clean(row.get("extract_status", "")) != "extracted":
            continue

        url = clean(row.get("url", ""))
        source_id = clean(row.get("source_id", ""))
        key = url or source_id

        is_new = "yes" if key and key not in existing_keys else "no"

        new_rows.append({
            "source_id": source_id,
            "title": clean(row.get("title", "")),
            "domain": clean(row.get("domain", "")),
            "country": clean(row.get("country", "")),
            "category": clean(row.get("category", "")),
            "subcategory": clean(row.get("subcategory", "")),
            "file_type": "txt",
            "file_path": clean(row.get("corpus_path", "")),
            "url": url,
            "summary": "",
            "keywords": "",
            "insights": "",
            "added_at": today,
            "update_batch": update_batch,
            "is_new": is_new,
            "is_latest_update":"yes",
        })    
    new_df = pd.DataFrame(new_rows, columns=required_cols)

    existing_added_at = {}
    existing_batch = {}

    if not source.empty:
        for _, row in source.iterrows():
            key = clean(row.get("url", ""))
            if not key:
                key = clean(row.get("source_id", ""))
            if key:
                existing_added_at[key] = clean(row.get("added_at", ""))
                existing_batch[key] = clean(row.get("update_batch", ""))

    combined = pd.concat([source[required_cols], new_df], ignore_index=True)

    combined["_dedup_key"] = combined["url"].apply(clean)
    combined.loc[combined["_dedup_key"] == "", "_dedup_key"] = combined["source_id"].apply(clean)

    combined = combined.drop_duplicates(subset=["_dedup_key"], keep="last")

    for idx, row in combined.iterrows():
        key = clean(row.get("_dedup_key", ""))

        if key in existing_added_at and existing_added_at[key]:
            combined.at[idx, "added_at"] = existing_added_at[key]

        if clean(row.get("is_new", "")) != "yes":
            if key in existing_batch and existing_batch[key]:
                combined.at[idx, "update_batch"] = existing_batch[key]

    combined = combined.drop(columns=["_dedup_key"])

    for col in combined.columns:
        combined[col] = combined[col].apply(clean)

    combined.to_csv(SOURCE_INDEX_PATH, index=False, encoding="utf-8-sig")

    print("[OK] Updated:", SOURCE_INDEX_PATH)
    print("Previous rows:", len(source))
    print("Manifest extracted rows:", len(new_df))
    print("Total rows:", len(combined))
    print("Rows with URL:", combined["url"].astype(str).str.strip().ne("").sum())
    print("Rows missing URL:", combined["url"].astype(str).str.strip().eq("").sum())
    print("New rows in this update:", (combined["is_new"] == "yes").sum())
    print("Update batch:", update_batch)


if __name__ == "__main__":
    main()
