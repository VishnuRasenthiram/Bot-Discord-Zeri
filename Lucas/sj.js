const fs = require('fs');
const Plotly = require('plotly.js-dist');

function readPointsFromFile(filename) {
    const data = fs.readFileSync(filename, 'utf8');
    const points = data.trim().split('\n').map(line => {
        const [x, y] = line.split(' ').map(Number);
        return { x, y };
    });
    return points;
}

function findRectangle(points) {
    const pointsByX = new Map();
    const pointsByY = new Map();
    const pointsSet = new Set();

    points.forEach(point => {
        if (!pointsByX.has(point.x)) pointsByX.set(point.x, []);
        if (!pointsByY.has(point.y)) pointsByY.set(point.y, []);
        pointsByX.get(point.x).push(point.y);
        pointsByY.get(point.y).push(point.x);
        pointsSet.add(`${point.x},${point.y}`);
    });

    for (const [x1, yList] of pointsByX.entries()) {
        for (let i = 0; i < yList.length; i++) {
            for (let j = i + 1; j < yList.length; j++) {
                const y1 = yList[i];
                const y2 = yList[j];
                for (const x2 of pointsByY.get(y1)) {
                    if (x2 !== x1 && pointsSet.has(`${x2},${y2}`)) {
                        return [{ x: x1, y: y1 }, { x: x1, y: y2 }, { x: x2, y: y1 }, { x: x2, y: y2 }];
                    }
                }
            }
        }
    }
    return null;
}

function plotPoints(points, rectangle) {
    const xPoints = points.map(p => p.x);
    const yPoints = points.map(p => p.y);

    const tracePoints = {
        x: xPoints,
        y: yPoints,
        mode: 'markers',
        type: 'scatter',
        name: 'Points'
    };

    const traces = [tracePoints];

    if (rectangle) {
        const rectX = [rectangle[0].x, rectangle[1].x, rectangle[3].x, rectangle[2].x, rectangle[0].x];
        const rectY = [rectangle[0].y, rectangle[1].y, rectangle[3].y, rectangle[2].y, rectangle[0].y];

        const traceRect = {
            x: rectX,
            y: rectY,
            mode: 'lines',
            type: 'scatter',
            name: 'Rectangle',
            line: { color: 'red' }
        };
        traces.push(traceRect);
    }

    const layout = {
        title: 'Points and Rectangle',
        xaxis: { title: 'X' },
        yaxis: { title: 'Y' }
    };

    Plotly.newPlot('plot', traces, layout);
}

// Lecture des points à partir du fichier 'points.txt'
const filename = 'points.txt';
const points = readPointsFromFile(filename);
console.log('Lecture des points terminée.');

const startTime = Date.now();
const rectangle = findRectangle(points);
console.log(`Recherche du rectangle terminée en ${(Date.now() - startTime) / 1000} secondes.`);

if (rectangle) {
    rectangle.forEach(point => console.log(`${point.x} ${point.y}`));
} else {
    console.log("Aucun rectangle trouvé");
}

// Créez un fichier HTML pour afficher le graphique
const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Points and Rectangle</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div id="plot" style="width:100%;height:100vh;"></div>
    <script>
        ${fs.readFileSync(__filename)}
        const points = ${JSON.stringify(points)};
        const rectangle = ${JSON.stringify(rectangle)};
        plotPoints(points, rectangle);
    </script>
</body>
</html>
`;

// Écrire le fichier HTML et l'ouvrir dans le navigateur
fs.writeFileSync('index.html', htmlContent);
console.log('Graphique généré dans index.html');
