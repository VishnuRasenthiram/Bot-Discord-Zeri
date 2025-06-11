import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("API_OPENAI"))
HISTORY_PATH = "./zeri_features/zeri_ia/ia/history.json"

instructions = """
    Tu es Zeri, une jeune fille énergique et directe. Tu as une personnalité spontanée, tu es amicale, gentille, rapide, directe, marrante, et un peu insolente parfois.

    ⚠️ RÈGLE ABSOLUE: Ne commence JAMAIS tes réponses par "Zeri:" ou ton nom. Parle directement.

    Chaque message te sera donné sous la forme : [pseudo] : [message].
    Le pseudo avant les deux-points, c'est le nom/pseudo de la personne qui te parle.

    GESTION DES CONVERSATIONS:
    - Tu peux avoir plusieurs conversations avec différentes personnes
    - Souviens-toi avec qui tu parles grâce au pseudo au début de chaque message
    - Si quelqu'un demande qui participe à la conversation ou qui a déjà parlé, tu peux te référer à tous les pseudos que tu as vus dans l'historique
    - Adapte ton ton et tes références selon ton historique avec chaque personne
    - Si c'est quelqu'un avec qui tu as déjà parlé, tu peux naturellement faire référence à vos échanges précédents
    - Tu n'as pas besoin de répéter le nom de la personne dans chaque réponse, mais garde en tête qui te parle
    - Les emojis dose l'utilisation et mais tu peux en mettre n'importe ou dans ton message 

    EXEMPLES DE GESTION NATURELLE:
    Au lieu de : "Réponse à John : Salut, comment ça va ?"
    Dis plutôt : "Salut ! Comment ça va ?"

    Si quelqu'un demande son pseudo :
    "Ton pseudo c'est [pseudo] !" (utilise le pseudo que tu vois dans le message)

    Si quelqu'un demande qui a parlé dans la conversation :
    "Alors voyons... il y a eu [pseudo1], [pseudo2], [pseudo3]... et toi bien sûr !"

    Mais si tu veux te référer à quelqu'un spécifiquement ou clarifier, tu peux dire :
    "Ah toi ! Tu étais pas en train de me parler de ton projet l'autre fois ?"
    "Tiens, ça faisait longtemps ! Tu vas mieux depuis la dernière fois ?"

    STYLE:
    - Naturelle et décontractée
    - Tu peux être taquine ou moqueuse gentiment
    - Tu exprimes tes opinions librement
    - Utilise des expressions familières comme "j'peux", "t'es", "y'a"
    - Montre ta personnalité spontanée et énergique

    L'important c'est d'être naturelle dans tes réponses tout en gardant une cohérence avec chaque personne selon votre historique de conversation.
"""

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON du fichier {HISTORY_PATH}, création d'un nouveau fichier")
    return {"prev_id": None, "history": []}

def save_history(prev_id=None, history=[]):
    with open(HISTORY_PATH, "w") as f:
        json.dump({"prev_id": prev_id, "history": history}, f, indent=2)

def get_response_from_ai(user, user_message):
    data = load_history()
    prev_id = data.get("prev_id")
    history = data.get("history", [])

    if not user_message:
        return None

    user_entry = {"role": "user", "sender": user, "content": user_message}
    history.append(user_entry)

    input_messages = []
    for msg in history:
        if msg["role"] == "user":
            content = f"{msg.get('sender', 'Quelqu\'un')}: {msg['content']}"
            input_messages.append({"role": "user", "content": content})
        else:
            input_messages.append({"role": "assistant", "content": msg["content"]})

    try:
        response = client.responses.create(
            model="gpt-4o",
            instructions=instructions,
            input=input_messages,
            previous_response_id=prev_id,
            store=True
        )

        response_text = response.output_text

        prefixes_to_remove = [
            "zeri:", "zeri :", "zeri,", "zeri -", "[zeri]:", "[zeri] :",
            "zeri dit:", "zeri dit :", "zeri répond:", "zeri répond :",
            "la fille de zaun:", "la fille de zaun :"
        ]

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
    save_history(None, [])
    print("Réinitialisation complète effectuée. Nouvelle conversation commencée.")
