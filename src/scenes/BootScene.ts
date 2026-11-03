import Phaser from 'phaser';

type Draw = (c: CanvasRenderingContext2D, w: number, h: number) => void;

function makeTexture(scene: Phaser.Scene, key: string, w: number, h: number, draw: Draw): void {
  if (scene.textures.exists(key)) return;
  const t = scene.textures.createCanvas(key, w, h);
  if (!t) return;
  draw(t.getContext(), w, h);
  t.refresh();
}

function rr(c: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number): void {
  c.beginPath();
  c.roundRect(x, y, w, h, r);
}

function cottage(wall: string, roof: string, roofHi: string): Draw {
  return (c, w, h) => {
    // soft ground shadow
    c.fillStyle = 'rgba(0,0,0,.28)';
    c.beginPath(); c.ellipse(w / 2, h - 16, w * 0.46, 22, 0, 0, 7); c.fill();
    // walls
    const g = c.createLinearGradient(0, h * 0.4, 0, h - 20);
    g.addColorStop(0, wall); g.addColorStop(1, '#3a2a35');
    c.fillStyle = g; rr(c, 22, h * 0.44, w - 44, h * 0.5 - 14, 6); c.fill();
    c.strokeStyle = 'rgba(0,0,0,.35)'; c.lineWidth = 3; c.stroke();
    // roof
    c.fillStyle = roof;
    c.beginPath(); c.moveTo(6, h * 0.5); c.lineTo(w / 2, h * 0.06); c.lineTo(w - 6, h * 0.5); c.closePath(); c.fill();
    c.strokeStyle = roofHi; c.lineWidth = 3;
    for (let i = 1; i < 5; i++) {
      const y = h * 0.5 - i * (h * 0.09);
      c.beginPath(); c.moveTo(6 + i * 16, y); c.lineTo(w - 6 - i * 16, y); c.stroke();
    }
    c.fillStyle = 'rgba(255,255,255,.1)';
    c.beginPath(); c.moveTo(w / 2, h * 0.06); c.lineTo(w - 6, h * 0.5); c.lineTo(w / 2, h * 0.5); c.closePath(); c.fill();
    // chimney
    c.fillStyle = '#4b3b4d'; rr(c, w * 0.7, h * 0.08, 22, 44, 3); c.fill();
    // windows (warm glow)
    for (const x of [w * 0.28, w * 0.64]) {
      const gl = c.createRadialGradient(x + 14, h * 0.66, 2, x + 14, h * 0.66, 30);
      gl.addColorStop(0, '#ffe3a0'); gl.addColorStop(1, '#d98a3a');
      c.fillStyle = gl; rr(c, x, h * 0.58, 30, 34, 5); c.fill();
      c.strokeStyle = '#3a2a35'; c.lineWidth = 3; c.stroke();
      c.beginPath(); c.moveTo(x + 15, h * 0.58); c.lineTo(x + 15, h * 0.58 + 34); c.moveTo(x, h * 0.58 + 17); c.lineTo(x + 30, h * 0.58 + 17); c.stroke();
    }
    // door
    c.fillStyle = '#5b3a2a';
    c.beginPath(); c.moveTo(w / 2 - 20, h - 22); c.lineTo(w / 2 - 20, h * 0.74); c.arc(w / 2, h * 0.74, 20, Math.PI, 0); c.lineTo(w / 2 + 20, h - 22); c.closePath(); c.fill();
    c.strokeStyle = '#2a1a14'; c.lineWidth = 3; c.stroke();
    c.fillStyle = '#ffcf6b'; c.beginPath(); c.arc(w / 2 + 10, h * 0.86, 3, 0, 7); c.fill();
  };
}

const drawTower: Draw = (c, w, h) => {
  c.fillStyle = 'rgba(0,0,0,.3)';
  c.beginPath(); c.ellipse(w / 2, h - 16, w * 0.4, 22, 0, 0, 7); c.fill();
  const g = c.createLinearGradient(0, 0, w, 0);
  g.addColorStop(0, '#5d5a86'); g.addColorStop(0.5, '#7a76a8'); g.addColorStop(1, '#4a4770');
  c.fillStyle = g; rr(c, w * 0.22, h * 0.22, w * 0.56, h * 0.72, 8); c.fill();
  c.strokeStyle = 'rgba(0,0,0,.4)'; c.lineWidth = 3; c.stroke();
  c.fillStyle = '#3c3a64';
  c.beginPath(); c.moveTo(w * 0.14, h * 0.26); c.lineTo(w / 2, h * 0.0); c.lineTo(w * 0.86, h * 0.26); c.closePath(); c.fill();
  for (const y of [0.34, 0.5, 0.66]) {
    c.fillStyle = '#5cf0d0'; c.shadowColor = '#5cf0d0'; c.shadowBlur = 14;
    c.beginPath(); c.arc(w / 2, h * y, 9, 0, 7); c.fill(); c.shadowBlur = 0;
  }
  c.fillStyle = '#4a2a20';
  c.beginPath(); c.moveTo(w / 2 - 20, h - 22); c.lineTo(w / 2 - 20, h * 0.82); c.arc(w / 2, h * 0.82, 20, Math.PI, 0); c.lineTo(w / 2 + 20, h - 22); c.closePath(); c.fill();
};

