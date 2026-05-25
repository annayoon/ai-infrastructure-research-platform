import os
from pathlib import Path

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

    .metric-card {
        padding: 1rem;
        border-radius: 0.75rem;
        background-color: #161b22;
        border: 1px solid #30363d;
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
    Convert NaN, None, 'None', 'nan' values to empty string.
    This prevents the UI from showing ugly 'None' text.
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
    If the file does not exist, return an empty DataFrame.
    """
    if not SOURCE_INDEX_PATH.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(SOURCE_INDEX_PATH)
    except Exception as e:
        st.error(f"Failed to read source index: {e}")
        return pd.DataFrame()

    # Normalize column names
    df.columns = [str(col).strip() for col in df.columns]

    # Ensure expected columns exist
    expected_columns = [
        "title",
        "category",
        "source",
        "publisher",
        "url",
        "file_path",
        "local_path",
        "query",
        "date",
        "notes",
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""

    # Clean empty-looking values
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


def resolve_local_file_path(row):
    """
    Resolve local file path from source index row.
    Supports file_path and local_path.
    """
    for col in ["local_path", "file_path"]:
        value = row.get(col, "")
        value = normalize_empty(value)

        if not value:
            continue

        candidate = Path(value)

        if not candidate.is_absolute():
            candidate = BASE_DIR / candidate

        if candidate.exists():
            return candidate

    return None


# =========================================================
# Header
# =========================================================

st.title("AI Infrastructure Research Portal")

st.markdown(
    """
    <div class="small-caption">
    Research portal for AI infrastructure, data center, power generation,
    advanced technology campus, Alaska market validation, and public-source evidence tracking.
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
    else:
        url_count = 0
        category_count = 0
        corpus_count = len(list_corpus_files())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Sources", total_sources)
    col2.metric("Original URLs", int(url_count))
    col3.metric("Categorized Rows", int(category_count))
    col4.metric("Corpus Files", corpus_count)

    st.subheader("Recommended Workflow")

    st.markdown(
        """
        1. Use **Source Index** to check collected sources and open original URLs.
        2. Use **Corpus Search** to find evidence paragraphs inside collected text.
        3. Use **File Preview** to inspect downloaded or extracted local files.
        4. Use **Data Health Check** to identify missing URLs, missing titles, or incomplete metadata.
        """
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
        "Collected source metadata. The Original Source column opens the source URL when available."
    )

    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])

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

    keyword = filter_col3.text_input(
        "Keyword filter",
        placeholder="Search title, source, publisher, category, notes...",
    )

    view_df = source_df.copy()

    if selected_category != "All":
        view_df = view_df[view_df["category"] == selected_category]

    if only_with_url:
        view_df = view_df[view_df["url"].astype(str).str.strip().ne("")]

    if keyword.strip():
        keyword_lower = keyword.strip().lower()

        searchable_cols = [
            col
            for col in [
                "title",
                "category",
                "source",
                "publisher",
                "url",
                "query",
                "notes",
                "file_path",
                "local_path",
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
    "summary",
    "keywords",
    "insights",
    ]

    display_columns = get_available_columns(view_df, preferred_columns)

    display_df = view_df[display_columns].copy()

    # Rename only for display clarity
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
        placeholder="Example: Alaska power generation, data center, fiber, AI infrastructure...",
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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rows", total_rows)
    col2.metric("Missing URLs", int(missing_url))
    col3.metric("Missing Titles", int(missing_title))
    col4.metric("Missing Categories", int(missing_category))

    st.subheader("Rows Missing Original URL")

    missing_url_df = source_df[source_df["url"].astype(str).str.strip().eq("")].copy()

    if missing_url_df.empty:
        st.success("All rows have original source URLs.")
    else:
        health_columns = get_available_columns(
            missing_url_df,
            [
                "title",
                "category",
                "source",
                "publisher",
                "query",
                "file_path",
                "local_path",
                "notes",
            ],
        )

        st.dataframe(
            missing_url_df[health_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Download rows missing URLs",
            data=missing_url_df[health_columns].to_csv(index=False).encode("utf-8-sig"),
            file_name="rows_missing_urls.csv",
            mime="text/csv",
        )

    st.subheader("Column List")

    st.code("\n".join(source_df.columns.tolist()), language="text")