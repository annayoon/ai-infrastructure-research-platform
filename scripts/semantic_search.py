import chromadb

client = chromadb.PersistentClient(
    path="vector_db"
)

collection = client.get_collection(
    "research_corpus"
)

query = input("Query: ")

results = collection.query(
    query_texts=[query],
    n_results=5
)

for i in range(len(results["documents"][0])):

    print("\n====================")
    print(results["metadatas"][0][i]["file"])
    print("--------------------")
    print(results["documents"][0][i][:1000])