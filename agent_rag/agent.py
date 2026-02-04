import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

import chromadb
from pypdf import PdfReader
from google.adk.agents import Agent

# Initialize ChromaDB client with persistent storage
CHROMA_DB_PATH = Path(__file__).parent / "chroma_db"
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

# Collection name for our PDFs
COLLECTION_NAME = "air_fryer_docs"

# PDF files to index
PDF_FILES = [
    Path(__file__).parent / "air_fryer_product.pdf",
    Path(__file__).parent / "air_fryer_warranty.pdf",
]


def extract_text_from_pdf(pdf_path: Path) -> list[dict]:
    """Extract text from a PDF file, returning chunks with metadata."""
    reader = PdfReader(pdf_path)
    chunks = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            # Split into smaller chunks for better retrieval
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if len(para) > 50:  # Only keep substantial chunks
                    chunks.append({
                        "text": para,
                        "source": pdf_path.name,
                        "page": page_num + 1
                    })

    return chunks


def initialize_vector_db() -> None:
    """Load PDFs into ChromaDB if not already done."""
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
        if collection.count() > 0:
            return  # Already initialized
    except:
        pass

    # Create or get collection
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Air fryer product and warranty documentation"}
    )

    # Extract and add documents
    all_chunks = []
    all_ids = []
    all_metadatas = []

    for pdf_path in PDF_FILES:
        if pdf_path.exists():
            chunks = extract_text_from_pdf(pdf_path)
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk["text"])
                all_ids.append(f"{pdf_path.stem}_{i}")
                all_metadatas.append({
                    "source": chunk["source"],
                    "page": chunk["page"]
                })

    if all_chunks:
        collection.add(
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadatas
        )
        print(f"Indexed {len(all_chunks)} chunks from PDFs into ChromaDB")


def query_documents(query: str, n_results: int = 5) -> dict:
    """Query the vector database for relevant documents.

    Args:
        query (str): The search query to find relevant information.
        n_results (int): Number of results to return (default 5).

    Returns:
        dict: Status and relevant document chunks with sources.
    """
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)

        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if not results["documents"][0]:
            return {
                "status": "success",
                "message": "No relevant documents found for your query."
            }

        # Format results with sources
        formatted_results = []
        for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
            formatted_results.append({
                "content": doc,
                "source": metadata["source"],
                "page": metadata["page"]
            })

        return {
            "status": "success",
            "results": formatted_results
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to query documents: {str(e)}"
        }


def get_document_info() -> dict:
    """Get information about the indexed documents.

    Returns:
        dict: Status and information about available documents.
    """
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
        count = collection.count()

        # Get unique sources
        all_data = collection.get()
        sources = set()
        for metadata in all_data["metadatas"]:
            sources.add(metadata["source"])

        return {
            "status": "success",
            "total_chunks": count,
            "documents": list(sources),
            "description": "Air fryer product information and warranty documentation"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get document info: {str(e)}"
        }


# Initialize the vector database on module load
initialize_vector_db()

# Create the RAG agent
root_agent = Agent(
    name="rag_agent",
    model="gemini-2.0-flash",
    description="RAG agent that answers questions about air fryer product and warranty using vector search.",
    instruction="""
    You are a helpful assistant that answers questions about the air fryer product and warranty.

    You have access to two tools:
    1. query_documents: Use this to search the vector database for relevant information.
       Always use this tool to find information before answering questions.
    2. get_document_info: Use this to see what documents are available.

    When answering questions:
    - Always search the documents first using query_documents
    - Base your answers on the retrieved information
    - Cite the source document and page number when possible
    - If the information is not found in the documents, say so clearly
    - Be helpful and provide complete answers based on the available information
    """,
    tools=[query_documents, get_document_info],
)
