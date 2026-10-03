from studentapp.rag.embeddings import embed_text
from studentapp.rag.generator import generate_answer
from studentapp.rag.vector_store import search_chunks
from studentapp.rag.structured_retriever import (
    get_student_data,
    student_data_to_context
)


# Main RAG pipeline:
# Connect student data, document retrieval,
# and Gemini to generate the final answer
def ask_rag(question, user):

    # 1. Get the logged-in student's structured data
    student_data = get_student_data(user)

    structured_context = student_data_to_context(
        student_data
    )

    # 2. Convert the user's question into a vector
    # so it can be compared with document vectors
    query_vector = embed_text(question)

    # 3. Search ChromaDB for the most relevant
    # document chunks belonging to this student
    results = search_chunks(
        query_vector,
        student_id=student_data["student_id"],
        n_results=3
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # 4. Combine the retrieved document chunks
    # into one piece of context for Gemini
    document_context = "\n\n".join(
        documents
    )

    # 5. Combine structured student data
    # and unstructured document data
    context = f"""
STRUCTURED STUDENT DATA:

{structured_context}

UNSTRUCTURED DOCUMENT DATA:

{document_context}
"""

    # 6. Send the question and combined context
    # to Gemini to generate the final answer
    result = generate_answer(
        question,
        context
    )

    # 7. Extract source information from the
    # metadata of the retrieved chunks
    sources = []

    for metadata in metadatas:

        source = metadata.get("source")

        if source:
            sources.append({
                "document_id": metadata.get("document_id"),
                "source": source,
                "chunk_index": metadata.get("chunk_index")
            })

    # 8. Convert the Pydantic response into a dictionary
    # and attach the actual retrieved sources
    response = result.model_dump()

    response["sources"] = sources

    return response