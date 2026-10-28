"""Biblioteca de materiais fisicamente plausiveis (Principled BSDF).

Os materiais sao criados por nome e reconstruidos a cada execucao (sem
duplicar). Texturas procedurais usam coordenadas de objeto, que nesta cena
equivalem a metros, pois a geometria arquitetonica e criada em coordenadas de
mundo. Cores calibradas a olho a partir das fotos reais; ajuste fino na fase
de direcao de arte.
"""
import math
import os

import bpy

from .. import config

_cache = {}


def _novo(nome):
    mat = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    if hasattr(mat, "use_nodes") and not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    saida = nt.nodes.new("ShaderNodeOutputMaterial")
    saida.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    nt.links.new(bsdf.outputs["BSDF"], saida.inputs["Surface"])
    return mat, nt, bsdf, saida


def _set(bsdf, **kw):
    nomes = {
        "cor": "Base Color", "metal": "Metallic", "rug": "Roughness", "verniz": "Coat Weight",
        "ior": "IOR", "alfa": "Alpha", "spec": "Specular IOR Level",
    }
    for k, v in kw.items():
        entrada = bsdf.inputs.get(nomes[k])
        if entrada is None:
            continue
        if k == "cor":
            entrada.default_value = (*v, 1.0)
        else:
            entrada.default_value = v


def _coord(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    return tc


def _ruido_cor(nt, bsdf, cor_a, cor_b, escala, detalhe=6.0, contraste=(0.35, 0.65), entrada=None):
    """Variacao de cor por ruido (manchas, desgaste)."""
    tc = _coord(nt)
    ru = nt.nodes.new("ShaderNodeTexNoise")
    ru.inputs["Scale"].default_value = escala
    ru.inputs["Detail"].default_value = detalhe
    nt.links.new(tc.outputs["Object"], ru.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = contraste
    nt.links.new(ru.outputs["Fac"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*cor_a, 1)
    mix.inputs["B"].default_value = (*cor_b, 1)
    nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], entrada or bsdf.inputs["Base Color"])
    return ru


def _relevo(nt, bsdf, altura_saida, forca=0.3, distancia=0.02):
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = forca
    bump.inputs["Distance"].default_value = distancia
    nt.links.new(altura_saida, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return bump


def _relevo_ruido(nt, bsdf, escala, forca=0.15):
    tc = _coord(nt)
    ru = nt.nodes.new("ShaderNodeTexNoise")
    ru.inputs["Scale"].default_value = escala
    ru.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], ru.inputs["Vector"])
    _relevo(nt, bsdf, ru.outputs["Fac"], forca)


def _nervuras(nt, bsdf, passo, eixo="XY", forca=0.6):
    """Telha/painel metalico trapezoidal: faixas periodicas no plano horizontal."""
    tc = _coord(nt)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    soma = nt.nodes.new("ShaderNodeMath")
    soma.operation = "ADD"
    if eixo == "XY":
        nt.links.new(sep.outputs["X"], soma.inputs[0])
        nt.links.new(sep.outputs["Y"], soma.inputs[1])
    else:
        nt.links.new(sep.outputs["Y"], soma.inputs[0])
        soma.inputs[1].default_value = 0.0
    # perfil trapezoidal: seno saturado
    fase = nt.nodes.new("ShaderNodeMath")
    fase.operation = "MULTIPLY"
    fase.inputs[1].default_value = 2 * math.pi / passo
    nt.links.new(soma.outputs[0], fase.inputs[0])
    seno = nt.nodes.new("ShaderNodeMath")
    seno.operation = "SINE"
    nt.links.new(fase.outputs[0], seno.inputs[0])
    sat = nt.nodes.new("ShaderNodeMapRange")
    sat.inputs["From Min"].default_value = -0.35
    sat.inputs["From Max"].default_value = 0.35
    sat.clamp = True
    nt.links.new(seno.outputs[0], sat.inputs["Value"])
    _relevo(nt, bsdf, sat.outputs["Result"], forca, 0.015)


