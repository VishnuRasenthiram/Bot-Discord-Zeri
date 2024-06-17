from PIL import Image
import os
import re

def convert_jpg_to_png(input_path, output_path):
    image = Image.open(input_path)
    image.save(output_path, "PNG")

def batch_convert_jpg_to_png(input_folder, output_folder):
    files = os.listdir(input_folder)
    files.sort(key=lambda x: int(re.sub('\D', '', x)))  # Tri par ordre numérique
    for filename in files:
        if filename.endswith(".jpg"):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(output_folder, output_filename)
            if os.path.exists(output_path):
                os.remove(output_path)  # Supprime le fichier PNG existant
            convert_jpg_to_png(input_path, output_path)

# Exemple d'utilisation
input_folder = "C:/Users/theob/Downloads/Webtoon-Downloader-master (1)/Webtoon-Downloader-master/src/Lecteur_omniscient"
output_folder = "C:/Users/theob/Downloads/Webtoon-Downloader-master (1)/Webtoon-Downloader-master/src/Lecteur_omniscient"


batch_convert_jpg_to_png(input_folder, output_folder)
