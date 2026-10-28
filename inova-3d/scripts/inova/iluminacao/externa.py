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
