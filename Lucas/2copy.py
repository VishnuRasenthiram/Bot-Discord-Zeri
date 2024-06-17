import matplotlib.pyplot as plt
from collections import defaultdict

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))

def read_points(filename):
    points = set()
    with open(filename, 'r') as file:
        for line in file:
            x, y = map(int, line.split())
            point = Point(x, y)
            points.add(point)
    return points

def find_aligned_neighbors(points):
    aligned_neighbors_x = defaultdict(list)
    aligned_neighbors_y = defaultdict(list)

    for point in points:
        aligned_neighbors_x[point.x].append(point)
        aligned_neighbors_y[point.y].append(point)

    return aligned_neighbors_x, aligned_neighbors_y

def find_hexagon(points, aligned_neighbors_x, aligned_neighbors_y):
    points_list = list(points)
    points_set = set(points_list)
    for p1 in points_list:
        for p2 in aligned_neighbors_x[p1.x]:
            if p2 == p1 or p2.y <= p1.y:
                continue
            for p3 in aligned_neighbors_y[p2.y]:
                if p3 == p2 or p3 == p1 or p3.x <= p2.x:
                    continue
                for p4 in aligned_neighbors_x[p3.x]:
                    if p4 == p3 or p4 == p2 or p4 == p1 or p4.y <= p3.y:
                        continue
                    for p5 in aligned_neighbors_y[p4.y]:
                        if p5 == p4 or p5 == p3 or p5 == p2 or p5 == p1 or p5.x >= p4.x:
                            continue
                        for p6 in aligned_neighbors_x[p5.x]:
                            if p6 == p5 or p6 == p4 or p6 == p3 or p6 == p2 or p6 == p1 or p6.y >= p5.y:
                                continue
                            if p6.y == p1.y:
                                hexagon = [p1, p2, p3, p4, p5, p6]
                                return hexagon
    return None

def plot_points(points, hexagon=None):
    plt.figure(figsize=(8, 8))
    plt.scatter([point.x for point in points], [point.y for point in points], color='blue', s=5)
    if hexagon:
        hexagon.append(hexagon[0])  # Ajoutez le premier point à la fin pour fermer le hexagone
        plt.plot([point.x for point in hexagon], [point.y for point in hexagon], color='red')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Hexagon and Points')
    plt.grid(True)
    plt.show()

def main():
    filename = "2.1.txt"
    points = read_points(filename)
    aligned_neighbors_x, aligned_neighbors_y = find_aligned_neighbors(points)
    hexagon = find_hexagon(points, aligned_neighbors_x, aligned_neighbors_y)

    if hexagon:
        print("Hexagon found:", [str(point) for point in hexagon])
        plot_points(points, hexagon)
    else:
        print("No hexagon found.")
        plot_points(points)

if __name__ == "__main__":
    main()
