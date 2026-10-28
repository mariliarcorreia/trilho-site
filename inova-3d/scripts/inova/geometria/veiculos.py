"""Veiculos do patio (posicoes do dia da filmagem) por instancias de modelos.

Os modelos ficam em colecoes fora da cena ("MODELO_*") e sao instanciados por
empties. Assim, 40 motos compartilham a mesma malha. Nesta fase os modelos sao
volumetricos (escala, silhueta e cor corretas); o detalhamento fica para a fase
de direcao de arte.
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

from ..core import cena
from ..materiais.biblioteca import obter as M

# comprimento, largura, altura da carroceria, (cabine x0, x1, altura do topo), cacamba?
TIPOS = {
    "picape": dict(L=5.30, W=1.86, zc=1.02, cab=(-0.45, 1.25, 1.82), cacamba=True, roda=0.39, eixo=1.62),
    "picape_compacta": dict(L=4.47, W=1.73, zc=0.92, cab=(-0.15, 1.15, 1.56), cacamba=True, roda=0.33, eixo=1.35),
    "sedan": dict(L=4.60, W=1.78, zc=0.92, cab=(-1.15, 0.95, 1.45), cacamba=False, roda=0.32, eixo=1.38),
    "hatch": dict(L=4.00, W=1.73, zc=0.92, cab=(-1.55, 0.65, 1.48), cacamba=False, roda=0.32, eixo=1.25),
}
CORES_CARRO = {"preto": "carro_preto", "prata": "carro_prata", "branco": "carro_branco", "grafite": "carro_grafite"}


def _colecao_modelo(nome):
    col = bpy.data.collections.get(nome)
    if col is None:
        col = bpy.data.collections.new(nome)
    else:
        cena._apagar_conteudo(col)
    return col


def _cabine(nome, col, x0, x1, z0, z1, W, mat):
    """Cabine trapezoidal (para-brisa e vidro traseiro inclinados)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    comp = x1 - x0
    for v in bm.verts:
        topo = v.co.z > 0
        fx = 0.62 if topo else 1.0
        fy = 0.86 if topo else 1.0
        v.co = Vector(((x0 + x1) / 2 + v.co.x * comp * fx + (-0.08 * comp if topo else 0),
                       v.co.y * W * fy, z0 + (v.co.z + 0.5) * (z1 - z0)))
    obj = cena.objeto_bmesh(nome, col, bm, mat)
    mod = obj.modifiers.new("chanfro", "BEVEL")
    mod.width = 0.05
    mod.segments = 2
    return obj