def _grade(nt, largura, altura, argamassa, cor_celula, cor_linha, uv=False):
    """Grade regular (modulos, blocos, tela) via textura de tijolo sem deslocamento."""
    tc = _coord(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.0
    br.squash = 1.0
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = argamassa
    br.inputs["Mortar Smooth"].default_value = 0.1
    br.inputs["Brick Width"].default_value = largura
    br.inputs["Row Height"].default_value = altura
    br.inputs["Color1"].default_value = (*cor_celula, 1)
    br.inputs["Color2"].default_value = (*cor_celula, 1)
    br.inputs["Mortar"].default_value = (*cor_linha, 1)
    nt.links.new(tc.outputs["UV" if uv else "Object"], br.inputs["Vector"])
    return br


# --- construtores -------------------------------------------------------------

def _simples(nome, cor, metal=0.0, rug=0.5, verniz=0.0):
    def f():
        mat, nt, bsdf, _ = _novo(nome)
        _set(bsdf, cor=cor, metal=metal, rug=rug, verniz=verniz)
        return mat
    return f


def _metal_fachada():
    mat, nt, bsdf, _ = _novo("metal_fachada")
    _set(bsdf, metal=0.55, rug=0.42)
    _ruido_cor(nt, bsdf, (0.60, 0.62, 0.64), (0.68, 0.70, 0.72), 0.35, contraste=(0.3, 0.7))
    _nervuras(nt, bsdf, 0.25, "XY", 0.5)
    return mat


def _telhado():
    mat, nt, bsdf, _ = _novo("telhado_metalico")
    _set(bsdf, metal=0.35, rug=0.6)
    _ruido_cor(nt, bsdf, (0.52, 0.49, 0.44), (0.62, 0.59, 0.53), 0.12)
    _nervuras(nt, bsdf, 0.33, "X", 0.4)
    return mat


def _alvenaria():
    mat, nt, bsdf, _ = _novo("alvenaria_branca")
    _set(bsdf, rug=0.85)
    _ruido_cor(nt, bsdf, (0.80, 0.80, 0.78), (0.88, 0.88, 0.86), 1.2, contraste=(0.4, 0.6))
    return mat


def _bloco():
    mat, nt, bsdf, _ = _novo("bloco_concreto")
    _set(bsdf, rug=0.9)
    br = _grade(nt, 0.39, 0.19, 0.012, (0.47, 0.47, 0.46), (0.40, 0.40, 0.39))
    nt.links.new(br.outputs["Color"], bsdf.inputs["Base Color"])
    _relevo(nt, bsdf, br.outputs["Fac"], 0.2)
    return mat


def _asfalto(nome, a, b, escala):
    def f():
        mat, nt, bsdf, _ = _novo(nome)
        _set(bsdf, rug=0.92)
        _ruido_cor(nt, bsdf, a, b, escala, contraste=(0.3, 0.75))
        _relevo_ruido(nt, bsdf, 60.0, 0.12)
        return mat
    return f


def _painel_solar():
    mat, nt, bsdf, _ = _novo("painel_solar")
    _set(bsdf, metal=0.15, rug=0.12, verniz=0.6)
    br = _grade(nt, 1.13, 2.28, 0.03, (0.035, 0.05, 0.085), (0.55, 0.57, 0.6))
    nt.links.new(br.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def _tela_gradil():
    """Tela soldada: arames escuros, vaos transparentes."""
    mat, nt, bsdf, saida = _novo("tela_gradil")
    _set(bsdf, cor=(0.07, 0.075, 0.08), metal=0.6, rug=0.5)
    br = _grade(nt, 0.065, 0.2, 0.006, (0, 0, 0), (1, 1, 1), uv=True)
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(br.outputs["Fac"], mix.inputs["Fac"])
    nt.links.new(transp.outputs[0], mix.inputs[1])
    nt.links.new(bsdf.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], saida.inputs["Surface"])
    return mat


def _imagem_alfa(nome, arquivo, metal=0.0, rug=0.45, cor_fixa=None):
    """Decalque com transparencia a partir de PNG (logomarca oficial)."""
    def f():
        mat, nt, bsdf, saida = _novo(nome)
        _set(bsdf, metal=metal, rug=rug)
        caminho = config.textura(arquivo)
        img = bpy.data.images.get(os.path.basename(caminho))
        if img is None:
            img = bpy.data.images.load(caminho)
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.interpolation = "Cubic"
        tex.extension = "CLIP"
        if cor_fixa is None:
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            _set(bsdf, cor=cor_fixa)
        transp = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
        nt.links.new(transp.outputs[0], mix.inputs[1])
        nt.links.new(bsdf.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], saida.inputs["Surface"])
        return mat
    return f


