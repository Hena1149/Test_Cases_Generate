from typing import List, Set, Dict, Tuple  # Import des types pour les annotations
from difflib import SequenceMatcher
import re
import string
import spacy
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk
from collections import Counter

# Téléchargements NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Chargement du modèle spaCy
nlp = spacy.load("fr_core_news_sm")

def clean_text(text: str) -> List[str]:
    """Nettoie le texte et retourne les tokens."""
    # Mise en minuscule
    text = text.lower()
    
    # Suppression des éléments indésirables
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    
    # Lemmatisation et filtrage
    doc = nlp(text)
    cleaned_tokens = [
        token.lemma_ for token in doc
        if token.text not in stopwords.words('french')
        and token.text not in string.punctuation
        and not token.is_space
        and len(token.text) > 2
    ]
    return cleaned_tokens

def generate_wordcloud(text: str) -> plt.Figure:
    """Génère un nuage de mots à partir du texte."""
    tokens = clean_text(text)
    freq_dist = Counter(tokens)
    
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis'
    ).generate_from_frequencies(freq_dist)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

def is_similar(text1: str, text2: str, threshold: float = 0.85) -> bool:
    """Détermine si deux textes sont similaires."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio() >= threshold

def remove_duplicates(new_items: List[str], existing_items: List[str]) -> List[str]:
    """
    Supprime les doublons entre les nouveaux items et les items existants.
    
    Args:
        new_items: Liste des nouveaux points de contrôle générés
        existing_items: Liste des points de contrôle existants
        
    Returns:
        Liste filtrée sans doublons
    """
    # On combine les listes pour éliminer les doublons internes aussi
    all_items = new_items + existing_items
    unique_items = []
    
    for item in all_items:
        if not any(is_similar(item, existing) for existing in unique_items):
            unique_items.append(item)
    
    # On conserve l'ordre original pour les nouveaux items
    return [item for item in new_items if item in unique_items] + \
           [item for item in existing_items if item in unique_items]