const drawTree: Draw = (c, w, h) => {
  c.fillStyle = 'rgba(0,0,0,.28)';
  c.beginPath(); c.ellipse(w / 2, h - 12, w * 0.32, 14, 0, 0, 7); c.fill();
  c.fillStyle = '#4b3224'; rr(c, w / 2 - 9, h * 0.55, 18, h * 0.4, 4); c.fill();
  const blobs: Array<[number, number, number, string]> = [
    [0.5, 0.34, 0.34, '#2f6b4a'], [0.34, 0.46, 0.26, '#3a7d55'], [0.66, 0.46, 0.26, '#3a7d55'], [0.5, 0.24, 0.24, '#4a9266'],
  ];
  for (const [x, y, r, col] of blobs) {
    c.fillStyle = col; c.beginPath(); c.arc(w * x, h * y, w * r, 0, 7); c.fill();
  }
  c.fillStyle = 'rgba(255,255,255,.1)'; c.beginPath(); c.arc(w * 0.42, h * 0.2, w * 0.12, 0, 7); c.fill();
};

const drawGrass: Draw = (c, w, h) => {
  c.fillStyle = '#3d6b4a'; c.fillRect(0, 0, w, h);
  let s = 7;
  const r = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 260; i++) {
    c.fillStyle = r() < 0.5 ? 'rgba(80,140,90,.35)' : 'rgba(30,70,50,.3)';
    c.fillRect(r() * w, r() * h, 2 + r() * 3, 2 + r() * 5);
  }
};

function person(body: string, hat: string): Draw {
  return (c, w, h) => {
    c.fillStyle = 'rgba(0,0,0,.3)';
    c.beginPath(); c.ellipse(w / 2, h - 8, 20, 8, 0, 0, 7); c.fill();
    // long dress / robe down to the ground
    const g = c.createLinearGradient(0, h * 0.4, 0, h - 8);
    g.addColorStop(0, body); g.addColorStop(1, 'rgba(30,24,48,1)');
    c.fillStyle = g;
    c.beginPath(); c.moveTo(w / 2 - 12, h * 0.42); c.lineTo(w / 2 + 12, h * 0.42); c.lineTo(w / 2 + 22, h - 10); c.lineTo(w / 2 - 22, h - 10); c.closePath(); c.fill();
    // long sleeves
    c.fillStyle = body;
    rr(c, w / 2 - 22, h * 0.44, 10, 30, 5); c.fill(); rr(c, w / 2 + 12, h * 0.44, 10, 30, 5); c.fill();
    // head and hat
    c.fillStyle = '#f0c9a0'; c.beginPath(); c.arc(w / 2, h * 0.32, 11, 0, 7); c.fill();
    c.fillStyle = hat; c.beginPath(); c.ellipse(w / 2, h * 0.27, 20, 6, 0, 0, 7); c.fill();
    rr(c, w / 2 - 10, h * 0.14, 20, 14, 6); c.fill();
  };
}

const drawDot = (col: string): Draw => (c, w, h) => {
  c.shadowColor = col; c.shadowBlur = 12; c.fillStyle = col;
  c.beginPath(); c.arc(w / 2, h / 2, Math.min(w, h) / 4, 0, 7); c.fill();
};

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  create(): void {
    makeTexture(this, 'grass', 128, 128, drawGrass);
    makeTexture(this, 'cottage_a', 300, 260, cottage('#d8b48a', '#a2473c', '#c56a58'));
    makeTexture(this, 'cottage_b', 320, 260, cottage('#cfd1c0', '#4f6c9b', '#7a97c4'));
    makeTexture(this, 'cottage_c', 300, 260, cottage('#e0c08a', '#7d5a3c', '#a67b55'));
    makeTexture(this, 'tower', 220, 340, drawTower);
    makeTexture(this, 'tree', 150, 190, drawTree);
    makeTexture(this, 'player_ph', 64, 96, person('#6d5aa8', '#8a3d52'));
    makeTexture(this, 'player_boy_ph', 64, 96, person('#3f6fa0', '#3a3a3a'));
    makeTexture(this, 'npc_ph', 64, 96, person('#a85d4a', '#4a3a2a'));
    makeTexture(this, 'npc_dvora', 64, 96, person('#5a4a7a', '#7a5a8a'));
    makeTexture(this, 'npc_hub', 64, 96, person('#7a7a50', '#8a8a5a'));
    makeTexture(this, 'dot_gold', 24, 24, drawDot('#ffcf6b'));
    makeTexture(this, 'dot_teal', 24, 24, drawDot('#5cf0d0'));
    makeTexture(this, 'dot_pink', 24, 24, drawDot('#ff9ad0'));
    this.scene.start('World');
  }
}
