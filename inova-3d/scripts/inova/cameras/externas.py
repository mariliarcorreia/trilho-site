"""Cameras de validacao (calibradas nas fotos reais) e movimentos de drone."""
import importlib.util
import json
import math
import os

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Vector

from .. import config
from ..core import cena


def _calibrador():
    caminho = os.path.join(config.RAIZ, "ferramentas", "calibrar_cameras.py")
    spec = importlib.util.spec_from_file_location("calibrar_cameras", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _nova_camera(nome, col, sensor):
    dados = bpy.data.cameras.new(nome)
    dados.sensor_fit = "HORIZONTAL"
    dados.sensor_width = sensor
    dados.clip_start = 0.5
    dados.clip_end = 4000.0
    cam = bpy.data.objects.new(nome, dados)
    col.objects.link(cam)
    return cam


def construir_validacao(cfg_cam, calib):
    col = cena.colecao_limpa("Cameras/Validacao")
    cams = {}
    for chave, c in calib["cameras"].items():
        cam = _nova_camera(f"CAM_{chave}", col, cfg_cam["sensor_mm"])
        cam.location = c["posicao"]
        cam.rotation_euler = [math.radians(a) for a in c["rotacao_euler_graus"]]
        cam.data.lens = c["lente_mm_sensor36"] * cfg_cam["sensor_mm"] / 36.0
        cams[chave] = cam
    return cams


def verificar_projecao(cams, calib, resolucao):
    """Reprojeta, pelas cameras do Blender, os pontos marcados nas fotos.

    Confirma que a convencao de camera do Blender bate com a do calibrador.
    Diferencas grandes aqui indicam erro de configuracao, nao de modelagem.
    """
    cal = _calibrador()
    with open(os.path.join(config.REFERENCIAS, "pontos_correspondencia.json"), encoding="utf-8") as fh:
        marcados = json.load(fh)["pontos"]
    pts = cal.pontos_modelo(calib["parametros"] | {"adm_y_fundo": calib["parametros"].get("adm_y_fundo", 0.0)})
    cena_atual = bpy.context.scene
    bpy.context.view_layer.update()
    W, H = resolucao
    cena_atual.render.resolution_x, cena_atual.render.resolution_y = W, H
    rel = {}
    for chave, cam in cams.items():
        erros = {}
        for nome, (u, v) in marcados[chave].items():
            q = world_to_camera_view(cena_atual, cam, Vector(pts[nome]))
            pu, pv = q.x * W, (1 - q.y) * H
            erros[nome] = round(math.hypot(pu - u, pv - v), 1)
        rel[chave] = {"medio": round(sum(erros.values()) / len(erros), 2), "max": max(erros.values()), "por_ponto": erros}
    return rel


def _chave(cam, quadro, pos, rot, lente):
    cam.location = pos
    cam.rotation_euler = [math.radians(a) for a in rot]
    cam.data.lens = lente
    cam.keyframe_insert("location", frame=quadro)
    cam.keyframe_insert("rotation_euler", frame=quadro)
    cam.data.keyframe_insert("lens", frame=quadro)


def construir_movimentos(cfg_cam, calib):
    col = cena.colecao_limpa("Cameras/Drone")
    fps = cfg_cam["fps"]
    cams = {}
    for nome, mv in cfg_cam["movimentos"].items():
        cam = _nova_camera(nome, col, cfg_cam["sensor_mm"])
        n = int(round(mv["duracao_s"] * fps))
        for k in mv["chaves"]:
            _chave(cam, 1 + round(k["t"] * (n - 1)), k["pos"], k["rot"], k["lente"])
        fim = calib["cameras"][mv["final"]]
        _chave(cam, n, fim["posicao"], fim["rotacao_euler_graus"], fim["lente_mm_sensor36"])
        cam["quadros"] = n
        cam["descricao"] = mv["descricao"]
        # suaviza entrada e saida (curvas Bezier com tangentes automaticas travadas)
        anim = [cam.animation_data, cam.data.animation_data]
        for ad in anim:
            for fc in _fcurves(ad):
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
                fc.update()
        cams[nome] = cam
    return cams


def _fcurves(animation_data):
    """F-curves de uma acao, compativel com acoes em camadas (Blender 4.4+)."""
    acao = animation_data.action if animation_data else None
    if acao is None:
        return []
    if hasattr(acao, "fcurves") and len(getattr(acao, "fcurves", [])):
        return list(acao.fcurves)
    curvas = []
    for camada in getattr(acao, "layers", []):
        for faixa in camada.strips:
            for canal in faixa.channelbags:
                curvas.extend(canal.fcurves)
    return curvas
