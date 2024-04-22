from dotenv import load_dotenv

from rag.retriever import VectorRetriever

if __name__ == "__main__":
    load_dotenv()
    query = """
        Hello my id is: dbe92510-c33f-4ff7-9908-ee6356fe251f
        Could you please draft a LinkedIn post discussing RAG systems?
        I'm particularly interested in highlighting how RAG systems streamline project management processes and provide a clear visual representation of task statuses. 
        Additionally, if you could touch on any recent advancements or best practices in utilizing RAG systems for efficient project tracking, that would be fantastic. 
        Looking forward to sharing valuable insights with my professional network! 
        """
    retriever = VectorRetriever(query=query)
    hits = retriever.retrieve_top_k(3)
    result = retriever.rerank(hits=hits)
    print(result)
