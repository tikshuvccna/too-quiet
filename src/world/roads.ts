import Phaser from 'phaser';

export interface RoadDef {
  /** Control points; the curve passes through all of them. First and last sit on door fronts. */
  pts: Array<[number, number]>;
  width: number;
}

/** The village plaza: cobbled ellipse in the middle (oblique view makes circles look like ellipses). */
export const PLAZA = { x: 1280, y: 1010, rx: 175, ry: 112 };

export const ROADS: RoadDef[] = [
  // west: grandma's door to the plaza
  { pts: [[742, 940], [750, 985], [830, 1008], [1000, 1012], [1130, 1010]], width: 62 },
  // north: plaza to the clinic door
  { pts: [[1280, 900], [1276, 860], [1270, 830], [1268, 822]], width: 58 },
  // east: plaza to the bakery and the tower road
  { pts: [[1430, 1010], [1560, 1018], [1700, 1018], [1770, 996], [1756, 960]], width: 62 },
  { pts: [[1780, 1010], [1900, 982], [2030, 930], [2110, 820], [2160, 700], [2180, 630]], width: 54 },
  // south: plaza to Grandpa Hed's bench and beyond
  { pts: [[1280, 1120], [1268, 1220], [1252, 1330], [1262, 1480]], width: 56 },
  // west branch to the print house
  { pts: [[900, 1010], [740, 1030], [600, 1080], [566, 1200], [558, 1340], [556, 1504]], width: 54 },
  // south-east to the bridge and the mill
  { pts: [[1782, 1018], [1850, 1130], [1930, 1240], [1968, 1292], [2060, 1382], [2150, 1448], [2172, 1500]], width: 54 },
  // highways of the big valley
  // east: bakery road to the market row, bell hill and the stone moor
  { pts: [[1900, 982], [2250, 1010], [2600, 930], [2950, 800], [3300, 700], [3700, 640], [4100, 560], [4500, 520], [5000, 640], [5500, 800]], width: 56 },
  // market square down the valley to the mill road and on to the great tower gate
  { pts: [[3300, 700], [3240, 1050], [3290, 1400], [3380, 1800], [3600, 2100], [3950, 2260], [4300, 2250]], width: 54 },
  // mill to the valley road
  { pts: [[2172, 1500], [2500, 1650], [2900, 1780], [3380, 1800]], width: 54 },
  // print house south to the orchard and the whisper woods
  { pts: [[556, 1504], [620, 1900], [760, 2350], [880, 2800], [820, 3300], [760, 3700]], width: 54 },
  // Hed's bench south: orchard, then the coast road to the lighthouse and harbour
  { pts: [[1262, 1480], [1290, 1900], [1380, 2350], [1700, 2800], [2300, 3150], [3000, 3330], [3600, 3380], [4300, 3340], [5000, 3300]], width: 56 },
  // orchard crossroads to the woods
  { pts: [[880, 2800], [1250, 3200], [1500, 3500]], width: 46 },
];

function stamp(g: Phaser.GameObjects.Graphics, pts: Phaser.Math.Vector2[], radius: number): void {
  for (const p of pts) g.fillCircle(p.x, p.y, radius);
}

/** Smooth, round-capped paths with a worn centre and a few pebbles. Drawn once into a static Graphics. */
export function drawRoads(g: Phaser.GameObjects.Graphics): void {
  const curves = ROADS.map((r) => {
    const spline = new Phaser.Curves.Spline(r.pts.map(([x, y]) => new Phaser.Math.Vector2(x, y)));
    return { r, pts: spline.getSpacedPoints(Math.max(8, Math.ceil(spline.getLength() / 5))) };
  });
  // plaza ground first, so paths blend into it
  g.fillStyle(0x5e4d3a, 1);
  g.fillEllipse(PLAZA.x, PLAZA.y, PLAZA.rx * 2 + 14, PLAZA.ry * 2 + 12);
  for (const { r, pts } of curves) {
    g.fillStyle(0x5e4d3a, 1);
    stamp(g, pts, r.width / 2 + 6);
  }
  g.fillStyle(0xc9ad7f, 1);
  g.fillEllipse(PLAZA.x, PLAZA.y, PLAZA.rx * 2, PLAZA.ry * 2);
  for (const { r, pts } of curves) {
    g.fillStyle(0xc9ad7f, 1);
    stamp(g, pts, r.width / 2);
    g.fillStyle(0xd8be92, 0.7);
    stamp(g, pts, r.width / 2 - 14);
  }
  // cobbles on the plaza: concentric rings of small stones
  let seed = 5;
  const rnd = (): number => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let ring = 1; ring <= 4; ring++) {
    const k = ring / 4.2;
    const n = 10 + ring * 9;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + ring;
      const x = PLAZA.x + Math.cos(a) * PLAZA.rx * k;
      const y = PLAZA.y + Math.sin(a) * PLAZA.ry * k;
      g.fillStyle(rnd() < 0.5 ? 0xb89b6e : 0xdcc49a, 0.9);
      g.fillEllipse(x, y, 20 + rnd() * 8, 11 + rnd() * 4);
    }
  }
  // pebbles and wheel-worn patches along the paths
  for (const { r, pts } of curves) {
    for (let i = 0; i < pts.length; i += 3) {
      const p = pts[i] as Phaser.Math.Vector2;
      const off = (rnd() - 0.5) * (r.width - 14);
      g.fillStyle(rnd() < 0.5 ? 0xa98c60 : 0xe2cba0, 0.75);
      g.fillCircle(p.x + off, p.y + (rnd() - 0.5) * 10, 1.5 + rnd() * 2.4);
    }
  }
}