def _vidro_escuro():
    """Vidro fume: transmissivo (deixa ver o interior escuro) e reflexivo."""
    mat, nt, bsdf, _ = _novo("vidro_escuro")
    _set(bsdf, cor=(0.30, 0.33, 0.35), metal=0.0, rug=0.02, ior=1.52, spec=1.0)
    trans = bsdf.inputs.get("Transmission Weight")
    if trans is not None:
        trans.default_value = 1.0
    return mat


def _vegetacao():
    mat, nt, bsdf, _ = _novo("vegetacao")
    _set(bsdf, rug=0.7)
    _ruido_cor(nt, bsdf, (0.08, 0.17, 0.05), (0.22, 0.30, 0.10), 4.0)
    return mat


def _grama_seca():
    mat, nt, bsdf, _ = _novo("grama_seca")
    _set(bsdf, rug=0.95)
    _ruido_cor(nt, bsdf, (0.30, 0.30, 0.15), (0.45, 0.33, 0.20), 0.25, contraste=(0.35, 0.7))
    _relevo_ruido(nt, bsdf, 25.0, 0.2)
    return mat


def _terra():
    mat, nt, bsdf, _ = _novo("terra_vermelha")
    _set(bsdf, rug=0.97)
    _ruido_cor(nt, bsdf, (0.50, 0.27, 0.16), (0.62, 0.38, 0.24), 0.18, contraste=(0.3, 0.7))
    _relevo_ruido(nt, bsdf, 8.0, 0.25)
    return mat


def _calcada():
    mat, nt, bsdf, _ = _novo("calcada")
    _set(bsdf, rug=0.95)
    _ruido_cor(nt, bsdf, (0.36, 0.21, 0.13), (0.47, 0.34, 0.26), 0.5, contraste=(0.35, 0.65))
    return mat


def _terreno_distante():
    mat, nt, bsdf, _ = _novo("terreno_distante")
    _set(bsdf, rug=1.0)
    _ruido_cor(nt, bsdf, (0.14, 0.17, 0.08), (0.36, 0.24, 0.16), 0.02, contraste=(0.35, 0.75))
    return mat


