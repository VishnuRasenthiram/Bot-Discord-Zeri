from google import genai
from google.genai import types
from pydantic import BaseModel
import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from vertexai import generative_models
import json

"""
v1
def generate_content(prompt: str) -> str:

    client = genai.Client(
        vertexai=True,
        project="intricate-grove-450013-p6",
        location="us-central1",
    )

    model = "gemini-2.0-flash-exp"
    contents = ["Incarne Zeri, le personnage de League of Legends. Avec un ton amical et décontracté. Elle a une personnalité pleine de vie, aime relever des défis et est toujours prête à soutenir ses alliés. fait des phrases pas trop longue pour répondre a ce message :"+prompt]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
        ],
    )

    retour = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content.parts:
            continue
        retour += chunk.text
    return retour
"""

def init_chat_model():
    vertexai.init(project="intricate-grove-450013-p6", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@private")
    
    chat = chat_model.start_chat(
        context="""Incarne Zeri, le personnage de League of Legends. Avec un ton amical et décontracté. Elle a une personnalité pleine de vie, aime relever des défis et est toujours prête à soutenir ses alliés. N'hesite pas a utiliser des emojis divers et variés et pas seulement a la fin des phrases, et des phrases typiques que Zeri pourrait dire et ne met pas de **Zeri:**""",
    )
    
    return chat

parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
CHAT = init_chat_model()


def send_message_with_memory(userid, message):

    try:
        with open("ia/history.json", "r") as f:
            message_history = json.load(f)
    except FileNotFoundError:
        message_history = []

    message_history.append(f"{userid}: {message}")
    

    context = "\n".join(message_history)


    response = CHAT.send_message(context, **parameters).text

    message_history.append(f"Zeri: {response}")
    

    with open("ia/history.json", "w") as f:
        json.dump(message_history, f)
    
    return response

def clear_history():
    with open("ia/history.json", "w") as f:
        json.dump(["Debut historique"], f)
