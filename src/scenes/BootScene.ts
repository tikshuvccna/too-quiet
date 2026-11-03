import Phaser from 'phaser';

export const CHARS = ['apprentice_girl', 'apprentice_boy', 'dvora'] as const;
export type CharKey = (typeof CHARS)[number];

interface AnimDef { frames: string[]; frameRate: number; repeat: number }

type Draw = (c: CanvasRenderingContext2D, w: number, h: number) => void;

function makeTexture(scene: Phaser.Scene, key: string, w: number, h: number, draw: Draw): void {
  if (scene.textures.exists(key)) return;
  const t = scene.textures.createCanvas(key, w, h);
  if (!t) return;
  draw(t.getContext(), w, h);
  t.refresh();
}

const drawGrass: Draw = (c, w, h) => {
  c.fillStyle = '#3d6b4a';
  c.fillRect(0, 0, w, h);
  let s = 7;
  const r = (): number => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 260; i++) {
    c.fillStyle = r() < 0.5 ? 'rgba(80,140,90,.35)' : 'rgba(30,70,50,.3)';
    c.fillRect(r() * w, r() * h, 2 + r() * 3, 2 + r() * 5);
  }
};

const drawDot = (col: string): Draw => (c, w, h) => {
  c.shadowColor = col;
  c.shadowBlur = 12;
  c.fillStyle = col;
  c.beginPath();
  c.arc(w / 2, h / 2, Math.min(w, h) / 4, 0, 7);
  c.fill();
};

const drawShadow: Draw = (c, w, h) => {
  const g = c.createRadialGradient(w / 2, h / 2, 2, w / 2, h / 2, w / 2);
  g.addColorStop(0, 'rgba(0,0,0,.45)');
  g.addColorStop(1, 'rgba(0,0,0,0)');
  c.fillStyle = g;
  c.fillRect(0, 0, w, h);
};

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload(): void {
    const base = import.meta.env.BASE_URL;
    for (const k of CHARS) {
      this.load.atlas(k, `${base}assets/characters/${k}.png`, `${base}assets/characters/${k}.json`);
      this.load.json(`${k}:anims`, `${base}assets/characters/${k}.json`);
    }
    this.load.atlas('props', `${base}assets/props/props.png`, `${base}assets/props/props.json`);
    this.load.atlas('buildings', `${base}assets/buildings/buildings.png`, `${base}assets/buildings/buildings.json`);
    this.load.json('buildings:meta', `${base}assets/buildings/buildings.json`);
    this.load.atlas('buildings_truth', `${base}assets/buildings/buildings_truth.png`, `${base}assets/buildings/buildings_truth.json`);
    this.load.atlas('fx', `${base}assets/fx/fx.png`, `${base}assets/fx/fx.json`);
  }

  create(): void {
    makeTexture(this, 'grass', 128, 128, drawGrass);
    makeTexture(this, 'dot_gold', 24, 24, drawDot('#ffcf6b'));
    makeTexture(this, 'dot_teal', 24, 24, drawDot('#5cf0d0'));
    makeTexture(this, 'dot_pink', 24, 24, drawDot('#ff9ad0'));
    makeTexture(this, 'blob', 64, 32, drawShadow);
    for (const k of CHARS) {
      const data = this.cache.json.get(`${k}:anims`) as { anims?: Record<string, AnimDef> } | undefined;
      for (const [name, a] of Object.entries(data?.anims ?? {})) {
        const key = `${k}:${name}`;
        if (this.anims.exists(key)) continue;
        this.anims.create({ key, frames: a.frames.map((f) => ({ key: k, frame: f })), frameRate: a.frameRate, repeat: a.repeat });
      }
    }
    this.scene.start('World');
  }
}
