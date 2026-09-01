"""Build and query a local ChromaDB index of the project PDFs."""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from chunking import chunk_text
from extraction import extract_text


BASE_DIR = Path(__file__).parent
DOCUMENTS_DIR = BASE_DIR / "documents"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "documents"
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_index():
    """Extract, chunk, embed, and persist every PDF in ``documents/``."""
    pdf_files = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"Aucun fichier PDF trouve dans {DOCUMENTS_DIR}")

    documents = []
    metadatas = []
    ids = []

    for pdf_path in pdf_files:
        text = extract_text(pdf_path)
        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for chunk_number, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            documents.append(chunk)
            metadatas.append({"source": pdf_path.name, "chunk": chunk_number})
            ids.append(f"{pdf_path.stem}-{chunk_number}")

    if not documents:
        raise ValueError("Aucun texte exploitable n'a ete extrait des PDF")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    embeddings = _get_model().encode(documents).tolist()
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return collection.count()


def search(query, k=3):
    """Return the ``k`` chunks closest in meaning to ``query``."""
    if not query or not query.strip():
        raise ValueError("La question ne peut pas etre vide")
    if k < 1:
        raise ValueError("k doit etre superieur ou egal a 1")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as error:
        raise RuntimeError("L'index n'existe pas encore. Lancez build_index().") from error

    query_embedding = _get_model().encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []
    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        matches.append({"text": document, "metadata": metadata, "distance": distance})
    return matches


if __name__ == "__main__":
    print("Construction de l'index local...\n")
    count = build_index()
    print(f"Index construit : {count} fragments\n")

    queries = [
        "Qu'est-ce qu'un commit Git ?",
        "Comment résoudre un conflit dans Git ?",
        "Quelles sont les règles pédagogiques ?",
        "Quelle est la météo demain ?",
        "Comment réparer une plomberie domestique ?",
    ]
    for query in queries:
        print(f"Question : {query}")
        for number, result in enumerate(search(query, k=3), start=1):
            similarity = max(0.0, min(1.0, 1.0 - result["distance"]))
            print(
                f"--- Resultat {number} ({result['metadata']['source']}) "
                f"similarite={similarity:.4f} ---"
            )
            print(result["text"][:300].replace("\n", " "))
        print("=" * 80)
