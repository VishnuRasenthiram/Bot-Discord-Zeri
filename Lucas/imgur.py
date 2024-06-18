import requests
import os
import base64

# Remplacez par vos informations d'identification Imgur
client_id = "dbad42f279f3dc8"
access_token = "cae435fe74a38bc43d557077be1d40f7f9200982"

# Titre de l'album
album_title = "Mon album d'images"

# Création de l'album
headers = {
    "Authorization": f"Bearer {access_token}",
}


response = requests.post("https://api.imgur.com/3/album", headers=headers)

if response.status_code == 200:
    album_id = response.json()["data"]["id"]
    album_url = f"https://imgur.com/a/{album_id}"
    print(f"Album créé avec succès: {album_url}")
else:
    print(f"Erreur lors de la création de l'album: {response.status_code}")
    print(f"Contenu de la réponse: {response.content}")  # Debug log
    album_id = None

# Téléchargement des images vers l'album
def upload_image(image_path, album_id):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    with open(image_path, "rb") as image_file:
        print(f"Tentative d'upload de l'image: {image_path}")  # Debug log
        file_size = os.path.getsize(image_path)  # Debug log
        print(f"Taille du fichier: {file_size} octets")  # Debug log
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

        response = requests.post(
            "https://api.imgur.com/3/image",
            headers=headers,
            data={
                "image": image_data,
                "album": album_id,
                "type": "base64",
            },
        )

    if response.status_code == 200:
        print(f"Image téléchargée avec succès: {image_path}")
    else:
        print(f"Erreur lors du téléchargement de l'image: {image_path}")
        print(f"Code d'état de la réponse: {response.status_code}")  # Debug log
        print(f"Contenu de la réponse: {response.content}")  # Debug log

# Remplacez 'images_folder' par le chemin d'accès à votre dossier d'images
images_folder = "Lucas/10k"

if album_id:
    for image_path in os.listdir(images_folder):
        full_image_path = os.path.join(images_folder, image_path)
        if os.path.isfile(full_image_path):
            upload_image(full_image_path, album_id)
    # Afficher l'URL de l'album à la fin du script
    print(f"Album complet disponible à l'adresse : {album_url}")
else:
    print("L'album n'a pas pu être créé, donc les images ne seront pas téléchargées.")
