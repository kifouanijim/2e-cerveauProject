"""
Extraction de texte à partir de fichiers PDF.

Utilise PyMuPDF (fitz) pour extraire le texte page par page.
"""
import fitz  # PyMuPDF
from pathlib import Path
import sys


def extract_text(pdf_path):
    """
    Extrait le texte brut d'un fichier PDF.
    
    Args:
        pdf_path (str ou Path): Chemin vers le fichier PDF
        
    Returns:
        str: Texte extrait du PDF, sans mise en forme
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"Le fichier {pdf_path} n'existe pas.")
    
    if not pdf_path.suffix.lower() == ".pdf":
        raise ValueError(f"Le fichier doit être un PDF, pas {pdf_path.suffix}")
    
    text = ""
    
    try:
        # Ouvrir le PDF
        with fitz.open(pdf_path) as pdf:
            num_pages = pdf.page_count
            print(f"📄 Extraction du PDF : {pdf_path.name}")
            print(f"📊 Nombre de pages : {num_pages}\n")
            
            # Parcourir chaque page
            for page_num in range(num_pages):
                page = pdf[page_num]
                page_text = page.get_text()
                
                # Ajouter le texte de la page
                text += f"--- Page {page_num + 1} ---\n"
                text += page_text
                text += "\n"
    
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'extraction du PDF : {e}")
    
    return text


if __name__ == "__main__":
    documents_dir = Path(__file__).parent / "documents"
    pdf_files = [Path(sys.argv[1])] if len(sys.argv) > 1 else sorted(documents_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ Aucun fichier PDF trouvé dans : {documents_dir}")
        raise SystemExit(1)

    for pdf_file in pdf_files:
        try:
            extracted_text = extract_text(pdf_file)
            print("✅ Extraction réussie !\n")
            print("=" * 80)
            print(extracted_text[:1000])
            print("=" * 80)
            print(f"\n📝 Longueur totale du texte : {len(extracted_text)} caractères\n")
        except Exception as e:
            print(f"❌ Erreur pour {pdf_file}: {e}")
