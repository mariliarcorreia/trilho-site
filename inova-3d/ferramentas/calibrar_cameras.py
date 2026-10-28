"""Calibracao conjunta: tres cameras de drone + dimensoes principais da fachada.

Roda fora do Blender (numpy + scipy). Le os pontos marcados nas fotos reais
(referencias/pontos_correspondencia.json), monta um modelo parametrico simples
da fachada e resolve, por minimos quadrados, a pose e a distancia focal de cada
camera junto com as dimensoes estimadas.

A escala absoluta vem de ancoras com medida conhecida ou tipica:
  * a pessoa caminhando na calcada (foto B), altura assumida de 1,72 m;
  * a altura tipica do gradil frontal (2,4 m, com incerteza);
  * a lente equivalente a 24 mm dos quadros B e C (sem zoom), que evita a
    ambiguidade entre distancia da camera e distancia focal.
Todas as outras medidas saem do ajuste e ficam registradas com o erro de
reprojecao, para que possam ser revisadas e corrigidas em config/fachada.json.

Uso:
    python ferramentas/calibrar_cameras.py            # resolve e grava config/calibracao.json
    python ferramentas/calibrar_cameras.py --overlay  # tambem desenha os pontos reprojetados
"""
import argparse
import json
import math
import os

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1290, 726
SIGMA_PX = 5.0
ALTURA_PESSOA = 1.72

# nome: (valor inicial, desvio do prior). Prior largo = medida livre.
PARAMS = {
    "g1_largura":        (38.0, 15.0),
    "g1_altura":         (11.5, 4.0),
    "faixa_branca_alt":  (3.6, 1.5),
    "anexo_largura":     (6.0, 4.0),
    "anexo_altura":      (4.2, 2.0),
    "adm_x0":            (18.0, 10.0),
    "adm_largura":       (22.0, 8.0),
    "adm_profundidade":  (10.0, 5.0),
    "adm_altura":        (7.6, 2.0),
    "adm_y_fundo":       (0.0, 3.0),
    "torre_x_rel":       (14.0, 6.0),
    "torre_largura":     (5.0, 3.0),
    "torre_altura":      (9.0, 2.0),
    "torre_avanco":      (0.5, 0.3),
    "cerca_y":           (-24.0, 10.0),
    "cerca_altura":      (2.4, 0.3),
    "cerca_px1":         (10.0, 40.0),
    "cerca_px2":         (50.0, 40.0),
    "pessoa_x":          (40.0, 40.0),
    "pessoa_y":          (-27.0, 10.0),
    "meiofio_y":         (-28.0, 10.0),
    "meiofio_x1":        (-20.0, 60.0),
    "meiofio_x2":        (60.0, 60.0),
    "g2_x_dir":          (72.0, 20.0),
    "g2_y_frente":       (8.0, 10.0),
    "g2_altura":         (12.0, 4.0),
}
NOMES = list(PARAMS)

# camera: x, y, z, guinada (graus, + gira para a esquerda), inclinacao (graus, - olha para baixo), rolagem, focal_px
CAMS_INI = {
    "B": [18.0, -60.0, 13.0, 0.0, -8.0, 0.0, 1000.0],
    "A": [-15.0, -55.0, 45.0, -25.0, -35.0, 0.0, 2000.0],
    "C": [25.0, -110.0, 25.0, 0.0, -10.0, 0.0, 950.0],
}
ORDEM_CAMS = ["B", "A", "C"]
# Prior de lente: B e C sao quadros de video DJI sem zoom (equivalente 24 mm em sensor 36 mm,
# ou seja ~860 px na largura de 1290). A foto A tem zoom evidente, por isso fica livre.
PRIOR_FOCAL = {"B": (860.0, 200.0), "C": (860.0, 200.0)}


def pontos_modelo(p):
    """Pontos 3D do modelo em funcao dos parametros (dicionario)."""
    ax0 = p["adm_x0"]
    ay = -p["adm_profundidade"]
    tx = ax0 + p["torre_x_rel"]
    ty = ay - p["torre_avanco"]
    return {
        "g1_topo_esq": (0, 0, p["g1_altura"]),
        "g1_topo_dir": (p["g1_largura"], 0, p["g1_altura"]),
        "g1_faixa_branca_esq": (0, 0, p["faixa_branca_alt"]),
        "g1_base_esq": (0, 0, 0),
        "anexo_topo_esq": (-p["anexo_largura"], 0, p["anexo_altura"]),
        "adm_frente_esq_topo": (ax0, ay, p["adm_altura"]),
        "adm_frente_esq_base": (ax0, ay, 0),
        "adm_fundo_esq_topo": (ax0, p["adm_y_fundo"], p["adm_altura"]),
        "adm_frente_dir_topo": (ax0 + p["adm_largura"], ay, p["adm_altura"]),
        "adm_frente_dir_base": (ax0 + p["adm_largura"], ay, 0),
        "torre_esq_topo": (tx, ty, p["torre_altura"]),
        "torre_esq_base": (tx, ty, 0),
        "torre_dir_topo": (tx + p["torre_largura"], ty, p["torre_altura"]),
        "cerca_poste1_base": (p["cerca_px1"], p["cerca_y"], 0),
        "cerca_poste1_topo": (p["cerca_px1"], p["cerca_y"], p["cerca_altura"]),
        "cerca_poste2_base": (p["cerca_px2"], p["cerca_y"], 0),
        "cerca_poste2_topo": (p["cerca_px2"], p["cerca_y"], p["cerca_altura"]),
        "pessoa_pes": (p["pessoa_x"], p["pessoa_y"], 0),
        "pessoa_cabeca": (p["pessoa_x"], p["pessoa_y"], ALTURA_PESSOA),
        "meiofio_esq": (p["meiofio_x1"], p["meiofio_y"], 0),
        "meiofio_dir": (p["meiofio_x2"], p["meiofio_y"], 0),
        "g2_frente_dir_topo": (p["g2_x_dir"], p["g2_y_frente"], p["g2_altura"]),
        "g2_frente_dir_base": (p["g2_x_dir"], p["g2_y_frente"], 0),
    }


