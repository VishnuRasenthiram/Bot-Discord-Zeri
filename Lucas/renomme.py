import os
import re

def natural_sort_key(s):
    # Utilise une expression régulière pour extraire des segments de nombres dans le nom de fichier
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def rename_files_in_order(directory):
    # Récupérer la liste des fichiers dans le dossier
    files = os.listdir(directory)
    
    # Trier les fichiers par ordre naturel (numérique et alphabétique)
    files.sort(key=natural_sort_key)
    
    # Parcourir les fichiers et les renommer
    for index, filename in enumerate(files):
        # Obtenir l'extension du fichier
        file_extension = os.path.splitext(filename)[1]
        # Créer le nouveau nom de fichier
        new_filename = f"{index+1:03d}{file_extension}"
        # Obtenir le chemin complet des fichiers
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)
        # Renommer le fichier
        os.rename(old_file, new_file)
        print(f"Renamed: {filename} to {new_filename}")
# Exemple d'utilisation
directory_path = "C:\\Users\\theob\\Downloads\\Webtoon-Downloader-master (1)\\Webtoon-Downloader-master\\src\\Lecteur_omniscient"

rename_files_in_order(directory_path)
