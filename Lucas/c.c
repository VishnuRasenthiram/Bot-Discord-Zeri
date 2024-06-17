#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int x, y, z;
} Point;

Point* read_points_from_file(const char* filename, int* num_points) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        perror("Could not open file");
        exit(EXIT_FAILURE);
    }

    int capacity = 10;
    *num_points = 0;
    Point* points = malloc(capacity * sizeof(Point));

    while (fscanf(file, "%d %d %d", &points[*num_points].x, &points[*num_points].y, &points[*num_points].z) == 3) {
        (*num_points)++;
        if (*num_points >= capacity) {
            capacity *= 2;
            points = realloc(points, capacity * sizeof(Point));
        }
    }

    fclose(file);
    return points;
}

bool point_exists(Point* points, int num_points, int x, int y, int z) {
    for (int i = 0; i < num_points; ++i) {
        if (points[i].x == x && points[i].y == y && points[i].z == z) {
            return true;
        }
    }
    return false;
}

Point* find_parallelepiped(Point* points, int num_points) {
    for (int i = 0; i < num_points; ++i) {
        int x1 = points[i].x, y1 = points[i].y, z1 = points[i].z;
        for (int j = i + 1; j < num_points; ++j) {
            int x2 = points[j].x, y2 = points[j].y, z2 = points[j].z;
            if (x1 != x2 && y1 != y2 && z1 != z2) {
                if (point_exists(points, num_points, x1, y1, z2) &&
                    point_exists(points, num_points, x1, y2, z1) &&
                    point_exists(points, num_points, x2, y1, z1) &&
                    point_exists(points, num_points, x2, y2, z2) &&
                    point_exists(points, num_points, x1, y2, z2) &&
                    point_exists(points, num_points, x2, y1, z2) &&
                    point_exists(points, num_points, x2, y2, z1)) {

                    Point* parallelepiped = malloc(8 * sizeof(Point));
                    parallelepiped[0] = (Point){x1, y1, z1};
                    parallelepiped[1] = (Point){x1, y1, z2};
                    parallelepiped[2] = (Point){x1, y2, z1};
                    parallelepiped[3] = (Point){x1, y2, z2};
                    parallelepiped[4] = (Point){x2, y1, z1};
                    parallelepiped[5] = (Point){x2, y1, z2};
                    parallelepiped[6] = (Point){x2, y2, z1};
                    parallelepiped[7] = (Point){x2, y2, z2};
                    return parallelepiped;
                }
            }
        }
    }
    return NULL;
}

int main() {
    const char* filename = "1-6.txt";
    int num_points;
    Point* points = read_points_from_file(filename, &num_points);

    printf("Lecture des points terminée.\n");

    Point* parallelepiped = find_parallelepiped(points, num_points);

    if (parallelepiped) {
        printf("Parallélépipède trouvé :\n");
        for (int i = 0; i < 8; ++i) {
            printf("(%d, %d, %d)\n", parallelepiped[i].x, parallelepiped[i].y, parallelepiped[i].z);
        }
        free(parallelepiped);
    } else {
        printf("Aucun parallélépipède trouvé\n");
    }

    free(points);
    return 0;
}