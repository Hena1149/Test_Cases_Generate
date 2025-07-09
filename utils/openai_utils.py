import requests
import json
from typing import List
from tqdm import tqdm

def split_text(text: str, chunk_size: int = 4000) -> List[str]:
    """Découpe le texte en morceaux."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_rules(text: str, api_key: str, endpoint: str, model: str) -> List[str]:
    """Génère les règles de gestion avec OpenAI."""
    chunks = split_text(text)
    all_rules = []
    
    for chunk in tqdm(chunks, desc="Génération des règles"):
        url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        prompt = (
            "À partir du texte suivant du cahier des charges, génère une liste claire et concise de règles de gestion métier. "
            "Chaque règle doit être numérotée et rédigée de manière exploitable pour un analyste ou développeur. "
            "Base-toi uniquement sur le contenu :\n\n"
            f"{chunk}"
        )
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 3000
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            rules_text = response.json()["choices"][0]["message"]["content"]
            all_rules.extend(rules_text.split('\n'))
        except Exception as e:
            print(f"Erreur lors de la génération des règles : {e}")
    
    return [rule.strip() for rule in all_rules if rule.strip()]

def generate_checkpoints(rules: List[str], api_key: str, endpoint: str, model: str) -> List[str]:
    """Génère les points de contrôle à partir des règles."""
    checkpoints = []
    batch_size = 5
    
    progress_bar = tqdm(total=len(rules), desc="Génération des points de contrôle")
    
    for i in range(0, len(rules), batch_size):
        batch = rules[i:i + batch_size]
        batch_text = "\n".join(batch)
        
        url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        prompt = (
            "À partir des règles de gestion suivantes, génère une liste de points de contrôle. "
            "Chaque point doit commencer par un verbe d'action comme : Vérifier que..., S'assurer que..., Contrôler si..., etc.\n\n"
            f"{batch_text}\n\n"
            "Format attendu :\n"
            "1. [Point de contrôle]\n"
            "2. [Point de contrôle]\n"
            "..."
        )
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            cp_text = response.json()["choices"][0]["message"]["content"]
            checkpoints.extend([line.strip() for line in cp_text.split('\n') if line.strip()])
            progress_bar.update(len(batch))
        except Exception as e:
            print(f"Erreur lors de la génération des points de contrôle : {e}")
    
    progress_bar.close()
    return checkpoints

def generate_test_cases(checkpoints: List[str], api_key: str, endpoint: str, model: str) -> List[str]:
    """Génère les cas de test détaillés."""
    test_cases = []
    
    progress_bar = tqdm(total=len(checkpoints), desc="Génération des cas de test")
    
    for cp in checkpoints:
        url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key
        }
        prompt = (
            f"À partir du point de contrôle suivant et il faut savoir qu'un point de contrôle peut contenir plusieurs cas de test, alors il faut générer tout les cas de test de ce point de contrôle :\n'{cp}'\n"
            "Génère un cas de test détaillé avec les éléments suivants :\n"
            "### ID du test\n"
            "### Titre\n"
            "### Préconditions\n"
            "### Données d'entrée\n"
            "### Étapes\n"
            "### Résultat attendu\n\n"
            "Formate la réponse en Markdown."
        )
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            test_case = response.json()["choices"][0]["message"]["content"]
            test_cases.append(test_case)
            progress_bar.update(1)
        except Exception as e:
            print(f"Erreur lors de la génération du cas de test pour '{cp[:30]}...': {e}")
    
    progress_bar.close()
    return test_cases