from PIL import Image
import os
import re

def convert_jpg_to_png(input_path, output_path):
    image = Image.open(input_path)
    image.save(output_path, "PNG")

def batch_convert_jpg_to_png(input_folder, output_folder):
    files = os.listdir(input_folder)
    files.sort(key=lambda x: int(re.sub(r'\D', '', x))) # Tri par ordre numérique
    for filename in files:
        if filename.endswith(".jpg"):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(output_folder, output_filename)
            if os.path.exists(output_path):
                os.remove(output_path)  # Supprime le fichier PNG existant
            convert_jpg_to_png(input_path, output_path)

# Exemple d'utilisation
input_folder = "Lucas/Downloads/Webtoon-Downloader-master/src/Tower_of_God"
output_folder = "Lucas/Downloads/Webtoon-Downloader-master/src/Tower_of_God"


batch_convert_jpg_to_png(input_folder, output_folder)
