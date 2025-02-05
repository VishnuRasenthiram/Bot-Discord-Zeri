from google import genai
from google.genai import types
from pydantic import BaseModel




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
