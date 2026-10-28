"""Retroprojecao de pixels das fotos reais sobre planos conhecidos do modelo.

Com as cameras calibradas (config/calibracao.json), um pixel marcado na foto
vira um raio no espaco. A intersecao desse raio com um plano conhecido
(fachada do galpao em Y=0, frente do predio administrativo, piso Z=0) da a
posicao metrica do detalhe: janelas, colunas, letreiro, veiculos etc.

Uso:
    python ferramentas/retroprojetar.py B plano_y=-12.49 712,240 803,385
    python ferramentas/retroprojetar.py B plano_z=0 590,405
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calibrar_cameras import H, RAIZ, W, rot_camera  # noqa: E402


def carregar_camera(chave):
    with open(os.path.join(RAIZ, "config", "calibracao.json")) as fh:
        c = json.load(fh)["cameras"][chave]
    rx, ry, rz = c["rotacao_euler_graus"]
    return np.array(c["posicao"]), rot_camera(rz, rx - 90, ry), c["focal_px"]


def raio(cam, u, v):
    pos, R, f = cam
    d_cam = np.array([(u - W / 2) / f, -(v - H / 2) / f, -1.0])
    d = R @ d_cam
    return pos, d / np.linalg.norm(d)


def intersectar(cam, u, v, eixo, valor):
    o, d = raio(cam, u, v)
    i = "xyz".index(eixo)
    t = (valor - o[i]) / d[i]
    return o + t * d


def main():
    chave, plano, *pixels = sys.argv[1:]
    eixo, valor = plano.replace("plano_", "").split("=")
    cam = carregar_camera(chave)
    for px in pixels:
        u, v = (float(t) for t in px.split(","))
        p = intersectar(cam, u, v, eixo, float(valor))
        print(f"{px:>12} -> X={p[0]:7.2f}  Y={p[1]:7.2f}  Z={p[2]:6.2f}")


if __name__ == "__main__":
    main()
