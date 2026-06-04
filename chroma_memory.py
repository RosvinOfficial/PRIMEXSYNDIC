import chromadb
from config import settings
import time

class JarvisMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(name="jarvis_longterm_memory")

    def store_memory(self, user_id: str, user_input: str, response: str):
        """
        Saves structured text exchange to Vector Database.
        """
        memory_id = f"{user_id}_{int(time.time())}"
        combined_text = f"User statement: {user_input} | Your Response: {response}"
        
        self.collection.add(
            documents=[combined_text],
            metadatas=[{"user_id": user_id, "timestamp": time.time()}],
            ids=[memory_id]
        )

    def retrieve_memories(self, user_id: str, query: str, limit: int = 3) -> str:
        """
        Queries Chroma for context sentences similar to the user interaction.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={"user_id": user_id}
        )
        
        if results and 'documents' in results and results['documents']:
            return " ".join(results['documents'][0])
        return ""
