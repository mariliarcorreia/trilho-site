"""Predio administrativo de dois pavimentos, com torre grafite e emblema."""
import math
import random

import bmesh
import bpy
from mathutils import Vector

from ..core import cena
from ..materiais.biblioteca import obter as M


def _cortador(nome, col, x0, x1, y0, y1, z0, z1):
    c = cena.caixa(nome, col, x0, x1, y0, y1, z0, z1)
    c.hide_render = True
    c.display_type = "WIRE"
    return c


def _subtrair(alvo, cortador):
    mod = alvo.modifiers.new(f"furo_{cortador.name}", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cortador
    mod.solver = "EXACT"


def _janela(nome, col, col_cort, parede, j, yf, laminas):
    """Vao recuado com vidro fume, fundo escuro, moldura e brises horizontais."""
    rec = 0.16
    corte = _cortador(f"{nome}_corte", col_cort, j["x0"], j["x1"], yf - 0.2, yf + rec, j["z0"], j["z1"])
    _subtrair(parede, corte)
    cena.caixa(f"{nome}_fundo", col, j["x0"], j["x1"], yf + rec - 0.02, yf + rec, j["z0"], j["z1"], M("interior_escuro"))
    cena.caixa(f"{nome}_vidro", col, j["x0"], j["x1"], yf + rec - 0.05, yf + rec - 0.04, j["z0"], j["z1"], M("vidro_escuro"))
    e = 0.05
    pecas = [
        cena.caixa(f"{nome}_mold_inf", col, j["x0"], j["x1"], yf - 0.03, yf + rec, j["z0"], j["z0"] + e, M("esquadria")),
        cena.caixa(f"{nome}_mold_sup", col, j["x0"], j["x1"], yf - 0.03, yf + rec, j["z1"] - e, j["z1"], M("esquadria")),
        cena.caixa(f"{nome}_mold_esq", col, j["x0"], j["x0"] + e, yf - 0.03, yf + rec, j["z0"], j["z1"], M("esquadria")),
        cena.caixa(f"{nome}_mold_dir", col, j["x1"] - e, j["x1"], yf - 0.03, yf + rec, j["z0"], j["z1"], M("esquadria")),
    ]
    passo = (j["z1"] - j["z0"] - 2 * e) / laminas
    for i in range(laminas):
        zc = j["z0"] + e + passo * (i + 0.5)
        pecas.append(cena.caixa(f"{nome}_brise_{i}", col, j["x0"] + e, j["x1"] - e, yf - 0.02, yf + 0.06,
                                zc - passo * 0.28, zc + passo * 0.28, M("brise")))
    cena.juntar(f"{nome}_esquadria", pecas)


def _muda(nome, col, x, y, rng):
    """Planta ornamental de folhas lanceoladas (como as mudas da jardineira nas fotos)."""
    bm = bmesh.new()
    n = rng.randint(9, 13)
    for i in range(n):
        ang = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        incl = math.radians(rng.uniform(20, 45))
        comp = rng.uniform(0.45, 0.7)
        base = Vector((x, y, 0.25))
        ponta = base + Vector((math.cos(ang) * math.sin(incl), math.sin(ang) * math.sin(incl), math.cos(incl))) * comp
        lado = Vector((-math.sin(ang), math.cos(ang), 0)) * 0.035
        v = [bm.verts.new(base + lado), bm.verts.new(base - lado), bm.verts.new(ponta)]
        bm.faces.new(v)
    return cena.objeto_bmesh(nome, col, bm, M("vegetacao"))


def construir(cfg):
    a = cfg["predio_administrativo"]
    col = cena.colecao_limpa("Fachada/Administrativo")
    col_cort = cena.colecao_limpa("Fachada/Administrativo_cortadores")
    x0, x1, yf, yb = a["x0"], a["x1"], a["y_frente"], a["y_fundo"]
    hp = a["altura_parede"]
    v = a["vidro"]

    # corpo principal (a direita do vidro) e bloco posterior ate o galpao
    parede = cena.caixa("ADM_corpo", col, v["x1"], x1, yf, yb, 0.0, hp, M("alvenaria_branca"))
    cena.caixa("ADM_bloco_fundo", col, x0, x1, a["platibanda_fundo_y"], yb, 0.0, hp + a["platibanda_altura"] + 0.62,
               M("alvenaria_branca"))

    # ambiente envidracado a esquerda: paredes, lajes e fundo escuros
    prof_hall = 6.2
    yv = yf + v["recuo"]
    cena.caixa("ADM_hall_parede_esq", col, x0, x0 + 0.15, yf, yf + prof_hall, 0.0, hp, M("alvenaria_branca"))
    cena.caixa("ADM_hall_fundo", col, x0, v["x1"], yf + prof_hall, yf + prof_hall + 0.2, 0.0, hp, M("interior_escuro"))
    cena.caixa("ADM_hall_laje", col, x0, v["x1"], yv, yf + prof_hall, v["travessa_z"] + 0.05, v["travessa_z"] + 0.3,
               M("interior_escuro"))
    cena.caixa("ADM_hall_piso", col, x0, v["x1"], yf, yf + prof_hall, 0.0, 0.05, M("concreto"))
    cena.caixa("ADM_verga_vidro", col, x0, v["x1"], yf, yf + 0.3, v["z1"], hp, M("alvenaria_branca"))
    cena.caixa("ADM_hall_teto", col, x0, v["x1"], yf + 0.3, yf + prof_hall, v["z1"], hp, M("interior_escuro"))
    cena.caixa("ADM_vidro_fachada", col, v["x0"], v["x1"], yv, yv + 0.02, 0.05, v["z1"], M("vidro_escuro"))
    e = 0.07
    pecas = [
        cena.caixa("ADM_caixilho_inf", col, v["x0"], v["x1"], yv - 0.06, yv + 0.08, 0.0, 0.08, M("esquadria")),
        cena.caixa("ADM_caixilho_sup", col, v["x0"], v["x1"], yv - 0.06, yv + 0.08, v["z1"] - e, v["z1"], M("esquadria")),
        cena.caixa("ADM_caixilho_esq", col, v["x0"], v["x0"] + e, yv - 0.06, yv + 0.08, 0.0, v["z1"], M("esquadria")),
        cena.caixa("ADM_caixilho_dir", col, v["x1"] - e, v["x1"], yv - 0.06, yv + 0.08, 0.0, v["z1"], M("esquadria")),
        cena.caixa("ADM_travessa", col, v["x0"], v["x1"], yv - 0.06, yv + 0.08, v["travessa_z"] - e / 2,
                   v["travessa_z"] + e / 2, M("esquadria")),
    ]
    for i, mx in enumerate(v["montantes_x"]):
        pecas.append(cena.caixa(f"ADM_montante_{i}", col, mx - e / 2, mx + e / 2, yv - 0.06, yv + 0.08, 0.0, v["z1"],
                                M("esquadria")))
    cena.juntar("ADM_caixilharia", pecas)

    # janelas com brises
    for i, j in enumerate(a["janelas"]):
        _janela(f"ADM_janela_{i}", col, col_cort, parede, j, yf, a["brise_laminas"])

    # beiral em ACM (frente e laterais), laje de cobertura e platibanda posterior
    av = a["beiral_avanco"]
    yp = a["platibanda_fundo_y"]
    cena.caixa("ADM_beiral", col, x0 - av, x1 + av, yf - av, yp, a["beiral_z0"], a["beiral_z1"], M("cinza_acm"), chanfro=0.02)
    cena.caixa("ADM_laje_cobertura", col, x0, x1, yf, yp, a["beiral_z0"], a["beiral_z1"] - 0.25, M("concreto"))
    cx = a["caixa_cobertura"]
    cena.caixa("ADM_caixa_cobertura", col, cx["x0"], cx["x1"], cx["y0"], cx["y1"], a["beiral_z1"] - 0.25,
               a["beiral_z1"] - 0.25 + cx["altura"], M("alvenaria_branca"), chanfro=0.02)

    # torre grafite com juntas de painel e emblema da marca
    t = a["torre"]
    yt = yf - t["avanco"]
    cena.caixa("ADM_torre", col, t["x0"], t["x1"], yt, yf + 1.0, 0.0, t["altura"], M("grafite_acm"), chanfro=0.015)
    juntas = []
    for i, zj in enumerate(t["juntas_z"]):
        juntas.append(cena.caixa(f"ADM_torre_junta_{i}", col, t["x0"] - 0.005, t["x1"] + 0.005, yt - 0.006, yf + 1.0,
                                 zj - 0.008, zj + 0.008, M("interior_escuro")))
    xm = (t["x0"] + t["x1"]) / 2
    juntas.append(cena.caixa("ADM_torre_junta_v", col, xm - 0.008, xm + 0.008, yt - 0.006, yt, 0.0, t["juntas_z"][0],
                             M("interior_escuro")))
    cena.juntar("ADM_torre_juntas", juntas)
    em = t["emblema"]
    r = em["raio"]
    ye = yt - 0.02
    cena.plano_uv("ADM_emblema", col, [(em["x"] - r, ye, em["z"] - r), (em["x"] + r, ye, em["z"] - r),
                                       (em["x"] + r, ye, em["z"] + r), (em["x"] - r, ye, em["z"] + r)], M("emblema_aco"))

    # jardineira com mudas e calcada frontal
    jd = a["jardineira"]
    cena.caixa("ADM_jardineira", col, jd["x0"], jd["x1"], yf - jd["profundidade"], yf, 0.0, 0.25, M("concreto"))
    cena.caixa("ADM_jardineira_terra", col, jd["x0"] + 0.06, jd["x1"] - 0.06, yf - jd["profundidade"] + 0.06, yf,
               0.0, 0.24, M("terra_vermelha"))
    rng = random.Random(7)
    mudas = []
    for i in range(jd["mudas"]):
        x = jd["x0"] + (i + 0.5) * (jd["x1"] - jd["x0"]) / jd["mudas"]
        mudas.append(_muda(f"ADM_muda_{i}", col, x, yf - jd["profundidade"] / 2, rng))
    cena.juntar("ADM_mudas", mudas)
    cena.caixa("ADM_calcada", col, x0 - 0.5, x1 + 0.5, a["calcada_frente"]["y0"], yf, 0.0, 0.1, M("concreto"))

    # cortadores nao aparecem no render nem atrapalham a viewport
    lc = bpy.context.view_layer.layer_collection.children["INOVA"].children["Fachada"].children[col_cort.name]
    lc.hide_viewport = True
