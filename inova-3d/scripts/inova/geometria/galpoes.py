"""Galpao principal (G1), anexo lateral, galpao secundario (G2) e paineis solares."""
import math

import bmesh
import bpy

from ..core import cena
from ..materiais.biblioteca import obter as M


def _telhado_duas_aguas(nome, col, x0, x1, y0, y1, z_beiral, y_cumeeira, inclinacao, mat_telhado, mat_oitao):
    """Telhado com cumeeira paralela a fachada e oitoes laterais fechados."""
    t = math.tan(math.radians(inclinacao))
    z_cume = z_beiral + (y_cumeeira - y0) * t
    z_fundo = z_cume - (y1 - y_cumeeira) * t
    bm = bmesh.new()
    v = [bm.verts.new(c) for c in (
        (x0, y0, z_beiral), (x1, y0, z_beiral), (x1, y_cumeeira, z_cume), (x0, y_cumeeira, z_cume),
        (x0, y1, z_fundo), (x1, y1, z_fundo),
    )]
    bm.faces.new((v[0], v[1], v[2], v[3]))
    bm.faces.new((v[3], v[2], v[5], v[4]))
    obj = cena.objeto_bmesh(nome, col, bm, mat_telhado)
    sol = obj.modifiers.new("espessura", "SOLIDIFY")
    sol.thickness = 0.12
    # oitoes (triangulos laterais acima do beiral)
    for lado, x in (("esq", x0), ("dir", x1)):
        bm = bmesh.new()
        a = bm.verts.new((x, y0, z_beiral))
        b = bm.verts.new((x, y_cumeeira, z_cume))
        c = bm.verts.new((x, y1, z_fundo))
        d = bm.verts.new((x, y1, z_beiral))
        bm.faces.new((a, d, c, b) if lado == "esq" else (a, b, c, d))
        cena.objeto_bmesh(f"{nome}_oitao_{lado}", col, bm, mat_oitao)
    return z_cume, t


def _paredes(nome, col, x0, x1, y0, y1, h, mat, e=0.2):
    """Quatro paredes sem tampa, para o telhado ficar visivel atras da platibanda."""
    pecas = [
        cena.caixa(f"{nome}_frente", col, x0, x1, y0, y0 + e, 0.0, h, mat),
        cena.caixa(f"{nome}_fundo", col, x0, x1, y1 - e, y1, 0.0, h, mat),
        cena.caixa(f"{nome}_esq", col, x0, x0 + e, y0, y1, 0.0, h, mat),
        cena.caixa(f"{nome}_dir", col, x1 - e, x1, y0, y1, 0.0, h, mat),
    ]
    return cena.juntar(nome, pecas)


def construir_galpao_principal(cfg, col):
    g = cfg["galpao_principal"]
    W, D, H = g["largura"], g["profundidade"], g["altura_beiral"]
    x0 = g["x0"]
    fb = g["faixa_branca_altura"]

    # casca metalica e faixa inferior em alvenaria branca (frente e lateral direita visivel)
    _paredes("G1_casca", col, x0, x0 + W, 0.0, D, H, M("metal_fachada"))
    cena.caixa("G1_faixa_branca_frente", col, x0, x0 + W, -0.08, 0.0, 0.0, fb, M("alvenaria_branca"))
    cena.caixa("G1_faixa_branca_dir", col, x0 + W, x0 + W + 0.08, 0.0, D, 0.0, fb, M("alvenaria_branca"))
    cena.caixa("G1_rufo_frente", col, x0 - 0.05, x0 + W + 0.05, -0.12, 0.05, H - 0.12, H + 0.05, M("cinza_acm"))

    # colunas escuras na faixa branca
    meia = g["colunas_largura"] / 2
    pecas = []
    for i, cx in enumerate(g["colunas_x"]):
        pecas.append(cena.caixa(f"G1_coluna_{i}", col, cx - meia, cx + meia, -0.08 - g["colunas_avanco"], -0.08,
                                0.0, fb, M("pintura_grafite")))
    cena.juntar("G1_colunas", pecas)

    _telhado_duas_aguas("G1_telhado", col, x0, x0 + W, 0.0, D, H - g["platibanda"], g["cumeeira_y"],
                        g["inclinacao_telhado_graus"], M("telhado_metalico"), M("metal_fachada"))

    # letreiro oficial (variante de fachada da logomarca, sem alteracao de desenho)
    lt = g["letreiro"]
    y = -0.012  # letras aplicadas rente ao revestimento
    cena.plano_uv("G1_letreiro_inova", col, [(lt["x0"], y, lt["z0"]), (lt["x1"], y, lt["z0"]),
                                             (lt["x1"], y, lt["z1"]), (lt["x0"], y, lt["z1"])], M("logo_fachada"))

    # reservatorio metalico junto a parede
    r = g["reservatorio"]
    cena.cilindro("G1_reservatorio", col, r["x"], r["y"], 0.0, r["raio"], r["altura"], M("metal_galvanizado"))
    cena.cilindro("G1_reservatorio_tampa", col, r["x"], r["y"], r["altura"], r["raio"] * 1.03, 0.06, M("metal_galvanizado"))


