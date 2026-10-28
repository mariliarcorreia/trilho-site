"""Piso do patio, calcada, avenida duplicada, rua lateral, terreno vizinho,
muros, gradil com concertina e poste de iluminacao publica."""
import math

import bmesh
import bpy
from mathutils import Vector

from ..core import cena
from ..materiais.biblioteca import obter as M


def _faixas_tracejadas(nome, col, y, x0, x1, traco, intervalo, largura=0.12):
    pecas = []
    x = x0
    i = 0
    while x < x1:
        pecas.append(cena.caixa(f"{nome}_{i}", col, x, x + traco, y - largura / 2, y + largura / 2, 0.0, 0.012,
                                M("faixa_viaria")))
        x += traco + intervalo
        i += 1
    return cena.juntar(nome, pecas)


def construir_pisos(cfg):
    t = cfg["terreno"]
    col = cena.colecao_limpa("Fachada/Terreno")
    XA, XB = -400.0, 600.0
    cena.caixa("Chao_distante", col, -1500, 1500, -1500, 1500, -0.25, -0.05, M("terreno_distante"))

    p = t["patio"]
    cena.caixa("Patio", col, p["x0"], p["x1"], p["y0"], p["y1"] + 0.5, -0.05, 0.02, M("patio"))
    c = t["calcada"]
    cena.caixa("Calcada", col, XA, XB, c["y0"], c["y1"], -0.05, 0.10, M("calcada"))
    cena.caixa("Meio_fio", col, XA, XB, c["y0"] - 0.15, c["y0"], -0.05, 0.14, M("concreto"))

    av = t["avenida"]
    cena.caixa("Pista_proxima", col, XA, XB, av["pista_proxima"][0], av["pista_proxima"][1], -0.05, 0.0, M("asfalto"))
    cena.caixa("Pista_oposta", col, XA, XB, av["pista_oposta"][0], av["pista_oposta"][1], -0.05, 0.0, M("asfalto"))
    cy0, cy1 = av["canteiro"]
    cena.caixa("Canteiro", col, XA, XB, cy0, cy1, -0.05, 0.12, M("grama_seca"))
    cena.caixa("Canteiro_guia_1", col, XA, XB, cy0, cy0 + 0.15, -0.05, 0.15, M("concreto"))
    cena.caixa("Canteiro_guia_2", col, XA, XB, cy1 - 0.15, cy1, -0.05, 0.15, M("concreto"))
    cena.caixa("Acostamento_oposto", col, XA, XB, av["pista_oposta"][0] - 25, av["pista_oposta"][0], -0.05, 0.04,
               M("grama_seca"))

    # sinalizacao horizontal
    pecas = [
        cena.caixa("Bordo_1", col, XA, XB, c["y0"] - 0.45, c["y0"] - 0.33, 0.0, 0.012, M("faixa_viaria")),
        cena.caixa("Bordo_2", col, XA, XB, cy1 - 0.45, cy1 - 0.33, 0.0, 0.012, M("faixa_viaria")),
        cena.caixa("Bordo_3", col, XA, XB, cy0 - 0.45, cy0 - 0.33, 0.0, 0.012, M("faixa_viaria")),
        cena.caixa("Bordo_4", col, XA, XB, av["pista_oposta"][0] + 0.33, av["pista_oposta"][0] + 0.45, 0.0, 0.012,
                   M("faixa_viaria")),
    ]
    cena.juntar("Faixas_bordo", pecas)
    for i, y in enumerate(av["faixa_tracejada_y"]):
        _faixas_tracejadas(f"Faixa_tracejada_{i}", col, y, XA, XB, av["traco"], av["intervalo"])

    rl = t["rua_lateral"]
    cena.caixa("Rua_lateral", col, rl["x0"] + 1.6, rl["x1"] - 1.6, c["y1"], rl["y1"], -0.05, 0.005, M("asfalto"))
    cena.caixa("Rua_lateral_calcada_esq", col, rl["x0"], rl["x0"] + 1.6, c["y1"], rl["y1"], -0.05, 0.1, M("calcada"))
    cena.caixa("Rua_lateral_calcada_dir", col, rl["x1"] - 1.6, rl["x1"], c["y1"], rl["y1"], -0.05, 0.1, M("calcada"))

    tl = t["terreno_lateral"]
    cena.caixa("Terreno_lateral", col, tl["x0"], tl["x1"], tl["y0"], tl["y1"], -0.05, 0.03, M("terra_vermelha"))
    el = t["estacionamento_lateral"]
    cena.caixa("Estacionamento_lateral", col, el["x0"], el["x1"], el["y0"], el["y1"], -0.05, 0.02, M("patio"))


def _concertina(nome, col, pontos, z, raio=0.27, passo=0.16, pts_volta=10):
    """Arame farpado em espiral sobre o gradil, seguindo a poligonal da cerca."""
    curva = bpy.data.curves.new(nome, "CURVE")
    curva.dimensions = "3D"
    curva.bevel_depth = 0.006
    curva.bevel_resolution = 0
    for a, b in zip(pontos[:-1], pontos[1:]):
        a, b = Vector((*a, z)), Vector((*b, z))
        d = b - a
        comp = d.length
        u = d.normalized()
        lado = Vector((-u.y, u.x, 0))
        cima = Vector((0, 0, 1))
        n = max(2, int(comp / passo * pts_volta))
        sp = curva.splines.new("POLY")
        sp.points.add(n - 1)
        for i in range(n):
            s = i / (n - 1)
            ang = 2 * math.pi * s * comp / passo
            pos = a + d * s + lado * math.cos(ang) * raio + cima * math.sin(ang) * raio
            sp.points[i].co = (*pos, 1.0)
    obj = bpy.data.objects.new(nome, curva)
    col.objects.link(obj)
    obj.data.materials.append(M("metal_galvanizado"))
    return obj


