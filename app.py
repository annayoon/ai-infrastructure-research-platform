from openai import OpenAI
import streamlit as st
import pandas as pd
import chromadb

st.set_page_config(
    page_title="AI Infrastructure Research Portal",
    layout="wide"
)

st.title("AI Infrastructure Research Portal")
if question:

    try:

        client = OpenAI()

        db = chromadb.PersistentClient(
            path="vector_db"
        )
# =====================
# Metadata
# =====================

st.header("Source Index")

try:
    df = pd.read_csv("metadata/source_index.csv")

    st.dataframe(df)

except Exception as e:
    st.error(e)

# =====================
# Summaries
# =====================

st.header("Document Summaries")

try:
    summaries = pd.read_csv("metadata/summaries.csv")

    st.dataframe(summaries)

except Exception as e:
    st.error(e)

# =====================
# Insights
# =====================

st.header("Strategic Insights")

try:
    insights = pd.read_csv("metadata/insights.csv")

    st.dataframe(insights)

except Exception as e:
    st.error(e)

# =====================
# Knowledge Graph
# =====================

st.header("Knowledge Graph")

try:
    kg = pd.read_csv("metadata/knowledge_graph.csv")

    st.dataframe(kg)

except Exception as e:
    st.error(e)

# =====================
# Semantic Search
# =====================

st.header("Semantic Search")

query = st.text_input(
    "Search your research corpus"
)

if query:

    try:

        client = chromadb.PersistentClient(
            path="vector_db"
        )

        collection = client.get_collection(
            "research_corpus"
        )

        results = collection.query(
            query_texts=[query],
            n_results=5
        )

        for i in range(len(results["documents"][0])):

            st.subheader(
                results["metadatas"][0][i]["file"]
            )

            st.write(
                results["documents"][0][i][:2000]
            )

    except Exception as e:
        st.error(e)

# =====================
# AI Research Analyst
# =====================

st.header("AI Research Analyst")

question = st.text_area(
    "Ask a strategic infrastructure question"
)

if question:

    try:

        db = chromadb.PersistentClient(
            path="vector_db"
        )

        collection = db.get_collection(
            "research_corpus"
        )

        results = collection.query(
            query_texts=[question],
            n_results=5
        )

        context = ""

        for doc in results["documents"][0]:
            context += doc + "\n\n"

        prompt = f"""
You are an AI infrastructure strategic analyst.

Answer the question ONLY using the provided research context.

Question:
{question}

Research Context:
{context}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strategic AI infrastructure analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        st.subheader("AI Analysis")

        st.write(
            response.choices[0].message.content
        )

    except Exception as e:

        st.error(e)        