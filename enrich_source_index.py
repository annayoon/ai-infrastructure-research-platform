from pathlib import Path
import re
import pandas as pd


SOURCE_INDEX_PATH = Path("metadata/source_index.csv")
SUMMARIES_PATH = Path("metadata/summaries.csv")
INSIGHTS_PATH = Path("metadata/insights.csv")
CORPUS_DIR = Path("corpus_text")


def clean_text(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in ["nan", "none", "null"]:
        return ""
    return re.sub(r"\s+", " ", value)


def is_hash_like(value):
    value = clean_text(value)
    return bool(re.fullmatch(r"[a-f0-9]{8,}(_[a-f0-9]{8,})?", value))


def extract_title_from_text(file_path):
    path = Path(file_path)

    if not path.is_absolute():
        path = Path(".") / path

    if not path.exists():
        return ""

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return ""

    skip_keywords = [
        "copyright notice",
        "this manuscript",
        "under contract",
        "u.s. government",
        "publisher",
        "license",
        "abstract",
        "contents",
        "table of contents",
        "acknowledgements",
        "disclaimer",
    ]

    candidates = []

    for line in lines[:150]:
        line = clean_text(line)

        if not line:
            continue

        lower = line.lower()

        if any(keyword in lower for keyword in skip_keywords):
            continue

        if len(line) < 20:
            continue

        if len(line) > 180:
            continue

        # 문장부호가 너무 많거나 본문 문장처럼 보이는 행은 후순위
        candidates.append(line)

    if not candidates:
        return ""

    return candidates[0]


def infer_domain_from_title_or_summary(text):
    text = clean_text(text).lower()

    rules = [
        ("eia.gov", ["eia", "energy information administration"]),
        ("energy.gov", ["department of energy", "doe", "lawrence berkeley", "berkeley lab", "lbl", "lbnl"]),
        ("commerce.gov", ["department of commerce", "commerce"]),
        ("nist.gov", ["nist", "national institute of standards and technology"]),
        ("whitehouse.gov", ["white house", "executive order"]),
        ("iea.org", ["international energy agency", "iea"]),
        ("datacenterdynamics.com", ["data center dynamics", "datacenter dynamics"]),
    ]

    for domain, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return domain

    return ""


def normalize_category(text, current_category):
    current_category = clean_text(current_category)
    text = clean_text(text).lower()

    if current_category:
        return current_category

    rules = [
        ("AI", ["ai", "artificial intelligence", "gpu", "hpc", "accelerator"]),
        ("data center", ["data center", "datacenter", "colocation", "hyperscale"]),
        ("power", ["power", "electricity", "energy", "generation", "grid", "utility"]),
        ("cooling", ["cooling", "liquid cooling", "immersion", "thermal"]),
        ("government", ["government", "federal", "policy", "department", "agency"]),
        ("connectivity", ["fiber", "subsea cable", "telecom", "broadband", "connectivity"]),
        ("manufacturing", ["manufacturing", "semiconductor", "advanced manufacturing", "campus"]),
        ("Alaska", ["alaska", "anchorage", "fairbanks", "arctic"]),
    ]

    for category, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return category

    return "uncategorized"


def main():
    if not SOURCE_INDEX_PATH.exists():
        raise SystemExit("metadata/source_index.csv not found")

    df = pd.read_csv(SOURCE_INDEX_PATH)

    # 기본 컬럼 보장
    for col in [
        "source_id",
        "title",
        "domain",
        "country",
        "category",
        "subcategory",
        "file_type",
        "file_path",
        "url",
    ]:
        if col not in df.columns:
            df[col] = ""

    # summaries.csv 병합
    if SUMMARIES_PATH.exists():
        summaries = pd.read_csv(SUMMARIES_PATH)
        if "file" in summaries.columns:
            summaries["file_name"] = summaries["file"].apply(lambda x: Path(str(x)).name)
            df["file_name"] = df["file_path"].apply(lambda x: Path(str(x)).name)

            merge_cols = ["file_name"]
            if "summary" in summaries.columns:
                merge_cols.append("summary")
            if "keywords" in summaries.columns:
                merge_cols.append("keywords")

            df = df.merge(
                summaries[merge_cols],
                on="file_name",
                how="left",
            )
        else:
            df["summary"] = ""
            df["keywords"] = ""
    else:
        df["summary"] = ""
        df["keywords"] = ""

    # insights.csv 병합
    if INSIGHTS_PATH.exists():
        insights = pd.read_csv(INSIGHTS_PATH)
        if "file" in insights.columns:
            insights["file_name"] = insights["file"].apply(lambda x: Path(str(x)).name)
            df["file_name"] = df["file_path"].apply(lambda x: Path(str(x)).name)

            merge_cols = ["file_name"]
            if "insights" in insights.columns:
                merge_cols.append("insights")

            df = df.merge(
                insights[merge_cols],
                on="file_name",
                how="left",
            )
        else:
            df["insights"] = ""
    else:
        df["insights"] = ""

    # 값 정리
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    # title 보정
    updated_titles = 0

    for idx, row in df.iterrows():
        current_title = clean_text(row.get("title", ""))
        file_path = clean_text(row.get("file_path", ""))

        if is_hash_like(current_title) or not current_title:
            extracted = extract_title_from_text(file_path)
            if extracted:
                df.at[idx, "title"] = extracted
                updated_titles += 1

    # domain/category 보정
    updated_domains = 0
    updated_categories = 0

    for idx, row in df.iterrows():
        combined = " ".join([
            clean_text(row.get("title", "")),
            clean_text(row.get("summary", "")),
            clean_text(row.get("keywords", "")),
            clean_text(row.get("insights", "")),
            clean_text(row.get("file_path", "")),
        ])

        if clean_text(row.get("domain", "")) in ["", "unknown"]:
            inferred_domain = infer_domain_from_title_or_summary(combined)
            if inferred_domain:
                df.at[idx, "domain"] = inferred_domain
                updated_domains += 1

        old_category = clean_text(row.get("category", ""))
        new_category = normalize_category(combined, old_category)
        if new_category != old_category:
            df.at[idx, "category"] = new_category
            updated_categories += 1

    # source_index.csv에 남길 컬럼 순서
    output_columns = [
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

    for col in output_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[output_columns]

    df.to_csv(SOURCE_INDEX_PATH, index=False, encoding="utf-8-sig")

    print("[OK] Enriched source_index.csv")
    print("Rows:", len(df))
    print("Updated titles:", updated_titles)
    print("Updated domains:", updated_domains)
    print("Updated categories:", updated_categories)
    print("Rows with URL:", df["url"].astype(str).str.strip().ne("").sum())
    print("Rows missing URL:", df["url"].astype(str).str.strip().eq("").sum())


if __name__ == "__main__":
    main()
