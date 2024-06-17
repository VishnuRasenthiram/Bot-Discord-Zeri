const fs = require('fs');
const path = require('path');
const { Vector3, Scene, PerspectiveCamera, WebGLRenderer, Points, PointsMaterial, Geometry, Face3, MeshBasicMaterial, Mesh } = require('three');

// Lire les points à partir du fichier
function readPointsFromFile(filename) {
    const points = [];
    const data = fs.readFileSync(path.resolve(__dirname, filename), 'utf-8');
    data.split('\n').forEach(line => {
        const [x, y, z] = line.trim().split(' ').map(Number);
        if (!isNaN(x) && !isNaN(y) && !isNaN(z)) {
            points.push(new Vector3(x, y, z));
        }
    });
    return points;
}

// Trouver un parallélépipède dans les points
function findParallelepiped(points) {
    const pointsSet = new Set(points.map(p => p.toArray().toString()));
    const n = points.length;

    for (let i = 0; i < n; i++) {
        const [x1, y1, z1] = points[i];
        for (let j = i + 1; j < n; j++) {
            const [x2, y2, z2] = points[j];
            if (x1 !== x2 && y1 !== y2 && z1 !== z2) {
                if (pointsSet.has([x1, y1, z2].toString()) &&
                    pointsSet.has([x1, y2, z1].toString()) &&
                    pointsSet.has([x2, y1, z1].toString()) &&
                    pointsSet.has([x2, y2, z2].toString()) &&
                    pointsSet.has([x1, y2, z2].toString()) &&
                    pointsSet.has([x2, y1, z2].toString()) &&
                    pointsSet.has([x2, y2, z1].toString())) {
                    return [
                        new Vector3(x1, y1, z1), new Vector3(x1, y1, z2),
                        new Vector3(x1, y2, z1), new Vector3(x1, y2, z2),
                        new Vector3(x2, y1, z1), new Vector3(x2, y1, z2),
                        new Vector3(x2, y2, z1), new Vector3(x2, y2, z2)
                    ];
                }
            }
        }
    }
    return null;
}

// Initialiser la scène 3D
function initScene(points, parallelepiped) {
    const scene = new Scene();
    const camera = new PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Ajouter les points à la scène
    const geometry = new Geometry();
    geometry.vertices.push(...points);
    const material = new PointsMaterial({ color: 0x00ff00, size: 5 });
    const pointCloud = new Points(geometry, material);
    scene.add(pointCloud);

    if (parallelepiped) {
        // Ajouter le parallélépipède à la scène
        const edges = [
            [0, 1, 3, 2], [4, 5, 7, 6],
            [0, 1, 5, 4], [2, 3, 7, 6],
            [0, 2, 6, 4], [1, 3, 7, 5]
        ];
        const materials = new MeshBasicMaterial({ color: 0x00ffff, wireframe: true });
        edges.forEach(edge => {
            const faceGeometry = new Geometry();
            faceGeometry.vertices.push(...edge.map(i => parallelepiped[i]));
            faceGeometry.faces.push(new Face3(0, 1, 2), new Face3(2, 3, 0));
            const mesh = new Mesh(faceGeometry, materials);
            scene.add(mesh);
        });
    }

    camera.position.z = 50;

    const animate = function () {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    };

    animate();
}

// Lire les points et trouver le parallélépipède
const filename = '1-6.txt';
const points = readPointsFromFile(filename);
const parallelepiped = findParallelepiped(points);

if (parallelepiped) {
    parallelepiped.forEach(p => console.log(`${p.x} ${p.y} ${p.z}`));
} else {
    console.log("Aucun parallélépipède trouvé");
}

initScene(points, parallelepiped);
