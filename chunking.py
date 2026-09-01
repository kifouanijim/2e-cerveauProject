"""
Text chunking module for splitting long documents into manageable fragments.
Uses fixed-size chunks with overlap to preserve context at boundaries.
"""


def chunk_text(text, chunk_size, overlap):
    """
    Split text into fixed-size chunks with overlap.
    
    Args:
        text (str): The text to split
        chunk_size (int): Size of each chunk in characters
        overlap (int): Number of overlapping characters between consecutive chunks
    
    Returns:
        list: List of text chunks with overlap
    
    Example:
        chunks = chunk_text("Hello world example", chunk_size=10, overlap=3)
        # Returns chunks that share the last 3 characters of each chunk
        # with the first 3 characters of the next chunk
    """
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position for this chunk
        end = min(start + chunk_size, len(text))
        
        # Add the chunk
        chunks.append(text[start:end])
        
        # Move start position backward by overlap amount
        # This creates overlap between consecutive chunks
        start = end - overlap
        
        # If we're near the end and the remaining text is too small, break
        if end == len(text):
            break
    
    return chunks


if __name__ == "__main__":
    # Test with sample text
    sample_text = """Git est un système de gestion de versions distribué qui permet de suivre l'évolution 
d'un projet, de revenir en arrière si besoin, et de travailler à plusieurs sur le même code sans écraser le 
travail des autres. Ce guide couvre les commandes essentielles utilisées pendant les ateliers de la formation, 
notamment pour versionner le code des agents développés en Python. Git s'installe via le gestionnaire de paquets 
de votre système. Une fois installé, configurez votre identité, utilisée pour signer vos commits."""
    
    chunk_size = 150
    overlap = 30
    
    print(f"📝 Texte original : {len(sample_text)} caractères")
    print(f"⚙️ Paramètres : chunk_size={chunk_size}, overlap={overlap}")
    print("=" * 80)
    
    chunks = chunk_text(sample_text, chunk_size, overlap)
    
    print(f"📦 Nombre de chunks : {len(chunks)}\n")
    
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i + 1} (caractères {len(chunk)}) ---")
        print(f"{chunk}")
        print()
    
    # Verify overlap
    if len(chunks) > 1:
        print("=" * 80)
        print("🔍 Vérification du chevauchement :")
        for i in range(len(chunks) - 1):
            end_of_current = chunks[i][-overlap:]
            start_of_next = chunks[i + 1][:overlap]
            match = "✅" if end_of_current == start_of_next else "❌"
            print(f"{match} Chunk {i + 1} (fin) ↔ Chunk {i + 2} (début)")
            print(f"   Fin chunk {i + 1}   : '{end_of_current}'")
            print(f"   Début chunk {i + 2} : '{start_of_next}'")
            print()
