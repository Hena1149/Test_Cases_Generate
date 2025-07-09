import fitz  # PyMuPDF
import docx
from typing import List
import pandas as pd
from io import BytesIO
import re

def extract_text_from_pdf(file_path: str) -> str:
    """Extrait le texte d'un fichier PDF."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extrait le texte d'un fichier Word."""
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path: str) -> str:
    """Extrait le texte d'un fichier TXT."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def process_uploaded_file(file_path: str) -> str:
    """Traite le fichier uploadé selon son type."""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Type de fichier non supporté. Veuillez uploader un PDF, DOCX ou TXT.")

def export_to_excel(data: List[str], sheet_name: str = "Data") -> BytesIO:
    """Convertit une liste de textes en fichier Excel."""
    output = BytesIO()
    df = pd.DataFrame(data, columns=["Contenu"])
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        worksheet.set_column('A:A', 50)  # Ajuste la largeur de colonne
    
    output.seek(0)
    return output

def export_test_cases_to_excel(test_cases: List[str]) -> BytesIO:
    """Exporte les cas de test structurés vers Excel."""
    output = BytesIO()
    
    # Préparation des données
    data = []
    for i, test_case in enumerate(test_cases, 1):
        case_data = {
            "ID": f"TEST-{i}",
            "Titre": "",
            "Préconditions": "",
            "Données d'entrée": "",
            "Étapes": "",
            "Résultat attendu": ""
        }
        
        # Extraction des sections
        sections = re.split(r'###\s+', test_case)
        for section in sections:
            if "Titre" in section:
                case_data["Titre"] = section.replace("Titre", "").strip()
            elif "Préconditions" in section:
                case_data["Préconditions"] = section.replace("Préconditions", "").strip()
            elif "Données d'entrée" in section:
                case_data["Données d'entrée"] = section.replace("Données d'entrée", "").strip()
            elif "Étapes" in section:
                case_data["Étapes"] = section.replace("Étapes", "").strip()
            elif "Résultat attendu" in section:
                case_data["Résultat attendu"] = section.replace("Résultat attendu", "").strip()
        
        data.append(case_data)
    
    # Création du DataFrame
    df = pd.DataFrame(data)
    
    # Écriture Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Cas_de_test", index=False)
        
        # Formatage
        workbook = writer.book
        worksheet = writer.sheets["Cas_de_test"]
        
        # Ajustement des largeurs de colonnes
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    
    output.seek(0)
    return output