def _trecho_gradil(nome, col, a, b, h, passo, reforcado=False):
    a, b = Vector((*a, 0)), Vector((*b, 0))
    d = b - a
    comp = d.length
    u = d.normalized()
    ang = math.atan2(u.y, u.x)
    pecas = []
    n = max(1, round(comp / passo))
    lado = 0.05 if not reforcado else 0.08
    for i in range(n + 1):
        p = a + d * (i / n)
        pecas.append(cena.caixa(f"{nome}_poste_{i}", col, -lado, lado, -lado, lado, 0.0, h + 0.08, M("gradil")))
        pecas[-1].location = (p.x, p.y, 0)
        pecas[-1].rotation_euler = (0, 0, ang)
    # trilhos inferior e superior e tela soldada (UV em metros ao longo do trecho)
    for k, z in enumerate((0.08, h - 0.04)):
        tr = cena.caixa(f"{nome}_trilho_{k}", col, 0, comp, -0.025, 0.025, z - 0.025, z + 0.025, M("gradil"))
        tr.location = (a.x, a.y, 0)
        tr.rotation_euler = (0, 0, ang)
        pecas.append(tr)
    tela = cena.plano_uv(f"{nome}_tela", col, [(0, 0, 0.1), (comp, 0, 0.1), (comp, 0, h - 0.04), (0, 0, h - 0.04)],
                         M("tela_gradil"))
    uv = tela.data.uv_layers[0]
    for i, co in enumerate(((0, 0.1), (comp, 0.1), (comp, h - 0.04), (0, h - 0.04))):
        uv.data[i].uv = co
    tela.location = (a.x, a.y, 0)
    tela.rotation_euler = (0, 0, ang)
    for obj in pecas:
        obj.select_set(False)
    with bpy.context.temp_override(selected_editable_objects=pecas, active_object=pecas[0]):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
    cena.juntar(f"{nome}_estrutura", pecas)
    return tela


def construir_cercamento(cfg):
    t = cfg["terreno"]
    col = cena.colecao_limpa("Fachada/Cercamento")
    ce = t["cerca"]
    h, passo, y = ce["altura"], ce["passo_postes"], ce["y"]
    pv, pp = ce["portao_veiculos"], ce["portao_pedestres"]

    # poligonal: frente (direita -> portoes -> esquerda), chanfro e lateral esquerda
    trechos = [
        ((ce["x1"], y), (pp[1], y), False),
        ((pp[1], y), (pp[0], y), True),
        ((pv[1], y), (pv[0], y), True),
        ((pv[0], y), tuple(ce["chanfro_esq"][0]), False),
        (tuple(ce["chanfro_esq"][0]), tuple(ce["chanfro_esq"][1]), False),
        (tuple(ce["chanfro_esq"][1]), (ce["lateral_esq_x"], ce["lateral_esq_y1"]), False),
    ]
    for i, (a, b, reforco) in enumerate(trechos):
        _trecho_gradil(f"Gradil_{i}", col, a, b, h, passo if not reforco else 10.0, reforco)
    # trilho do portao de correr
    cena.caixa("Portao_trilho", col, pv[0] - 4.0, pv[1], y - 0.05, y + 0.05, 0.0, 0.03, M("metal_galvanizado"))

    if ce.get("concertina"):
        pontos = [(ce["x1"], y), tuple(ce["chanfro_esq"][0]), tuple(ce["chanfro_esq"][1]),
                  (ce["lateral_esq_x"], ce["lateral_esq_y1"])]
        _concertina("Concertina", col, pontos, h + 0.28)

    md = t["muro_direito"]
    cena.caixa("Muro_direito", col, md["x"], md["x"] + 0.2, md["y0"], md["y1"], 0.0, md["altura"], M("bloco_concreto"))
    mf = t["muro_fundo_g2"]
    cena.caixa("Muro_fundo_G2", col, mf["x0"], mf["x1"], mf["y"] - 0.2, mf["y"], 0.0, mf["altura"], M("bloco_concreto"))

    # poste de iluminacao publica (concreto conico, braco e luminaria)
    po = t["poste"]
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.17, radius2=0.09, depth=po["altura"])
    bmesh.ops.translate(bm, verts=bm.verts, vec=(po["x"], po["y"], po["altura"] / 2))
    poste = cena.objeto_bmesh("Poste", col, bm, M("poste_concreto"))
    for f in poste.data.polygons:
        f.use_smooth = len(f.vertices) == 4
    zb = po["z_luminaria"] + 0.4
    cena.cilindro("Poste_braco", col, po["x"] - po["braco"] / 2, po["y"], zb, 0.04, po["braco"], M("metal_galvanizado"),
                  12, eixo="X")
    cena.caixa("Poste_luminaria", col, po["x"] - po["braco"] - 0.35, po["x"] - po["braco"] + 0.25, po["y"] - 0.17,
               po["y"] + 0.17, zb - 0.16, zb + 0.06, M("cinza_acm"), chanfro=0.03)


def construir(cfg):
    construir_pisos(cfg)
    construir_cercamento(cfg)
