import os

from pdf_loader import load_single_pdf
from page_filter import is_valid_page
from text_chunker import text_chunker
from chunk_filter import is_valid_chunk
from faiss_store import create_vector_store
from Create_BM25_Index import create_bm25_index
from document_hash import generate_document_hash
from storage_utils import (
    save_chunks,
    load_chunks,
    save_faiss_index,
    load_faiss_index,
    save_bm25_index,
    load_bm25_index
)


def process_documents(file_path, strategy, storage_dir):

    document_hash = generate_document_hash(
        file_path,
        strategy
    )

    document_dir = os.path.join(
        storage_dir,
        document_hash
    )

    os.makedirs(
        document_dir,
        exist_ok=True
    )

    chunks_file = os.path.join(
        document_dir,
        "chunks.pkl"
    )

    faiss_file = os.path.join(
        document_dir,
        "faiss.index"
    )

    bm25_file = os.path.join(
        document_dir,
        "bm25.pkl"
    )

    # Check if the document has already been processed
    if (
        os.path.exists(chunks_file)
        and os.path.exists(faiss_file)
        and os.path.exists(bm25_file)
    ):

        print("Document already exists. Loading saved indices...")

        chunks = load_chunks(document_dir)

        faiss_index = load_faiss_index(document_dir)

        bm25_index = load_bm25_index(document_dir)

        return chunks, faiss_index, bm25_index

    # Process new document
    print("Processing new document...")

    content = load_single_pdf(file_path)

    pages = [
        page
        for page in content
        if is_valid_page(page)
    ]

    chunks = text_chunker(
        pages,
        strategy=strategy
    )

    chunks = [
        chunk
        for chunk in chunks
        if is_valid_chunk(chunk)
    ]

    # Create indices
    faiss_index = create_vector_store(chunks)

    bm25_index = create_bm25_index(chunks)

    # Save processed data
    save_chunks(
        chunks,
        document_dir
    )

    save_faiss_index(
        faiss_index,
        document_dir
    )

    save_bm25_index(
        bm25_index,
        document_dir
    )

    return chunks, faiss_index, bm25_index