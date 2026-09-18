"""
Download required NLTK resources and optional spaCy model for the NLP pipeline.
"""
import sys
import nltk

RESOURCES = [
    'punkt',
    'punkt_tab',
    'averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng',
    'maxent_ne_chunker',
    'maxent_ne_chunker_tab',
    'words',
    'wordnet',
    'omw-1.4',
    'brown',
]

def download_nltk_resources():
    print("=" * 60)
    print("Downloading required NLTK datasets...")
    print("=" * 60)
    for res in RESOURCES:
        try:
            print(f"Downloading '{res}'...")
            nltk.download(res, quiet=True)
            print(f"  [OK] '{res}' ready.")
        except Exception as e:
            print(f"  [!] Warning: could not download '{res}': {e}")
    print("\nNLTK resources download completed.\n")

def download_spacy_model():
    try:
        import spacy
        print("Checking spaCy 'en_core_web_sm' model...")
        try:
            spacy.load("en_core_web_sm")
            print("  [OK] spaCy model 'en_core_web_sm' is already installed.")
        except Exception:
            print("Downloading 'en_core_web_sm' via requirements.txt is expected.")
    except ImportError:
        print("spaCy not installed yet; NLTK fallback mode is fully functional.")

if __name__ == "__main__":
    download_nltk_resources()
    download_spacy_model()
    print("all resources ready")
