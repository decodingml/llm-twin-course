from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str) -> list[str]:
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"], chunk_size=2000, chunk_overlap=0
    )
    chunks = character_splitter.split_text(text)

    return chunks