def _modelo_carro(tipo, cor):
    d = TIPOS[tipo]
    col = _colecao_modelo(f"MODELO_{tipo}_{cor}")
    tinta = M(CORES_CARRO[cor])
    L, W, zc, r = d["L"], d["W"], d["zc"], d["roda"]
    if d["cacamba"]:
        cx0, cx1, ztopo = d["cab"]
        cena.caixa("frente", col, cx0, L / 2, -W / 2, W / 2, r * 0.75, zc, tinta, chanfro=0.08)
        cena.caixa("cacamba_piso", col, -L / 2, cx0, -W / 2, W / 2, r * 0.75, zc - 0.35, tinta, chanfro=0.04)
        for lado, s in (("e", -1), ("d", 1)):
            cena.caixa(f"cacamba_{lado}", col, -L / 2, cx0, s * W / 2 - (0.07 if s > 0 else 0), s * W / 2 + (0.07 if s < 0 else 0),
                       zc - 0.35, zc + 0.02, tinta, chanfro=0.02)
        cena.caixa("tampa", col, -L / 2, -L / 2 + 0.07, -W / 2, W / 2, zc - 0.35, zc + 0.02, tinta, chanfro=0.02)
        _cabine("cabine", col, cx0, cx1, zc, ztopo, W * 0.98, M("vidro_carro"))
        cena.caixa("teto", col, cx0 + 0.25, cx1 - 0.45, -W * 0.40, W * 0.40, ztopo - 0.02, ztopo + 0.03, tinta, chanfro=0.02)
    else:
        cx0, cx1, ztopo = d["cab"]
        cena.caixa("carroceria", col, -L / 2, L / 2, -W / 2, W / 2, r * 0.75, zc, tinta, chanfro=0.12)
        _cabine("cabine", col, cx0, cx1, zc, ztopo, W * 0.96, M("vidro_carro"))
        cena.caixa("teto", col, cx0 + 0.35, cx1 - 0.45, -W * 0.39, W * 0.39, ztopo - 0.02, ztopo + 0.025, tinta, chanfro=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cena.cilindro(f"pneu_{sx}{sy}", col, sx * d["eixo"], sy * (W / 2 - 0.13), r, r, 0.24, M("pneu"), 20, eixo="Y")
            cena.cilindro(f"aro_{sx}{sy}", col, sx * d["eixo"], sy * (W / 2 - 0.005), r, r * 0.62, 0.02, M("roda"), 16, eixo="Y")
    # farois e lanternas
    cena.caixa("farois", col, L / 2 - 0.02, L / 2 + 0.01, -W / 2 + 0.12, W / 2 - 0.12, zc - 0.18, zc - 0.06, M("metal_galvanizado"))
    cena.caixa("lanternas", col, -L / 2 - 0.01, -L / 2 + 0.02, -W / 2 + 0.1, W / 2 - 0.1, zc - 0.2, zc - 0.08, M("moto_vermelha"))
    return col


def _modelo_moto(cor):
    col = _colecao_modelo(f"MODELO_moto_{cor}")
    tinta = M(f"moto_{cor}")
    for s in (-1, 1):
        cena.cilindro(f"pneu_{s}", col, s * 0.68, 0.0, 0.31, 0.31, 0.1, M("pneu"), 18, eixo="Y")
        cena.cilindro(f"aro_{s}", col, s * 0.68, 0.0, 0.31, 0.2, 0.11, M("roda"), 12, eixo="Y")
    cena.caixa("motor", col, -0.25, 0.3, -0.16, 0.16, 0.3, 0.62, M("moto_cinza"), chanfro=0.03)
    cena.caixa("tanque", col, 0.0, 0.45, -0.17, 0.17, 0.72, 0.95, tinta, chanfro=0.06)
    cena.caixa("banco", col, -0.62, 0.05, -0.14, 0.14, 0.78, 0.9, M("moto_preta"), chanfro=0.04)
    cena.caixa("rabeta", col, -0.8, -0.3, -0.12, 0.12, 0.7, 0.82, tinta, chanfro=0.03)
    cena.caixa("garfo", col, 0.55, 0.62, -0.08, 0.08, 0.3, 1.02, M("roda"))
    cena.cilindro("guidao", col, 0.52, 0.0, 1.05, 0.02, 0.72, M("moto_preta"), 8, eixo="Y")
    cena.caixa("farol", col, 0.6, 0.72, -0.08, 0.08, 0.9, 1.02, M("moto_cinza"), chanfro=0.03)
    return col


def _modelo_bicicleta():
    col = _colecao_modelo("MODELO_bicicleta")
    for s in (-1, 1):
        cena.cilindro(f"roda_{s}", col, s * 0.52, 0.0, 0.34, 0.34, 0.035, M("pneu"), 24, eixo="Y")
    cena.caixa("quadro", col, -0.5, 0.5, -0.02, 0.02, 0.5, 0.56, M("moto_cinza"))
    cena.caixa("selim", col, -0.25, -0.05, -0.05, 0.05, 0.92, 0.97, M("moto_preta"))
    cena.caixa("canote", col, -0.17, -0.13, -0.02, 0.02, 0.5, 0.92, M("moto_cinza"))
    cena.cilindro("guidao", col, 0.45, 0.0, 0.98, 0.015, 0.55, M("moto_preta"), 8, eixo="Y")
    return col


def construir(cfg):
    v = cfg["veiculos"]
    col = cena.colecao_limpa("Fachada/Veiculos")
    modelos = {}

    def modelo(chave, fabrica):
        if chave not in modelos:
            modelos[chave] = fabrica()
        return modelos[chave]

    for i, c in enumerate(v["carros"]):
        m = modelo((c["tipo"], c["cor"]), lambda c=c: _modelo_carro(c["tipo"], c["cor"]))
        cena.instanciar(f"Carro_{i:02d}_{c['tipo']}", col, m, (c["x"], c["y"], 0.0), c["rot"])

    rng = random.Random(11)
    cores = ["preta", "preta", "vermelha", "cinza", "preta", "vermelha"]
    n = 0
    for f in v["fileiras_motos"]:
        x = f["x0"]
        while x <= f["x1"] + 1e-6:
            cor = rng.choice(cores)
            m = modelo(("moto", cor), lambda cor=cor: _modelo_moto(cor))
            cena.instanciar(f"Moto_{n:02d}", col, m, (x + rng.uniform(-0.08, 0.08), f["y"] + rng.uniform(-0.15, 0.15), 0.0),
                            f["rot"] + rng.uniform(-6, 6))
            x += f["passo"]
            n += 1

    b = v["bicicletas"]
    x = b["x0"]
    k = 0
    while x <= b["x1"] + 1e-6:
        cena.instanciar(f"Bicicleta_{k}", col, modelo("bike", _modelo_bicicleta), (x, b["y"], 0.0), 90)
        x += b["passo"]
        k += 1
    return modelos


def construir_contexto(cfg, modelos=None):
    """Volumes vizinhos simplificados (escala e horizonte) e carros da rua lateral."""
    cx = cfg["contexto"]
    col = cena.colecao_limpa("Contexto")
    if not cx.get("ativo", True):
        return
    mats = {"concreto": "contexto_concreto", "branco": "contexto_branco"}
    for vol in cx["volumes"]:
        cena.caixa(f"Ctx_{vol['nome']}", col, vol["x0"], vol["x1"], vol["y0"], vol["y1"], 0.0, vol["altura"],
                   M(mats[vol["cor"]]))
        cena.caixa(f"Ctx_{vol['nome']}_cobertura", col, vol["x0"] - 0.3, vol["x1"] + 0.3, vol["y0"] - 0.3, vol["y1"] + 0.3,
                   vol["altura"], vol["altura"] + 0.15, M("contexto_telhado"))
    rng = random.Random(3)
    cores = ["branco", "prata", "preto", "prata"]
    for i, (x, y) in enumerate(cx["carros_rua_lateral"]):
        cor = rng.choice(cores)
        m = bpy.data.collections.get(f"MODELO_sedan_{cor}") or _modelo_carro("sedan", cor)
        cena.instanciar(f"Ctx_carro_rua_{i}", col, m, (x, y, 0.0), 90 + rng.uniform(-3, 3))
    el = cfg["terreno"]["estacionamento_lateral"]
    for fila, (y, n) in enumerate(((el["y1"] - 3.0, 6), (el["y0"] + 3.2, 9))):
        for k in range(n):
            x = el["x0"] + 2.5 + k * (el["x1"] - el["x0"] - 5) / max(1, n - 1)
            cor = rng.choice(cores)
            tipo = rng.choice(["sedan", "hatch"])
            m = bpy.data.collections.get(f"MODELO_{tipo}_{cor}") or _modelo_carro(tipo, cor)
            cena.instanciar(f"Ctx_carro_est_{fila}_{k}", col, m, (x, y, 0.0), 90 + rng.uniform(-4, 4))
