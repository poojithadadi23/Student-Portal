import re
def split_into_sentences(text):
    #clear extra spaces and new lines
    text = re.sub(
        r'\s+',
        ' ',
        text 
    ).strip()

    if not text:
        return []
    
    #split text after .,! or
    sentences = re.split(
        r'(?<=[.!?])\s+',
        text

    )
    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()

    ]

#split documents based on context aware
def split_text(
    text,
    chunk_size = 1000,
    overlap_sentences = 2
):
    #seperate document into paragraph
    paragraphs = re.split(
        r'\n\s*\n',
        text
    )

    paragraphs = [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]

    chunks = []

    #build chunk based on sentence by sentence
    current_sentences = []
    current_length = 0
    for paragraph in paragraphs:
        sentences = split_into_sentences(
            paragraph
        )

        for sentence in sentences:
            sentence_length = len(sentence)
            if (
                current_sentences
                and 
                current_length + sentence_length
                > chunk_size
            ):
                chunks.append(
                    " ".join(current_sentences)
                )

                #keep the last sentences as overlap for the next chunk

                current_sentences = (
                    current_sentences[
                        -overlap_sentences:

                    ]
                )
                current_length = sum(
                    len(s)
                    for s in current_sentences

                )
            current_sentences.append(
                sentence
            )

            current_length += sentence_length

    #add the final remaining chunk
    if current_sentences:
        chunks.append(
            " ".join(current_sentences)
        )             

    return chunks