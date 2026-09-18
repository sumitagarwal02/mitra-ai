import chromadb

# Initialize persistent ChromaDB vector store
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="mitra_reflections")

def store_reflection(checkin_id: str, user_input: str, mood_analysis: str):
    """Embeds and stores user reflection into ChromaDB vector database."""
    text_content = f"User Reflection: {user_input} | Insight: {mood_analysis}"
    collection.add(
        documents=[text_content],
        metadatas=[{"user_input": user_input, "analysis": mood_analysis}],
        ids=[checkin_id]
    )

def retrieve_relevant_context(user_input: str, n_results: int = 2) -> str:
    """Performs semantic similarity search to recall relevant past check-ins."""
    count = collection.count()
    if count == 0:
        return "No prior relevant reflections found."

    results = collection.query(
        query_texts=[user_input],
        n_results=min(n_results, count)
    )

    if not results or not results.get("documents") or not results["documents"][0]:
        return "No prior relevant reflections found."

    docs = results["documents"][0]
    return "\n---\n".join(docs)