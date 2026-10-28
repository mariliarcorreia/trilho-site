"""Luz diurna: ceu fisico + sol direcional, coerentes com as fotos de drone.

As fotos foram feitas perto do meio-dia (sombras curtas sob carros e motos,
sombra da pessoa levemente para a esquerda). Por isso o sol fica alto e vindo
da direita, um pouco a frente da fachada. Elevacao e azimute ficam em
config/render.json para ajuste.
"""
import math

import bpy
from mathutils import Vector

from ..core import cena


def _no_ceu(nt, elev, azim):
    ceu = nt.nodes.new("ShaderNodeTexSky")
    for tipo in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING", "HOSEK_WILKIE"):
        try:
            ceu.sky_type = tipo
            break
        except TypeError:
            continue
    if hasattr(ceu, "sun_disc"):
        ceu.sun_disc = False
    if hasattr(ceu, "sun_elevation"):
        ceu.sun_elevation = math.radians(elev)
        ceu.sun_rotation = math.radians(90 - azim)
    if hasattr(ceu, "altitude"):
        ceu.altitude = 800.0
    for prop, val in (("air_density", 1.0), ("aerosol_density", 2.0), ("dust_density", 2.0), ("ozone_density", 1.0)):
        if hasattr(ceu, prop):
            setattr(ceu, prop, val)
    return ceu


def _ceu_estilizado(nt, luz, fundo_luz, saida):
    """Ceu de animacao: gradiente azul saturado com nuvens procedurais.

    A camera ve o gradiente com intensidade plena; a iluminacao da cena usa
    'ceu_intensidade', para o ceu nao lavar as cores.
    """
    zen, hor = luz["ceu_gradiente"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Generated"], sep.inputs["Vector"])
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.color_ramp.elements[0].position = 0.0
    rampa.color_ramp.elements[0].color = (*hor, 1)
    rampa.color_ramp.elements[1].position = 0.3
    rampa.color_ramp.elements[1].color = (*zen, 1)
    nt.links.new(sep.outputs["Z"], rampa.inputs["Fac"])
    cor = rampa.outputs["Color"]
    if luz.get("nuvens"):
        ruido = nt.nodes.new("ShaderNodeTexNoise")
        ruido.inputs["Scale"].default_value = 3.5
        ruido.inputs["Detail"].default_value = 6.0
        ruido.inputs["Roughness"].default_value = 0.55
        esc = nt.nodes.new("ShaderNodeMapping")
        esc.inputs["Scale"].default_value = (1.0, 1.0, 3.5)
        nt.links.new(coord.outputs["Generated"], esc.inputs["Vector"])
        nt.links.new(esc.outputs["Vector"], ruido.inputs["Vector"])
        mascara = nt.nodes.new("ShaderNodeMapRange")
        mascara.inputs["From Min"].default_value = 0.58
        mascara.inputs["From Max"].default_value = 0.72
        nt.links.new(ruido.outputs["Fac"], mascara.inputs["Value"])
        # nuvens so acima do horizonte e mais densas perto dele
        alt = nt.nodes.new("ShaderNodeMapRange")
        alt.inputs["From Min"].default_value = 0.0
        alt.inputs["From Max"].default_value = 0.08
        nt.links.new(sep.outputs["Z"], alt.inputs["Value"])
        mult = nt.nodes.new("ShaderNodeMath")
        mult.operation = "MULTIPLY"
        nt.links.new(mascara.outputs["Result"], mult.inputs[0])
        nt.links.new(alt.outputs["Result"], mult.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["B"].default_value = (1.0, 0.98, 0.95, 1)
        nt.links.new(mult.outputs[0], mix.inputs["Factor"])
        nt.links.new(cor, mix.inputs["A"])
        cor = mix.outputs["Result"]
    visto = nt.nodes.new("ShaderNodeBackground")
    visto.inputs["Strength"].default_value = luz.get("ceu_brilho_camera", 1.0)
    nt.links.new(cor, visto.inputs["Color"])
    nt.links.new(cor, fundo_luz.inputs["Color"])
    caminho = nt.nodes.new("ShaderNodeLightPath")
    mix_s = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(caminho.outputs["Is Camera Ray"], mix_s.inputs["Fac"])
    nt.links.new(fundo_luz.outputs["Background"], mix_s.inputs[1])
    nt.links.new(visto.outputs["Background"], mix_s.inputs[2])
    nt.links.new(mix_s.outputs[0], saida.inputs["Surface"])


def construir(luz):
    elev, azim = luz["sol_elevacao_graus"], luz["sol_azimute_graus"]
    mundo = bpy.data.worlds.get("Inova_Ceu") or bpy.data.worlds.new("Inova_Ceu")
    bpy.context.scene.world = mundo
    if hasattr(mundo, "use_nodes") and not mundo.use_nodes:
        mundo.use_nodes = True
    nt = mundo.node_tree
    nt.nodes.clear()
    saida = nt.nodes.new("ShaderNodeOutputWorld")
    fundo = nt.nodes.new("ShaderNodeBackground")
    fundo.inputs["Strength"].default_value = luz["ceu_intensidade"]
    if "ceu_gradiente" in luz:
        _ceu_estilizado(nt, luz, fundo, saida)
    else:
        nt.links.new(_no_ceu(nt, elev, azim).outputs["Color"], fundo.inputs["Color"])
        nt.links.new(fundo.outputs["Background"], saida.inputs["Surface"])

    col = cena.colecao_limpa("Iluminacao")
    dados = bpy.data.lights.new("Sol", "SUN")
    dados.energy = luz["sol_intensidade"]
    dados.angle = math.radians(0.53)
    dados.color = luz["sol_cor"]
    sol = bpy.data.objects.new("Sol", dados)
    col.objects.link(sol)
    # direcao para o sol: azimute medido a partir de +X, no sentido anti-horario
    para_sol = Vector((math.cos(math.radians(elev)) * math.cos(math.radians(azim)),
                       math.cos(math.radians(elev)) * math.sin(math.radians(azim)),
                       math.sin(math.radians(elev))))
    sol.rotation_euler = Vector((0, 0, 1)).rotation_difference(para_sol).to_euler()
    sol.location = para_sol * 100
    return sol
