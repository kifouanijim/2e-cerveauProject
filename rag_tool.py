"""Tool for retrieving relevant passages from the local PDF documentation."""

import re
import unicodedata

from chunking import chunk_text
from extraction import extract_text
from vector_store import CHUNK_OVERLAP, CHUNK_SIZE, DOCUMENTS_DIR, search


SIMILARITY_THRESHOLD = 0.10
NO_RELEVANT_PASSAGE = "Aucun passage pertinent n'a ete trouve dans la documentation locale."


def _similarity(result):
    """Read a similarity score, converting the current Chroma distance format."""
    if "similarity" in result:
        return max(0.0, min(1.0, float(result["similarity"])))

    distance = float(result.get("distance", 1.0))
    return max(0.0, min(1.0, 1.0 - distance))


def _has_lexical_match(question, text):
    """Keep a passage when several meaningful question terms occur in it."""
    def normalize(value):
        return "".join(
            character
            for character in unicodedata.normalize("NFD", value.lower())
            if unicodedata.category(character) != "Mn"
        )

    stopwords = {
        "quel", "quelle", "quels", "quelles", "est", "sont", "le", "la",
        "les", "un", "une", "des", "de", "du", "dans", "pour", "sur",
        "avec", "comment", "et", "ou", "a", "au", "aux", "ce", "cette",
    }
    question_terms = {
        term for term in re.findall(r"[a-z0-9]+", normalize(question))
        if len(term) > 3 and term not in stopwords
    }
    text_terms = set(re.findall(r"[a-z0-9]+", normalize(text)))
    return len(question_terms & text_terms) >= 2


def _search_all_local_documents(question):
    """Find matching passages by scanning every local PDF as a fallback."""
    passages = []
    for pdf_path in sorted(DOCUMENTS_DIR.glob("*.pdf")):
        text = extract_text(pdf_path)
        for chunk in chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP):
            if chunk.strip() and _has_lexical_match(question, chunk):
                passages.append(f"[{pdf_path.name}]\n{_focus_passage(question, chunk)}")
    return passages


def _clean_passage(text):
    """Remove extraction markers and normalize whitespace in a passage."""
    text = re.sub(r"--- Page \d+ ---", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _focus_passage(question, text):
    """Keep complete sentences that directly match the question."""
    cleaned = _clean_passage(text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    matching = [sentence for sentence in sentences if _has_lexical_match(question, sentence)]
    return " ".join(matching[:3]) if matching else cleaned


def search_documentation(question):
    """Return relevant local documentation, or a refusal when none is close enough."""
    results = search(question, k=3)
    if not results:
        return NO_RELEVANT_PASSAGE

    relevant_results = [
        result
        for result in results
        if _similarity(result) >= SIMILARITY_THRESHOLD
        or _has_lexical_match(question, result["text"])
    ]
    if not relevant_results:
        fallback_passages = _search_all_local_documents(question)
        if not fallback_passages:
            return NO_RELEVANT_PASSAGE
        return "\n\n".join(fallback_passages[:1])

    passages = []
    for result in relevant_results[:1]:
        source = result.get("metadata", {}).get("source", "documentation locale")
        passages.append(f"[{source}]\n{_focus_passage(question, result['text'])}")
    return "\n\n".join(passages)


if __name__ == "__main__":
    questions = [
        "Qu'est-ce qu'un commit Git ?",
        "Comment regler un probleme de plomberie dans une maison ?",
    ]
    for question in questions:
        print(f"Question : {question}")
        print(search_documentation(question))
        print("=" * 80)
