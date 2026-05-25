from pathlib import Path
import re
import pandas as pd


SOURCE_INDEX = Path("metadata/source_index.csv")
SUMMARIES = Path("metadata/summaries.csv")
INSIGHTS = Path("metadata/insights.csv")


def clean(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in ["nan", "none", "null"]:
        return ""
    return re.sub(r"\s+", " ", value)


def is_hash_like(value):
    value = clean(value)
    return bool(re.fullmatch(r"[a-z0-9]{8,}(_[a-z0-9]{8,})?", value))


def file_name_from_path(value):
    value = clean(value)
    if not value:
        return ""
    return Path(value).name


def decode_url_like_name(value):
    """
    Recover approximate URL from filenames like:
    https___www.ndc.gov.tw_en_Content_List.aspx_n=E738D6D7DD31163F.txt

    Because original separators were collapsed to underscores, this is best-effort.
    It works well enough for many government/public URLs.
    """
    value = clean(value)

    if not value:
        return ""

    # Remove corpus_text/ and .txt
    value = Path(value).name
    if value.endswith(".txt"):
        value = value[:-4]

    if not value.startswith("https___") and not value.startswith("http___"):
        return ""

    if value.startswith("https___"):
        rest = value[len("https___"):]
        scheme = "https://"
    else:
        rest = value[len("http___"):]
        scheme = "http://"

    # Known domain patterns first
    known_domains = [
        "www.ndc.gov.tw",
        "english.www.gov.cn",
        "op.europa.eu",
        "www.energy.gov",
        "www.eia.gov",
        "www.iea.org",
        "www.commerce.gov",
        "www.whitehouse.gov",
        "www.nist.gov",
        "eta-publications.lbl.gov",
        "escholarship.org",
    ]

    for domain in known_domains:
        encoded_domain = domain.replace(".", ".")
        if rest.startswith(encoded_domain + "_"):
            path = rest[len(encoded_domain) + 1:]
            path = path.replace("_-_", "/-/")
            path = path.replace("_", "/")
            return scheme + domain + "/" + path
        if rest == encoded_domain:
            return scheme + domain

    # Generic fallback:
    # Find likely domain part up to first underscore after a known TLD-ish pattern.
    m = re.match(r"([^_]+(?:\.[^_]+)+)_(.+)", rest)
    if not m:
        return scheme + rest.replace("_", "/")

    domain = m.group(1)
    path = m.group(2)

    path = path.replace("_-_", "/-/")
    path = path.replace("_", "/")

    return scheme + domain + "/" + path


def infer_domain_from_url(url):
    url = clean(url)
    if not url:
        return ""
    m = re.match(r"https?://([^/]+)", url)
    if not m:
        return ""
    return m.group(1).replace("www.", "")


def make_title_from_summary(summary):
    summary = clean(summary)
    if not summary:
        return ""

    # 첫 문장 또는 앞부분을 제목처럼 사용
    first_sentence = re.split(r"(?<=[.!?])\s+", summary)[0]
    first_sentence = clean(first_sentence)

    if len(first_sentence) > 120:
        first_sentence = first_sentence[:117].rstrip() + "..."

    return first_sentence


def make_title_from_url(url):
    url = clean(url)
    if not url:
        return ""

    # URL 마지막 부분을 사람이 읽을 수 있게 변환
    last = url.rstrip("/").split("/")[-1]
    last = re.sub(r"\.html?$", "", last)
    last = last.replace("-", " ").replace("_", " ")
    last = clean(last)

    if not last or len(last) < 8:
        return url

    return last[:140]


def main():
    df = pd.read_csv(SOURCE_INDEX)

    # 기본 컬럼 보장
    for col in ["source_id", "title", "domain", "country", "category", "subcategory", "file_type", "file_path", "url"]:
        if col not in df.columns:
            df[col] = ""

    # file_name 생성
    df["file_name"] = df["file_path"].apply(file_name_from_path)

    # summaries 병합
    if SUMMARIES.exists():
        summaries = pd.read_csv(SUMMARIES)
        summaries["file_name"] = summaries["file"].apply(file_name_from_path)
        keep = ["file_name"]
        if "summary" in summaries.columns:
            keep.append("summary")
        if "keywords" in summaries.columns:
            keep.append("keywords")
        df = df.merge(summaries[keep], on="file_name", how="left")

    # insights 병합
    if INSIGHTS.exists():
        insights = pd.read_csv(INSIGHTS)
        insights["file_name"] = insights["file"].apply(file_name_from_path)
        keep = ["file_name"]
        if "insights" in insights.columns:
            keep.append("insights")
        df = df.merge(insights[keep], on="file_name", how="left")

    # 모든 값 정리
    for col in df.columns:
        df[col] = df[col].apply(clean)

    repaired_urls = 0
    repaired_titles = 0
    repaired_domains = 0

    for idx, row in df.iterrows():
        title = clean(row.get("title", ""))
        file_path = clean(row.get("file_path", ""))
        url = clean(row.get("url", ""))
        summary = clean(row.get("summary", ""))
        domain = clean(row.get("domain", ""))

        # 1) URL 복구: title 또는 file_path에 https___가 있으면 복구
        if not url:
            decoded = decode_url_like_name(title) or decode_url_like_name(file_path)
            if decoded:
                df.at[idx, "url"] = decoded
                url = decoded
                repaired_urls += 1

        # 2) domain 복구
        if not domain or domain == "unknown":
            inferred_domain = infer_domain_from_url(url)
            if inferred_domain:
                df.at[idx, "domain"] = inferred_domain
                repaired_domains += 1

        # 3) title 복구
        # 해시형 제목이면 summary 첫 문장 사용, 없으면 URL 마지막 경로 사용
        if is_hash_like(title) or title.startswith("https___") or title.startswith("http___") or not title:
            new_title = make_title_from_summary(summary) or make_title_from_url(url)
            if new_title:
                df.at[idx, "title"] = new_title
                repaired_titles += 1

    # NaN 방지
    for col in df.columns:
        df[col] = df[col].apply(clean)

    output_cols = [
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

    for col in output_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[output_cols]

    df.to_csv(SOURCE_INDEX, index=False, encoding="utf-8-sig")

    print("[OK] Repaired source_index.csv")
    print("Rows:", len(df))
    print("Repaired URLs:", repaired_urls)
    print("Repaired titles:", repaired_titles)
    print("Repaired domains:", repaired_domains)
    print("Rows with URL:", df["url"].astype(str).str.strip().ne("").sum())
    print("Rows missing URL:", df["url"].astype(str).str.strip().eq("").sum())


if __name__ == "__main__":
    main()
