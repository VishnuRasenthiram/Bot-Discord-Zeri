import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def find_parallelepiped(points_chunk):
    points_set = set(points)
    n = len(points)
    
    for i in range(n):
        x1, y1, z1 = points[i]
        for j in range(i + 1, n):
            x2, y2, z2 = points[j]
            if x1 != x2 and y1 != y2 and z1 != z2:
                if ((x1, y1, z2) in points_set and (x1, y2, z1) in points_set and
                    (x2, y1, z1) in points_set and (x2, y2, z2) in points_set and
                    (x1, y2, z2) in points_set and (x2, y1, z2) in points_set and
                    (x2, y2, z1) in points_set):
                    return [
                        (x1, y1, z1), (x1, y1, z2), (x1, y2, z1), (x1, y2, z2),
                        (x2, y1, z1), (x2, y1, z2), (x2, y2, z1), (x2, y2, z2)
                    ]
    
    return None

def read_points_from_file(filename):
    points = []
    with open(filename, 'r') as file:
        for line in file:
            x, y, z = map(int, line.split())
            points.append((x, y, z))
    return points

# Lecture des points à partir du fichier 'points.txt'
filename = '1-6.txt'
start_time = time.time()
points = read_points_from_file(filename)
print(f"Lecture des points terminée en {time.time() - start_time:.2f} secondes.")

# Découper les points en chunks pour le traitement parallèle
num_chunks = 10  # Nombre de chunks à traiter
chunk_size = len(points) // num_chunks
point_chunks = [points[i:i + chunk_size] for i in range(0, len(points), chunk_size)]

# Fonction pour traiter chaque chunk en parallèle
def process_chunk(chunk):
    return find_parallelepiped(chunk)

start_time = time.time()
parallelepiped = None

# Utilisation de ThreadPoolExecutor pour exécuter les chunks en parallèle
with ThreadPoolExecutor(max_workers=num_chunks) as executor:
    futures = [executor.submit(process_chunk, chunk) for chunk in point_chunks]
    results = []
    with tqdm(total=len(point_chunks)) as pbar:
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            pbar.update(1)
            if result:
                parallelepiped = result
                break

print(f"Recherche du parallélépipède terminée en {time.time() - start_time:.2f} secondes.")

# Afficher les points du parallélépipède sur un graphique 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

if parallelepiped:
    x_points, y_points, z_points = zip(*parallelepiped)
    ax.scatter(x_points, y_points, z_points, s=100, label='Points du parallélépipède', c='r')  # Utiliser une taille de point plus grande pour les mettre en évidence

    for point in parallelepiped:
        print(f"{point[0]} {point[1]} {point[2]}")
    
    # Dessiner le parallélépipède
    edges = [
        [parallelepiped[0], parallelepiped[1], parallelepiped[3], parallelepiped[2]],
        [parallelepiped[4], parallelepiped[5], parallelepiped[7], parallelepiped[6]],
        [parallelepiped[0], parallelepiped[1], parallelepiped[5], parallelepiped[4]],
        [parallelepiped[2], parallelepiped[3], parallelepiped[7], parallelepiped[6]],
        [parallelepiped[0], parallelepiped[2], parallelepiped[6], parallelepiped[4]],
        [parallelepiped[1], parallelepiped[3], parallelepiped[7], parallelepiped[5]],
    ]
    ax.add_collection3d(Poly3DCollection(edges, facecolors='cyan', linewidths=1, edgecolors='r', alpha=.25))
else:
    print("Aucun parallélépipède trouvé")

# Configuration du graphique
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Points et Parallélépipède')
plt.legend()
plt.show()
