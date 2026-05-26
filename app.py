from pathlib import Path
from datetime import datetime
import re

import pandas as pd
import streamlit as st


# =========================================================
# Basic Settings
# =========================================================

st.set_page_config(
    page_title="AI Infrastructure Research Portal",
    page_icon="🔎",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent

METADATA_DIR = BASE_DIR / "metadata"
RESULTS_DIR = BASE_DIR / "results"
DOWNLOADS_DIR = BASE_DIR / "downloads"
CORPUS_DIR = BASE_DIR / "corpus_text"

SOURCE_INDEX_PATH = METADATA_DIR / "source_index.csv"


# =========================================================
# Style
# =========================================================

st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }

    h1, h2, h3 {
        font-weight: 800;
    }

    .small-caption {
        color: #9ca3af;
        font-size: 0.9rem;
    }

    .status-caption {
        color: #9ca3af;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Helper Functions
# =========================================================

def normalize_empty(value):
    """
    Convert NaN, None, 'None', 'nan', 'null' values to empty string.
    """
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.lower() in ["none", "nan", "null"]:
        return ""

    return value


def load_source_index():
    """
    Load metadata/source_index.csv safely.
    """
    if not SOURCE_INDEX_PATH.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(SOURCE_INDEX_PATH)
    except Exception as e:
        st.error(f"Failed to read source index: {e}")
        return pd.DataFrame()

    df.columns = [str(col).strip() for col in df.columns]

    expected_columns = [
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

    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""

    for col in df.columns:
        df[col] = df[col].apply(normalize_empty)

    return df


def get_available_columns(df, preferred_columns):
    return [col for col in preferred_columns if col in df.columns]


def read_text_file(path):
    """
    Read a text file safely with fallback encodings.
    """
    path = Path(path)

    if not path.exists():
        return ""

    for encoding in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception:
            return ""

    return ""


def list_corpus_files():
    """
    Return all text-like files from corpus_text.
    """
    if not CORPUS_DIR.exists():
        return []

    files = []
    for ext in ["*.txt", "*.md", "*.csv", "*.json"]:
        files.extend(CORPUS_DIR.rglob(ext))

    return sorted(files)


def search_corpus(keyword, max_results=100):
    """
    Simple keyword search over corpus_text.
    """
    keyword = keyword.strip().lower()

    if not keyword:
        return []

    matches = []
    corpus_files = list_corpus_files()

    for file_path in corpus_files:
        text = read_text_file(file_path)
        if not text:
            continue

        lowered = text.lower()

        if keyword not in lowered:
            continue

        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            if keyword in line.lower():
                matches.append(
                    {
                        "file": str(file_path.relative_to(BASE_DIR)),
                        "line": idx,
                        "text": line.strip()[:500],
                    }
                )

                if len(matches) >= max_results:
                    return matches

    return matches


def to_yes_no(value):
    value = normalize_empty(value).lower()
    if value in ["yes", "true", "1", "y"]:
        return "yes"
    return "no"


def clean_keyword_text(text):
    text = normalize_empty(text)
    text = re.sub(r"\s+", " ", text)
    return text


# =========================================================
# Header
# =========================================================

st.title("AI Infrastructure Research Portal")

st.markdown(
    """
    <div class="small-caption">
    Research portal for AI infrastructure, data center, power generation,
    advanced technology campus, Alaska market validation, Arctic connectivity,
    cooling advantage, and public-source evidence tracking.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# Load Data
# =========================================================

source_df = load_source_index()


# =========================================================
# Sidebar
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Source Index",
        "Corpus Search",
        "File Preview",
        "Data Health Check",
    ],
)

st.sidebar.divider()

st.sidebar.caption("Repository paths")
st.sidebar.code(
    f"""metadata: {METADATA_DIR.name}
results: {RESULTS_DIR.name}
downloads: {DOWNLOADS_DIR.name}
corpus_text: {CORPUS_DIR.name}""",
    language="text",
)


# =========================================================
# Overview
# =========================================================

if page == "Overview":
    st.header("Overview")

    total_sources = len(source_df) if not source_df.empty else 0

    if not source_df.empty:
        url_count = source_df["url"].astype(str).str.strip().ne("").sum()
        category_count = source_df["category"].astype(str).str.strip().ne("").sum()
        corpus_count = len(list_corpus_files())

        new_count = source_df["is_new"].astype(str).str.lower().eq("yes").sum()
        latest_update_count = source_df["is_latest_update"].astype(str).str.lower().eq("yes").sum()
    else:
        url_count = 0
        category_count = 0
        corpus_count = len(list_corpus_files())
        new_count = 0
        latest_update_count = 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Sources", total_sources)
    col2.metric("Original URLs", int(url_count))
    col3.metric("Categorized Rows", int(category_count))
    col4.metric("New Sources", int(new_count))
    col5.metric("Latest Updated", int(latest_update_count))
    col6.metric("Corpus Files", corpus_count)

    st.subheader("Recommended Workflow")

    st.markdown(
        """
        1. Use **Source Index** to check collected sources and open original URLs.
        2. Use **Only rows with URL** when selecting evidence for formal reports.
        3. Use **Only latest update** to review sources processed in the most recent update batch.
        4. Use **Corpus Search** to find supporting paragraphs inside extracted local text files.
        5. Use **Data Health Check** to identify missing URLs, missing titles, or incomplete metadata.
        """
    )

    st.subheader("Data Load Status")

    if SOURCE_INDEX_PATH.exists():
        modified_time = datetime.fromtimestamp(SOURCE_INDEX_PATH.stat().st_mtime)
        st.caption(f"Source index path: {SOURCE_INDEX_PATH}")
        st.caption(f"Source index last modified: {modified_time}")
        st.caption(f"Loaded source_index rows: {len(source_df)}")

        if "url" in source_df.columns:
            loaded_url_count = source_df["url"].astype(str).str.strip().ne("").sum()
            st.caption(f"Loaded source_index URLs: {loaded_url_count}")
    else:
        st.warning("metadata/source_index.csv was not found.")

    if not source_df.empty:
        st.subheader("Category Snapshot")

        category_counts = (
            source_df["category"]
            .replace("", "uncategorized")
            .value_counts()
            .reset_index()
        )
        category_counts.columns = ["Category", "Count"]

        st.dataframe(
            category_counts,
            use_container_width=True,
            hide_index=True,
        )

    if source_df.empty:
        st.warning(
            "metadata/source_index.csv was not found or could not be loaded. "
            "Please check whether the metadata directory and CSV file exist."
        )


# =========================================================
# Source Index
# =========================================================

elif page == "Source Index":
    st.header("Source Index")

    if source_df.empty:
        st.warning("No source index found. Please create metadata/source_index.csv first.")
        st.stop()

    st.caption(
        "Collected source metadata. Use the Original Source column to open source URLs when available."
    )

    # Filters
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([1, 1, 1, 1, 2])

    categories = sorted(
        [
            c
            for c in source_df["category"].dropna().astype(str).unique().tolist()
            if c.strip()
        ]
    )

    selected_category = filter_col1.selectbox(
        "Category",
        ["All"] + categories,
    )

    only_with_url = filter_col2.checkbox("Only rows with URL", value=False)

    only_new = filter_col3.checkbox("Only new sources", value=False)

    only_latest_update = filter_col4.checkbox("Only latest update", value=False)

    keyword = filter_col5.text_input(
        "Keyword filter",
        placeholder="Search title, domain, category, summary, keywords, insights...",
    )

    view_df = source_df.copy()

    if selected_category != "All":
        view_df = view_df[view_df["category"] == selected_category]

    if only_with_url:
        view_df = view_df[view_df["url"].astype(str).str.strip().ne("")]

    if only_new and "is_new" in view_df.columns:
        view_df = view_df[view_df["is_new"].astype(str).str.lower().eq("yes")]

    if only_latest_update and "is_latest_update" in view_df.columns:
        view_df = view_df[view_df["is_latest_update"].astype(str).str.lower().eq("yes")]

    if keyword.strip():
        keyword_lower = keyword.strip().lower()

        searchable_cols = [
            col
            for col in [
                "source_id",
                "title",
                "domain",
                "country",
                "category",
                "subcategory",
                "url",
                "summary",
                "keywords",
                "insights",
                "file_path",
                "added_at",
                "update_batch",
                "is_new",
                "is_latest_update",
            ]
            if col in view_df.columns
        ]

        mask = view_df[searchable_cols].apply(
            lambda row: keyword_lower in " ".join(row.astype(str)).lower(),
            axis=1,
        )

        view_df = view_df[mask]

    st.write(f"Showing **{len(view_df)}** of **{len(source_df)}** rows.")

    preferred_columns = [
        "source_id",
        "title",
        "domain",
        "country",
        "category",
        "subcategory",
        "file_type",
        "url",
        "file_path",
        "added_at",
        "update_batch",
        "is_new",
        "is_latest_update",
        "summary",
        "keywords",
        "insights",
    ]

    display_columns = get_available_columns(view_df, preferred_columns)

    display_df = view_df[display_columns].copy()

    display_df = display_df.rename(
        columns={
            "source_id": "Source ID",
            "title": "Title",
            "domain": "Domain",
            "country": "Country",
            "category": "Category",
            "subcategory": "Subcategory",
            "file_type": "File Type",
            "url": "Original Source",
            "file_path": "File Path",
            "added_at": "Added At",
            "update_batch": "Update Batch",
            "is_new": "New",
            "is_latest_update": "Latest Update",
            "summary": "Summary",
            "keywords": "Keywords",
            "insights": "Insights",
        }
    )

    column_config = {}

    if "Original Source" in display_df.columns:
        column_config["Original Source"] = st.column_config.LinkColumn(
            "Original Source",
            help="Open the original source URL",
            display_text="Open source",
        )

    if "Title" in display_df.columns:
        column_config["Title"] = st.column_config.TextColumn(
            "Title",
            width="large",
        )

    if "Category" in display_df.columns:
        column_config["Category"] = st.column_config.TextColumn(
            "Category",
            width="small",
        )

    if "Summary" in display_df.columns:
        column_config["Summary"] = st.column_config.TextColumn(
            "Summary",
            width="large",
        )

    if "Insights" in display_df.columns:
        column_config["Insights"] = st.column_config.TextColumn(
            "Insights",
            width="large",
        )

    if "New" in display_df.columns:
        column_config["New"] = st.column_config.TextColumn("New", width="small")

    if "Latest Update" in display_df.columns:
        column_config["Latest Update"] = st.column_config.TextColumn("Latest Update", width="small")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )

    st.download_button(
        label="Download filtered source index as CSV",
        data=display_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_source_index.csv",
        mime="text/csv",
    )


# =========================================================
# Corpus Search
# =========================================================

elif page == "Corpus Search":
    st.header("Corpus Search")

    st.caption(
        "Search extracted text files under corpus_text. "
        "Use this to find supporting evidence for report writing."
    )

    keyword = st.text_input(
        "Search keyword",
        placeholder="Example: Alaska power generation, cold climate cooling, Arctic fiber, data center electricity demand...",
    )

    max_results = st.slider(
        "Max results",
        min_value=10,
        max_value=300,
        value=100,
        step=10,
    )

    if st.button("Search", type="primary"):
        if not keyword.strip():
            st.warning("Please enter a keyword.")
        else:
            results = search_corpus(keyword, max_results=max_results)

            if not results:
                st.warning("No matches found.")
            else:
                result_df = pd.DataFrame(results)

                st.success(f"Found {len(result_df)} matching lines.")

                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "file": st.column_config.TextColumn("File", width="medium"),
                        "line": st.column_config.NumberColumn("Line"),
                        "text": st.column_config.TextColumn("Text", width="large"),
                    },
                )

                st.download_button(
                    label="Download search results as CSV",
                    data=result_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="corpus_search_results.csv",
                    mime="text/csv",
                )


# =========================================================
# File Preview
# =========================================================

elif page == "File Preview":
    st.header("File Preview")

    st.caption(
        "Preview local text files collected or extracted into the repository."
    )

    corpus_files = list_corpus_files()

    if not corpus_files:
        st.warning("No text files found under corpus_text.")
        st.stop()

    file_options = [str(path.relative_to(BASE_DIR)) for path in corpus_files]

    selected_file = st.selectbox("Select a file", file_options)

    selected_path = BASE_DIR / selected_file

    content = read_text_file(selected_path)

    if not content:
        st.warning("Could not read this file.")
    else:
        st.write(f"Previewing: `{selected_file}`")

        max_chars = st.slider(
            "Preview length",
            min_value=1000,
            max_value=50000,
            value=10000,
            step=1000,
        )

        st.text_area(
            "File content",
            value=content[:max_chars],
            height=600,
        )

        st.download_button(
            label="Download this text file",
            data=content.encode("utf-8"),
            file_name=Path(selected_file).name,
            mime="text/plain",
        )


# =========================================================
# Data Health Check
# =========================================================

elif page == "Data Health Check":
    st.header("Data Health Check")

    if source_df.empty:
        st.warning("No source index found.")
        st.stop()

    total_rows = len(source_df)

    missing_url = source_df["url"].astype(str).str.strip().eq("").sum()
    missing_title = source_df["title"].astype(str).str.strip().eq("").sum()
    missing_category = source_df["category"].astype(str).str.strip().eq("").sum()

    new_count = source_df["is_new"].astype(str).str.lower().eq("yes").sum()
    latest_update_count = source_df["is_latest_update"].astype(str).str.lower().eq("yes").sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Rows", total_rows)
    col2.metric("Missing URLs", int(missing_url))
    col3.metric("Missing Titles", int(missing_title))
    col4.metric("Missing Categories", int(missing_category))
    col5.metric("Latest Updated", int(latest_update_count))

    st.subheader("Update Batch Summary")

    if "update_batch" in source_df.columns:
        batch_df = (
            source_df["update_batch"]
            .replace("", "unknown")
            .value_counts()
            .reset_index()
        )
        batch_df.columns = ["Update Batch", "Count"]

        st.dataframe(
            batch_df,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Rows Missing Original URL")

    missing_url_df = source_df[source_df["url"].astype(str).str.strip().eq("")].copy()

    if missing_url_df.empty:
        st.success("All rows have original source URLs.")
    else:
        health_columns = get_available_columns(
            missing_url_df,
            [
                "source_id",
                "title",
                "domain",
                "country",
                "category",
                "subcategory",
                "file_path",
                "added_at",
                "update_batch",
                "is_new",
                "is_latest_update",
                "summary",
                "keywords",
                "insights",
            ],
        )

        health_display_df = missing_url_df[health_columns].copy()

        st.dataframe(
            health_display_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Download rows missing URLs",
            data=health_display_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="rows_missing_urls.csv",
            mime="text/csv",
        )

    st.subheader("Column List")

    st.code("\n".join(source_df.columns.tolist()), language="text")