def rot_camera(guinada, inclinacao, rolagem):
    """Matriz mundo<-camera no padrao do Blender (euler XYZ = 90+incl, rolagem, guinada)."""
    rx, ry, rz = math.radians(90 + inclinacao), math.radians(rolagem), math.radians(guinada)
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def projetar(cam, P):
    x, y, z, gu, inc, rol, f = cam
    R = rot_camera(gu, inc, rol)
    pc = R.T @ (np.asarray(P, float) - np.array([x, y, z]))
    prof = -pc[2]
    if prof < 0.1:
        prof = 0.1
    return np.array([W / 2 + f * pc[0] / prof, H / 2 - f * pc[1] / prof])


def desempacotar(v):
    p = dict(zip(NOMES, v[: len(NOMES)]))
    cams = {}
    for i, k in enumerate(ORDEM_CAMS):
        cams[k] = v[len(NOMES) + 7 * i: len(NOMES) + 7 * (i + 1)]
    return p, cams


def residuos(v, obs):
    p, cams = desempacotar(v)
    pts = pontos_modelo(p)
    r = []
    for k, marcados in obs.items():
        for nome, uv in marcados.items():
            r.extend((projetar(cams[k], pts[nome]) - np.array(uv)) / SIGMA_PX)
    for k, (f0, sig) in PRIOR_FOCAL.items():
        r.append((cams[k][6] - f0) / sig)
    for nome in NOMES:
        ini, sig = PARAMS[nome]
        r.append((p[nome] - ini) / sig)
    return np.array(r)


def main():
    from scipy.optimize import least_squares  # so e necessario para resolver, nao para projetar

    ap = argparse.ArgumentParser()
    ap.add_argument("--overlay", action="store_true")
    args = ap.parse_args()

    with open(os.path.join(RAIZ, "referencias", "pontos_correspondencia.json")) as fh:
        dados = json.load(fh)
    obs = dados["pontos"]

    v0 = [PARAMS[n][0] for n in NOMES]
    for k in ORDEM_CAMS:
        v0 += CAMS_INI[k]
    sol = least_squares(residuos, np.array(v0, float), args=(obs,), loss="soft_l1", f_scale=2.0, max_nfev=20000)
    p, cams = desempacotar(sol.x)
    pts = pontos_modelo(p)

    relatorio = {"parametros": {n: round(float(p[n]), 2) for n in NOMES}, "cameras": {}, "erro_px": {}}
    for k in ORDEM_CAMS:
        x, y, z, gu, inc, rol, f = [float(c) for c in cams[k]]
        erros = {n: round(float(np.linalg.norm(projetar(cams[k], pts[n]) - np.array(uv))), 1) for n, uv in obs[k].items()}
        relatorio["erro_px"][k] = {"medio": round(float(np.mean(list(erros.values()))), 2), "max": max(erros.values()), "por_ponto": erros}
        relatorio["cameras"][k] = {
            "posicao": [round(x, 2), round(y, 2), round(z, 2)],
            "rotacao_euler_graus": [round(90 + inc, 2), round(rol, 2), round(gu, 2)],
            "focal_px": round(f, 1),
            "lente_mm_sensor36": round(f / W * 36, 2),
        }
    with open(os.path.join(RAIZ, "config", "calibracao.json"), "w") as fh:
        json.dump(relatorio, fh, indent=2, ensure_ascii=False)
    print(json.dumps({k: relatorio[k] for k in ("parametros", "cameras")}, indent=1, ensure_ascii=False))
    for k in ORDEM_CAMS:
        print(k, "erro medio", relatorio["erro_px"][k]["medio"], "px | max", relatorio["erro_px"][k]["max"])

    if args.overlay:
        from PIL import Image, ImageDraw
        os.makedirs(os.path.join(RAIZ, "saida", "comparacao"), exist_ok=True)
        for k in ORDEM_CAMS:
            im = Image.open(os.path.join(RAIZ, dados["imagens"][k])).convert("RGB")
            d = ImageDraw.Draw(im)
            for n, uv in obs[k].items():
                q = projetar(cams[k], pts[n])
                d.ellipse([uv[0] - 5, uv[1] - 5, uv[0] + 5, uv[1] + 5], outline=(0, 255, 0), width=2)
                d.line([tuple(uv), tuple(q)], fill=(255, 0, 0), width=2)
                d.ellipse([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(255, 0, 0))
            im.save(os.path.join(RAIZ, "saida", "comparacao", f"pontos_reprojetados_{k}.png"))


if __name__ == "__main__":
    main()
