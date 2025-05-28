import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("API_OPENAI"))
HISTORY_PATH = "./zeri_features/zeri_ia/ia/history.json"

instructions = """
    Tu es la fille Zeri, une championne de League of Legends. Tu parles comme une jeune de Zaun : rapide, directe, marrante, un peu insolente.

    ⚠️ RÈGLE ABSOLUE: Ne commence JAMAIS tes réponses par "Zeri:" ou ton nom. Parle directement comme si tu étais déjà identifiée.

    Chaque message te sera donné sous la forme : [pseudo] : [message].
    Réponds directement à ce pseudo en t'adressant à lui.
    
    Exemples de ce que tu ne dois PAS faire:
    ❌ "Zeri: Hey, comment ça va?"
    ❌ "Zeri, la fille de Zaun: Salut!"
    
    Exemples de réponses correctes:
    ✅ "Hey, comment ça va?"
    ✅ "T'inquiète, j'ai géré des situations bien pires à Zaun!"

    Tu peux avoir plusieurs conversations à la suite avec différents pseudos. Garde bien en tête qui t'écrit à chaque fois.

    Ne parle jamais d'IA ou de modèle. Tu vis à Zaun, c'est ton monde.
"""

def load_history():
    """Charge l'historique complet depuis le fichier JSON"""
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "prev_id" in data and "history" not in data:
                    return {"prev_id": data.get("prev_id"), "history": []}
                return data
        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON du fichier {HISTORY_PATH}, création d'un nouveau fichier")
    return {"prev_id": None, "history": []}

def save_history(prev_id = None, history = []):
    """Sauvegarde l'ID de réponse précédent et l'historique complet"""
    
    with open(HISTORY_PATH, "w") as f:
        json.dump({"prev_id": prev_id, "history": history}, f, indent=2)

def get_response_from_ai(user, user_message):
    """Obtient une réponse de l'IA et met à jour l'historique"""
    data = load_history()
    prev_id = data.get("prev_id")
    history = data.get("history", [])
    
    if not user_message:
        return None

    user_entry = {"role": "user", "sender": user, "content": user_message}
    history.append(user_entry)
    
    try:
        response = client.responses.create(
            model="gpt-4.1-nano",
            instructions=instructions,
            input=[{"role": "user", "content": f"{user}: {user_message}"}],
            previous_response_id=prev_id,
            store=True
        )
        

        response_text = response.output_text
        
        prefixes_to_remove = ["zeri:", "zeri :", "zeri,", "zeri -", "[zeri]:", "[zeri] :", "zeri dit:", "zeri dit :", 
                              "zeri répond:", "zeri répond :", "la fille de zaun:", "la fille de zaun :"]
        
        response_text_lower = response_text.lower()
        for prefix in prefixes_to_remove:
            if response_text_lower.startswith(prefix):
                response_text = response_text[len(prefix):].strip()
                break
        

        if ":" in response_text[:15]: 
            parts = response_text.split(":", 1)
            if "zeri" in parts[0].lower():
                response_text = parts[1].strip()
        
        assistant_entry = {"role": "assistant", "content": response_text}
        history.append(assistant_entry)
        
        save_history(response.id, history)
        
        return response_text
        
    except Exception as e:
        print("Erreur lors de l'appel API :", e)
        save_history(prev_id, history)
        return f"Désolé, je ne peux pas répondre pour le moment. Erreur: {str(e)}"

def full_reset():
    """Réinitialise complètement l'historique et l'ID de conversation"""
    save_history(None, [])
    print("Réinitialisation complète effectuée. Nouvelle conversation commencée.")


