import os
import numpy as np
from PIL import Image
from natsort import natsorted

def concatenate_images(folder_path, output_path):
    image_files = os.listdir(folder_path)
    image_files = natsorted(image_files)  # Tri des noms de fichiers de manière numérique
    images = []
    max_height = 0

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path)
        image = np.array(image)

        height = image.shape[0]
        if height > max_height:
            max_height = height

        images.append(image)

    adjusted_images = []
    for image in images:
        height_diff = max_height - image.shape[0]
        if height_diff > 0:
            padding = np.zeros((height_diff, image.shape[1], image.shape[2]), dtype=np.uint8)
            image = np.concatenate((image, padding))

        adjusted_images.append(image)

    concatenated_image = np.concatenate(adjusted_images)
    
    # Diviser et sauvegarder les segments si nécessaire
    max_dimension = 65500
    total_height = concatenated_image.shape[0]
    num_segments = (total_height + max_dimension - 1) // max_dimension

    for i in range(num_segments):
        start_row = i * max_dimension
        end_row = min(start_row + max_dimension, total_height)
        segment = concatenated_image[start_row:end_row]
        segment_image = Image.fromarray(segment)
        segment_output_path = f"{os.path.splitext(output_path)[0]}_part{i+1}.jpg"
        segment_image.save(segment_output_path)
        print(f"Saved segment {i+1} as {segment_output_path}")

# Exemple d'utilisation
folder_path = "./upscaled"
output_path = "image_concatenated.jpg"

concatenate_images(folder_path, output_path)
958