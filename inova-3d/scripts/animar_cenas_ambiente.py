"""Anima cenas sem fala (2.5D): personagens recortados sobre o fundo, camera com
paralaxe, leve respiracao dos personagens, poeira na luz e brilho correndo no inox.

Uso: python scripts/animar_cenas_ambiente.py c05_frigorifico [c08_projeto ...]
Saida: saida/animacao/<cena>.mp4 (1920x1080, 24 fps, 5 s)
"""
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animacao_2d as a  # noqa: E402

RAIZ = a.RAIZ
DUR = 5.0

# camera por cena: centro inicial/final (fracao da imagem), zoom inicial/final
CAMERAS = {
    "c05_frigorifico": ((0.47, 0.50), (0.55, 0.48), 1.00, 1.10),
    "c08_projeto": ((0.50, 0.50), (0.45, 0.46), 1.00, 1.09),
    "c09_qualidade": ((0.48, 0.48), (0.42, 0.40), 1.00, 1.12),
    "c12_harmonia": ((0.52, 0.50), (0.50, 0.44), 1.00, 1.09),
    "c20_caminhada": ((0.40, 0.52), (0.55, 0.50), 1.06, 1.06),
}


def brilho_inox(img, t):
    """Faixa de reflexo diagonal que atravessa as superficies claras e metalicas."""
    H, W = img.shape[:2]
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    pos = (t / DUR) * 1.6 - 0.3
    faixa = np.exp(-(((X / W + Y / H * 0.6) - pos * 1.6) / 0.06) ** 2)
    cinza = img.mean(-1)
    sat = img.max(-1) - img.min(-1)
    metal = np.clip((cinza - 0.35) * 3, 0, 1) * np.clip((0.18 - sat) * 8, 0, 1)
    return np.clip(img + (faixa * metal * 0.35)[..., None], 0, 1)


def animar(nome):
    img_path = os.path.join(RAIZ, "pacote_kling", f"{nome}.png")
    img = np.asarray(Image.open(img_path).convert("RGB")).astype(np.float32) / 255
    H, W = img.shape[:2]
    pasta = os.path.join(RAIZ, "saida", "animacao", nome)
    os.makedirs(os.path.join(pasta, "quadros"), exist_ok=True)
    alfa = a.recortar(img_path, os.path.join(pasta, "recorte.png"))
    fundo = a.fundo_sem_personagem(img, alfa)
    rgba = np.dstack([img, alfa])
    (c0, c1, z0, z1) = CAMERAS[nome]
    part = a.Particulas(60, W, H, semente=len(nome))
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    base_y = H * 0.95
    n = int(DUR * a.FPS)
    for i in range(n):
        t = i / a.FPS
        u = a.suave(t / DUR)
        # respiracao leve dos personagens (estica a partir da base)
        s = 0.004 * math.sin(2 * math.pi * t / 3.4)
        dy = -(base_y - Y) * s * np.clip((base_y - Y) / base_y, 0, 1)
        dx = 1.5 * math.sin(2 * math.pi * t / 4.1) * np.clip((base_y - Y) / base_y, 0, 1)
        pers = cv2.remap(rgba, X - dx, Y - dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        centro = (np.array(c0) + (np.array(c1) - np.array(c0)) * u) * np.array([W, H])
        z = z0 + (z1 - z0) * u
        zf = 1 + (z - 1) * 0.5
        bg = a.transformar(brilho_inox(fundo, t), zf * 1.03, centro, (H, W))
        bg = part.desenhar(bg, t)
        ps = a.transformar(pers, z * 1.03, centro, (H, W))
        q = bg * (1 - ps[..., 3:4]) + ps[..., :3] * ps[..., 3:4]
        q = cv2.resize(np.clip(q, 0, 1), (a.W_SAIDA, a.H_SAIDA), interpolation=cv2.INTER_CUBIC)
        Image.fromarray((q * 255).astype(np.uint8)).save(os.path.join(pasta, "quadros", f"q_{i:04d}.png"))
    saida = os.path.join(RAIZ, "saida", "animacao", f"{nome}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(a.FPS), "-i",
                    os.path.join(pasta, "quadros", "q_%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "17", saida], check=True)
    print("ok", saida, flush=True)


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        animar(nome)
