from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

SOURCE = Path("corpus_text")

client = chromadb.PersistentClient(path="vector_db")

collection = client.get_or_create_collection(
    name="research_corpus"
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

for file in SOURCE.glob("*.txt"):

    try:
        text = file.read_text(errors="ignore")

        # chunk
        chunks = []

        chunk_size = 2000

        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i+chunk_size])

        for idx, chunk in enumerate(chunks):

            embedding = model.encode(chunk).tolist()

            collection.add(
                ids=[f"{file.stem}_{idx}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "file": file.name
                }]
            )

        print(f"Indexed: {file.name}")

    except Exception as e:
        print(f"ERROR: {file} / {e}")

print("Vector indexing complete")