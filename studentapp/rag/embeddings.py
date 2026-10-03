import os
import time

try:
    from django.conf import settings  # pyright: ignore[reportMissingModuleSource]
except ImportError:
    settings = None

try:
    from google import genai  # pyright: ignore[reportMissingImports]
    from google.genai import types  # pyright: ignore[reportMissingImports]
except ImportError:
    genai = None
    types = None

#gemini client
api_key = getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if genai is not None and api_key else None


def _get_client():
    if client is None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        raise ImportError("google-genai package is required for embeddings.")
    return client


def embed_text(text):
    client = _get_client()
    result = client.models.embed_content(
        model = "gemini-embedding-2",
        contents=[
            types.Content(
                parts=[
                    types.Part.from_text(text=text)
                ] 
            )
        ],
        config=types.EmbedContentConfig(
            output_dimensionality=768
        )
    )

    return result.embeddings[0].values

def embed_texts(texts):

    #store all genearted vectors here
    all_embeddings= []

    batch_size = 100

    for start in range(0, len(texts), batch_size):

        #get the current batch of text chunk
        batch = texts[start:start + batch_size]

        #convert each text into the format expected by gemini
        contents = [
            types.Content(
                parts=[
                    types.Part.from_text(text=text)
                ]
            )
            for text in batch
        ]

        max_retries = 3

        for attempt in range(max_retries):
            try:
                #send the batch to gemini and generate embeddings. 
                result = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=contents,
                    config=types.EmbedContentConfig(
                        output_dimensionality=768
                    )
                )
                break
            except Exception as e:
                error_message = str(e)

                #raise immedietly for errors other than rate limits
                if "429" not in error_message:
                    raise

                #stop after  the final  retry
                if attempt == max_retries - 1:
                    raise

                wait_time = 20 * (attempt + 1)

                print(
                    f"Gemini rate limit reached. "
                    f"Retring in  {wait_time} seconds..."
                )
                time.sleep(wait_time)

        #Extract vectors from gemini's response
        batch_embeddings = [
            embedding.values
            for embedding in result.embeddings
        ] 

        #add this batch's vectors to the complete list
        all_embeddings.extend(batch_embeddings)

        #Giving some time for the api before sending next batch
        if start + batch_size < len(texts):
            time.sleep(2)
            
    return all_embeddings