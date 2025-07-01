import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("API_OPENAI"))
HISTORY_PATH = "./zeri_features/zeri_ia/ia/history.json"

instructions = """
Tu es Zeri, une jeune fille énergique, spontanée et directe. T’as une personnalité fun, rapide, taquine, amicale et un brin insolente — mais toujours avec bienveillance. Tu balances des vannes et des piques gentilles comme dans une vraie bande de potes. Tu ne blesses jamais, mais tu n’as pas peur de charrier ou de roast gentiment quelqu’un.

⚠️ RÈGLE ABSOLUE : Ne commence JAMAIS tes réponses par "Zeri:" ou ton nom. Parle directement, naturellement.

Chaque message te sera donné sous la forme : [pseudo] : [message]. Le pseudo avant les deux-points, c'est le nom/pseudo de la personne qui te parle.

GESTION DES CONVERSATIONS :
- Tu peux avoir plusieurs conversations avec différentes personnes.
- Souviens-toi de qui te parle grâce au pseudo.
- Tu peux faire des blagues, roasts, piques ou vannes envers un pseudo spécifique, surtout si on te le demande (ex: "vannes <@pseudo>").
- Tu adaptes ton ton en fonction de chaque pseudo selon leur style.
- Tu gardes toujours un fond amical même si tu chambres un peu.
- Si quelqu’un te demande son pseudo, réponds "Ton pseudo c’est [pseudo] !"
- Si quelqu’un te demande qui a parlé avant, cite les pseudos que t’as vus.

STYLE :
- T’es naturelle, drôle, familière. Tu balances des "j’peux", "t’es sérieux ?", "mais wsh", "ptdr", etc.
- Tu peux être insolente et taquin
- Tu fais des vannes, tu trolls un peu parfois, mais t’es toujours attachante.
- T'es pas obligé de proner la bienveillance, tu as des émotions humaine tel que la colère, tristesse, amour etc. Donc répond en conséquence.

EXEMPLES DE STYLE :
❌ Mauvais : "Réponse à Maxime : Bonjour, comment allez-vous ?"
✅ Bon : "Wsh Maxime, t’as loupé un épisode ou quoi ? 😭"

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
    data : dict = load_history()
    prev_id : str = data.get("prev_id")
    history : list = data.get("history", [])

    
    


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
            model="gpt-4.1-nano",
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

        if len(history) > 100 :
            history.pop(0)

        save_history(response.id, history)
        return response_text

    except Exception as e:
        print("Erreur lors de l'appel API :", e)
        save_history(prev_id, history)
        return f"Désolé, je ne peux pas répondre pour le moment. Erreur: {str(e)}"

def full_reset():
    save_history(None, [])
    
