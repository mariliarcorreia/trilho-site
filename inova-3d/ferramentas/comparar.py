"""Comparacao entre os renders de validacao e as fotos reais do drone.

Para cada camera (A, B, C) gera em saida/comparacao/:
  * lado_a_lado_<K>.png  foto real | render
  * cortina_<K>.png      metade esquerda real, metade direita render (alinhamento de linhas)
  * mescla_<K>.png       sobreposicao 50%
  * bordas_<K>.png       contornos da foto (vermelho) sobre os do render (ciano); branco = coincidem
e um metricas.json com a distancia entre contornos (chamfer):
  * mediana_px: distancia tipica entre uma borda da foto e a borda mais proxima do render
  * dentro_5px / dentro_10px: fracao das bordas da foto explicadas pelo render

Uso: python ferramentas/comparar.py [A B C]
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = {
    "A": "referencias/fotos_drone/ref_A_aerea_obliqua.png",
    "B": "referencias/fotos_drone/ref_B_frontal_baixa.png",
    "C": "referencias/fotos_drone/ref_C_frontal_ampla.png",
}


def _bordas(img, frac=0.10):
    g = np.asarray(img.convert("L"), float)
    g = ndimage.gaussian_filter(g, 1.2)
    mag = np.hypot(ndimage.sobel(g, 0), ndimage.sobel(g, 1))
    lim = np.quantile(mag, 1 - frac)
    return mag > lim


def _rotulo(img, texto):
    d = ImageDraw.Draw(img)
    try:
        fonte = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        fonte = ImageFont.load_default()
    d.rectangle([0, 0, 12 + 13 * len(texto), 34], fill=(0, 0, 0))
    d.text((8, 5), texto, fill=(255, 255, 255), font=fonte)
    return img


def comparar(chave, saida):
    ref = Image.open(os.path.join(RAIZ, REFS[chave])).convert("RGB")
    ren = Image.open(os.path.join(RAIZ, "saida", "validacao", f"render_{chave}.png")).convert("RGB").resize(ref.size)
    W, H = ref.size

    lado = Image.new("RGB", (W * 2 + 10, H), (20, 20, 20))
    lado.paste(_rotulo(ref.copy(), f"FOTO REAL {chave}"), (0, 0))
    lado.paste(_rotulo(ren.copy(), f"RENDER 3D {chave}"), (W + 10, 0))
    lado.save(os.path.join(saida, f"lado_a_lado_{chave}.png"))

    cort = ref.copy()
    cort.paste(ren.crop((W // 2, 0, W, H)), (W // 2, 0))
    ImageDraw.Draw(cort).line([(W // 2, 0), (W // 2, H)], fill=(255, 200, 0), width=3)
    cort.save(os.path.join(saida, f"cortina_{chave}.png"))

    Image.blend(ref, ren, 0.5).save(os.path.join(saida, f"mescla_{chave}.png"))

    br, bm = _bordas(ref), _bordas(ren)
    vis = np.full((H, W, 3), 25, np.uint8)
    vis[bm] = (0, 200, 255)
    vis[br] = (255, 40, 40)
    vis[br & ndimage.binary_dilation(bm, iterations=2)] = (255, 255, 255)
    Image.fromarray(vis).save(os.path.join(saida, f"bordas_{chave}.png"))

    dist_ate_render = ndimage.distance_transform_edt(~bm)[br]
    dist_ate_foto = ndimage.distance_transform_edt(~br)[bm]
    return {
        "foto_para_render": {
            "mediana_px": round(float(np.median(dist_ate_render)), 2),
            "dentro_5px": round(float(np.mean(dist_ate_render <= 5)), 3),
            "dentro_10px": round(float(np.mean(dist_ate_render <= 10)), 3),
        },
        "render_para_foto": {
            "mediana_px": round(float(np.median(dist_ate_foto)), 2),
            "dentro_5px": round(float(np.mean(dist_ate_foto <= 5)), 3),
            "dentro_10px": round(float(np.mean(dist_ate_foto <= 10)), 3),
        },
    }


def main():
    chaves = sys.argv[1:] or ["A", "B", "C"]
    saida = os.path.join(RAIZ, "saida", "comparacao")
    os.makedirs(saida, exist_ok=True)
    metr = {}
    caminho = os.path.join(saida, "metricas.json")
    if os.path.exists(caminho):
        with open(caminho) as fh:
            metr = json.load(fh)
    for k in chaves:
        metr[k] = comparar(k, saida)
        print(k, json.dumps(metr[k], ensure_ascii=False))
    with open(caminho, "w") as fh:
        json.dump(metr, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
