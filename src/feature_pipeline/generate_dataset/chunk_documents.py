import re


def chunk_documents(documents: list[str], min_length: int = 1000, max_length: int = 2000):
    chunked_documents = []
    for document in documents:
        chunks = extract_substrings(document, min_length=min_length, max_length=max_length)
        chunked_documents.extend(chunks)
        
    return chunked_documents

def extract_substrings(
    text: str, min_length: int = 1000, max_length: int = 2000
) -> list[str]:
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s", text)

    extracts = []
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + " "
        else:
            if len(current_chunk) >= min_length:
                extracts.append(current_chunk.strip())
            current_chunk = sentence + " "

    if len(current_chunk) >= min_length:
        extracts.append(current_chunk.strip())

    return extracts
