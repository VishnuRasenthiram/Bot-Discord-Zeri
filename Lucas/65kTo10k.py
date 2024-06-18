import os
from PIL import Image

# Définir les chemins des dossiers
input_folder = 'Lucas/Downloads/Webtoon-Downloader-master/src/haut'
output_folder = 'Lucas/Downloads/Webtoon-Downloader-master/src/10k'

# Créer le dossier de sortie s'il n'existe pas
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Hauteur maximale des sous-images
max_height = 9900

# Parcourir toutes les images dans le dossier d'entrée
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif')):
        image_path = os.path.join(input_folder, filename)
        with Image.open(image_path) as img:
            width, height = img.size
            if height > max_height:
                num_subimages = (height + max_height - 1) // max_height  # Calculer le nombre de sous-images
                for i in range(num_subimages):
                    upper = i * max_height
                    lower = min((i + 1) * max_height, height)
                    cropped_img = img.crop((0, upper, width, lower))
                    new_filename = f"{os.path.splitext(filename)[0]}_part{i+1}{os.path.splitext(filename)[1]}"
                    output_path = os.path.join(output_folder, new_filename)
                    cropped_img.save(output_path)
                    print(f'Sous-image {new_filename} enregistrée.')
            else:
                # Copier l'image sans la modifier si elle ne dépasse pas la hauteur
                output_path = os.path.join(output_folder, filename)
                img.save(output_path)
                print(f'{filename} n\'a pas été coupée et a été copiée.')