_CONSTRUTORES = {
    "metal_fachada": _metal_fachada,
    "telhado_metalico": _telhado,
    "alvenaria_branca": _alvenaria,
    "bloco_concreto": _bloco,
    "grafite_acm": _simples("grafite_acm", (0.095, 0.10, 0.105), 0.35, 0.32, 0.3),
    "cinza_acm": _simples("cinza_acm", (0.58, 0.59, 0.60), 0.45, 0.32, 0.2),
    "pintura_grafite": _simples("pintura_grafite", (0.16, 0.165, 0.17), 0.0, 0.55),
    "vidro_escuro": _vidro_escuro,
    "esquadria": _simples("esquadria", (0.16, 0.165, 0.17), 0.8, 0.35),
    "brise": _simples("brise", (0.22, 0.225, 0.23), 0.7, 0.4),
    "interior_escuro": _simples("interior_escuro", (0.02, 0.02, 0.022), 0.0, 0.9),
    "asfalto": _asfalto("asfalto", (0.095, 0.088, 0.082), (0.15, 0.135, 0.12), 0.4),
    "patio": _asfalto("patio", (0.11, 0.10, 0.095), (0.20, 0.18, 0.16), 0.25),
    "concreto": _asfalto("concreto", (0.55, 0.54, 0.52), (0.66, 0.65, 0.62), 0.6),
    "faixa_viaria": _simples("faixa_viaria", (0.82, 0.82, 0.80), 0.0, 0.6),
    "calcada": _calcada,
    "terra_vermelha": _terra,
    "grama_seca": _grama_seca,
    "terreno_distante": _terreno_distante,
    "painel_solar": _painel_solar,
    "metal_galvanizado": _simples("metal_galvanizado", (0.62, 0.63, 0.62), 1.0, 0.32),
    "gradil": _simples("gradil", (0.06, 0.065, 0.07), 0.6, 0.45),
    "tela_gradil": _tela_gradil,
    "poste_concreto": _simples("poste_concreto", (0.62, 0.61, 0.58), 0.0, 0.8),
    "vegetacao": _vegetacao,
    "logo_fachada": _imagem_alfa("logo_fachada", "logo_fachada.png", 0.0, 0.4),
    "emblema_aco": _imagem_alfa("emblema_aco", "emblema_icone.png", 1.0, 0.28, cor_fixa=(0.78, 0.79, 0.80)),
    "carro_preto": _simples("carro_preto", (0.015, 0.015, 0.017), 0.6, 0.18, 1.0),
    "carro_prata": _simples("carro_prata", (0.56, 0.57, 0.59), 0.9, 0.25, 1.0),
    "carro_branco": _simples("carro_branco", (0.86, 0.86, 0.85), 0.0, 0.2, 1.0),
    "carro_grafite": _simples("carro_grafite", (0.12, 0.125, 0.13), 0.8, 0.25, 1.0),
    "vidro_carro": _simples("vidro_carro", (0.01, 0.012, 0.015), 0.0, 0.05, 1.0),
    "pneu": _simples("pneu", (0.025, 0.025, 0.025), 0.0, 0.85),
    "roda": _simples("roda", (0.5, 0.5, 0.52), 1.0, 0.3),
    "moto_preta": _simples("moto_preta", (0.02, 0.02, 0.02), 0.3, 0.3, 0.8),
    "moto_vermelha": _simples("moto_vermelha", (0.45, 0.03, 0.03), 0.2, 0.3, 0.8),
    "moto_cinza": _simples("moto_cinza", (0.35, 0.36, 0.38), 0.6, 0.3, 0.8),
    "contexto_concreto": _simples("contexto_concreto", (0.55, 0.55, 0.53), 0.0, 0.85),
    "contexto_branco": _simples("contexto_branco", (0.80, 0.80, 0.78), 0.0, 0.85),
    "contexto_telhado": _simples("contexto_telhado", (0.50, 0.50, 0.50), 0.4, 0.5),
    "copa_arvore": _simples("copa_arvore", (0.07, 0.13, 0.05), 0.0, 0.85),
    "tronco": _simples("tronco", (0.18, 0.13, 0.09), 0.0, 0.9),
    "telha_ceramica": _simples("telha_ceramica", (0.42, 0.20, 0.12), 0.0, 0.8),
}


def obter(nome):
    """Retorna o material, construindo-o uma vez por execucao."""
    if nome not in _cache or _cache[nome].name not in bpy.data.materials:
        _cache[nome] = _CONSTRUTORES[nome]()
    return _cache[nome]


def reiniciar_cache():
    _cache.clear()


def aplicar_paleta(cores_por_material):
    """Recolore materiais ja construidos (estilos de direcao de arte).

    Materiais com variacao (no Mix RGBA) recebem duas cores; materiais lisos, uma.
    """
    for nome, cores in cores_por_material.items():
        mat = bpy.data.materials.get(nome)
        if mat is None or mat.node_tree is None:
            continue
        mixes = [n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeMix" and n.data_type == "RGBA"]
        if mixes and len(cores) >= 2:
            mixes[0].inputs["A"].default_value = (*cores[0], 1)
            mixes[0].inputs["B"].default_value = (*cores[1], 1)
        else:
            for n in mat.node_tree.nodes:
                if n.bl_idname == "ShaderNodeBsdfPrincipled" and not n.inputs["Base Color"].is_linked:
                    n.inputs["Base Color"].default_value = (*cores[0], 1)
