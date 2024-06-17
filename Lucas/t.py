import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import time
from collections import defaultdict
from tqdm import tqdm  # Pour la barre de progression
import numpy as np

def find_parallelepiped(points):
    points_set = set(points)
    pairs = defaultdict(list)
    
    for x, y, z in points:
        pairs[(x, y)].append(z)
        pairs[(x, z)].append(y)
        pairs[(y, z)].append(x)
    
    for (x1, y1, z1) in tqdm(points, desc="Recherche du parallélépipède"):
        for z2 in pairs[(x1, y1)]:
            if z1 != z2 and (x1, y1, z2) in points_set:
                for y2 in pairs[(x1, z1)]:
                    if y1 != y2 and (x1, y2, z1) in points_set:
                        for x2 in pairs[(y1, z1)]:
                            if x1 != x2 and (x2, y1, z1) in points_set:
                                if (x1, y2, z2) in points_set and (x2, y1, z2) in points_set \
                                   and (x2, y2, z1) in points_set and (x2, y2, z2) in points_set:
                                    return [
                                        (x1, y1, z1), (x1, y1, z2), (x1, y2, z1), (x1, y2, z2),
                                        (x2, y1, z1), (x2, y1, z2), (x2, y2, z1), (x2, y2, z2)
                                    ]
    return None

def read_points_from_file(filename):
    points = np.loadtxt(filename, dtype=int)
    return [tuple(point) for point in points]

# Lecture des points à partir du fichier 'points.txt'
filename = '3-6.txt'
start_time = time.time()
points = read_points_from_file(filename)
print(f"Lecture des points terminée en {time.time() - start_time:.2f} secondes.")

start_time = time.time()
parallelepiped = find_parallelepiped(points)
print(f"Recherche du parallélépipède terminée en {time.time() - start_time:.2f} secondes.")

# Afficher les points du parallélépipède sur un graphique 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

if parallelepiped:
    x_points, y_points, z_points = zip(*parallelepiped)
    ax.scatter(x_points, y_points, z_points, s=100, label='Points du parallélépipède', c='r')  # Utiliser une taille de point plus grande pour les mettre en évidence
    for point in parallelepiped:
        print(point)
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
