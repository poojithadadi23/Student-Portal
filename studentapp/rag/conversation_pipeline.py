from studentapp.rag.embeddings import embed_text
from studentapp.rag.generator import generate_answer
from studentapp.rag.vector_store import search_chunks
from studentapp.rag.structured_retriever import (
    get_student_data,
    student_data_to_context
)

def ask_conversation(question, user, history):
    student_data = get_student_data(user)
    structured_context = student_data_to_context(
        student_data
    )

    #convert the user query into a vector
    #so that it can be compared with document vector
    query_vector = embed_text(question)
    
        #search chromadb for the most relevant
        #document chunk belonging to this student
    results = search_chunks(
        query_vector, 
        student_id=student_data["student_id"],
        n_results=3
    
    )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    
    #combine the retrived document chunks into one piece of context for gemini
    document_context = "\n\n".join(
        documents
    )

    #combine structure student data
        #and unstructured document data
    context = f"""
STRUCTURED STUDENT DATA:
    
{structured_context}
    
UNSTRUCTURES DOCUMENT DATA:
    
{document_context}
""" 
    history_text = ""

    for message in history:
        history_text += (
            f'{message["role"]}:'
            f'{message["content"]}\n'
        )

    conversation_prompt = f"""
You are a conversational AI Assistant
inside a student portal.

Use the provided student information
and document information to answer the 
user's question.

You also have access to the previous
conversation.

CONVERSATION_HISTORY:

{history_text}

RAG CONTEXT:

{context}

CURRENT QUESTION:

{question}

Instructions:
- Use only the provided context.
- Use conversation history when it helps
  understand the current question.
- Do not invent information.
- If the information is not available,
  say that you dont know.
- Return the answer using the required 
  structured format.  

""" 
    result = generate_answer(
        question=question,
        context=conversation_prompt

    )   
    response = result.model_dump()

    sources = []

    for metadata in metadatas:
        source = metadata.get("source")

        if source:
            sources.append({
                "document_id": metadata.get("document_id"),
                "source": source,
                "chunk_index": metadata.get("chunk_index")
            })
    response["sources"] =sources

    return response