def construir_anexo(cfg, col):
    a = cfg["anexo_lateral"]
    cena.caixa("Anexo_corpo", col, a["x0"], a["x1"], a["y0"], a["y1"], 0.0, a["altura"], M("alvenaria_branca"))
    cena.caixa("Anexo_cobertura", col, a["x0"] - 0.15, a["x1"], a["y0"] - 0.15, a["y1"], a["altura"], a["altura"] + 0.12,
               M("telhado_metalico"))
    v = a["veneziana"]
    cena.caixa("Anexo_veneziana_moldura", col, v["x0"], v["x1"], a["y0"] - 0.04, a["y0"], v["z0"], v["z1"], M("esquadria"))
    laminas = []
    n = 7
    passo = (v["z1"] - v["z0"]) / n
    for i in range(n):
        z = v["z0"] + passo * (i + 0.5)
        laminas.append(cena.caixa(f"Anexo_lamina_{i}", col, v["x0"] + 0.04, v["x1"] - 0.04, a["y0"] - 0.09, a["y0"] - 0.04,
                                  z - passo * 0.22, z + passo * 0.22, M("brise")))
    cena.juntar("Anexo_veneziana_laminas", laminas)


def construir_galpao_secundario(cfg, col):
    g = cfg["galpao_secundario"]
    x0, x1, y0 = g["x0"], g["x1"], g["y0"]
    y1 = y0 + g["profundidade"]
    H = g["altura_beiral"]
    _paredes("G2_casca", col, x0, x1, y0, y1, H, M("metal_fachada"))
    cena.caixa("G2_base_blocos", col, x0, x1, y0 - 0.1, y0, 0.0, g["base_blocos_altura"], M("bloco_concreto"))
    cena.caixa("G2_rufo_frente", col, x0 - 0.05, x1 + 0.05, y0 - 0.12, y0 + 0.05, H - 0.12, H + 0.05, M("cinza_acm"))
    _telhado_duas_aguas("G2_telhado", col, x0, x1, y0, y1, H - 0.1, g["cumeeira_y"], g["inclinacao_telhado_graus"],
                        M("telhado_metalico"), M("metal_fachada"))
    lt = g["letreiro"]
    y = y0 - 0.012
    cena.plano_uv("G2_letreiro_inova", col, [(lt["x0"], y, lt["z0"]), (lt["x1"], y, lt["z0"]),
                                             (lt["x1"], y, lt["z1"]), (lt["x0"], y, lt["z1"])], M("logo_fachada"))


def construir_paineis(cfg, col):
    """Blocos de modulos fotovoltaicos assentados na agua frontal do telhado do G1."""
    g = cfg["galpao_principal"]
    p = cfg["paineis_solares"]
    t = math.tan(math.radians(g["inclinacao_telhado_graus"]))
    z_beiral = g["altura_beiral"] - g["platibanda"] + 0.12  # topo da telha
    pecas = []
    for i, b in enumerate(p["blocos"]):
        def z(yy):
            return z_beiral + (min(yy, g["cumeeira_y"]) - 0.0) * t + p["altura_sobre_telhado"]
        cantos = [(b["x0"], b["y0"], z(b["y0"])), (b["x1"], b["y0"], z(b["y0"])),
                  (b["x1"], b["y1"], z(b["y1"])), (b["x0"], b["y1"], z(b["y1"]))]
        obj = cena.plano_uv(f"Solar_bloco_{i}", col, cantos, M("painel_solar"))
        sol = obj.modifiers.new("espessura", "SOLIDIFY")
        sol.thickness = 0.04
        sol.offset = 1.0
        pecas.append(obj)
    return pecas


def construir(cfg):
    col = cena.colecao_limpa("Fachada/Galpoes")
    construir_galpao_principal(cfg, col)
    construir_anexo(cfg, col)
    construir_galpao_secundario(cfg, col)
    col_sol = cena.colecao_limpa("Fachada/Paineis_Solares")
    construir_paineis(cfg, col_sol)
