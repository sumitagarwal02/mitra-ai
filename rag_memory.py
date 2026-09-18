import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="reflections")

def store_reflection(doc_id: str, user_id: str, user_prompt: str, mood_analysis: str):
    text_content = f"User Input: {user_prompt} | Analysis: {mood_analysis}"
    collection.add(
        documents=[text_content],
        metadatas=[{"user_id": user_id}],
        ids=[doc_id]
    )

def retrieve_relevant_context(query: str, user_id: str, n_results: int = 2) -> str:
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"user_id": user_id}
        )
        if results and results.get("documents") and results["documents"][0]:
            return "\n".join(results["documents"][0])
        return "No prior relevant reflections found."
    except Exception:
        return "No prior relevant reflections found."