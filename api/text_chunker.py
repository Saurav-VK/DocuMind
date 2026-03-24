from chunking_strategies import *

def text_chunker(pages , strategy = "recursive"):

    all_chunks = []
    
    chunker = ChunkingStrategies()
    
    for page in pages:
        if strategy == "token":
            chunks = chunker.token_text_splitter(page["text"])

        elif strategy == "sentence":
            chunks = chunker.sentence_transformer_token_text_splitter(page["text"])

        elif strategy == "semantic":
            chunks = chunker.semantic_chunker(page["text"])

        elif strategy == "recursive":
            chunks = chunker.recursive_character_text_splitter(page["text"])

        else:
            raise ValueError("Invalid Method")

        for chunk in chunks:
            all_chunks.append({"text" : chunk , "page" : page["page"] , "source" : page["source"]})

    return all_chunks

