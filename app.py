import streamlit as st
if question:

    try:

        # OpenAI client 생성 (lazy loading)
        client = OpenAI()

        # Vector DB 연결
        db = chromadb.PersistentClient(
            path="vector_db"
        )

        collection = db.get_collection(
            "research_corpus"
        )

        # Semantic retrieval
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