"""Ponto de entrada do projeto Inova Industrial 3D.

Funciona de duas formas:
  1) Blender instalado:  blender -b -P scripts/run.py -- [opcoes]
  2) Modulo bpy (pip):    python scripts/run.py [opcoes]

Exemplos:
  # so constroi a cena e salva o .blend para abrir/editar no Blender
  blender -b -P scripts/run.py -- --salvar cenas/fachada_v01.blend

  # renders de validacao (CAM_A, CAM_B, CAM_C) na resolucao das fotos
  blender -b -P scripts/run.py -- --render validacao

  # previa dos tres movimentos de drone (MP4 em saida/previas)
  blender -b -P scripts/run.py -- --render movimentos --perfil previa

Rodar de novo reconstroi a cena do zero (colecoes sob "INOVA" sao limpas antes),
entao nao ha duplicacao de objetos.
"""
import argparse
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

import bpy  # noqa: E402

from inova import config  # noqa: E402
from inova.cameras import externas  # noqa: E402
from inova.core import cena  # noqa: E402
from inova.geometria import administrativo, galpoes, terreno, veiculos  # noqa: E402
from inova.iluminacao import externa  # noqa: E402
from inova.materiais import biblioteca  # noqa: E402
from inova.render import perfis  # noqa: E402


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser(description="Inova Industrial 3D: fase 1 (fachada)")
    ap.add_argument("--render", choices=["nada", "validacao", "movimentos", "tudo"], default="nada")
    ap.add_argument("--perfil", default=None, help="teste | previa | validacao | final")
    ap.add_argument("--cameras", default="A,B,C", help="subconjunto de cameras de validacao")
    ap.add_argument("--movimentos", default=None, help="nomes dos movimentos separados por virgula (padrao: todos)")
    ap.add_argument("--passo", type=int, default=1, help="renderiza 1 a cada N quadros (previa rapida)")
    ap.add_argument("--salvar", default=None, help="caminho do .blend a salvar")
    ap.add_argument("--sem-contexto", action="store_true", help="omite volumes vizinhos")
    return ap.parse_args(argv)


def _preparar_blender():
    try:
        import addon_utils
        addon_utils.enable("cycles", default_set=True)
    except Exception:
        pass
    # cena vazia na primeira execucao (remove o cubo/luz/camera padrao)
    for nome in ("Cube", "Light", "Camera"):
        obj = bpy.data.objects.get(nome)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)


def construir_cena(sem_contexto=False):
    t0 = time.time()
    biblioteca.reiniciar_cache()
    fachada = config.carregar("fachada")
    if sem_contexto:
        fachada["contexto"]["ativo"] = False
    calib = config.carregar("calibracao")
    cfg_cam = config.carregar("cameras")
    cfg_render = config.carregar("render")

    galpoes.construir(fachada)
    administrativo.construir(fachada)
    terreno.construir(fachada)
    modelos = veiculos.construir(fachada)
    veiculos.construir_contexto(fachada, modelos)
    externa.construir(cfg_render["luz"])
    cams_val = externas.construir_validacao(cfg_cam, calib)
    cams_mov = externas.construir_movimentos(cfg_cam, calib)
    cena.purgar_orfaos()

    s = bpy.context.scene
    s.render.fps = cfg_cam["fps"]
    s.unit_settings.system = "METRIC"
    s.camera = cams_val["B"]
    n_obj = len([o for o in bpy.data.objects])
    print(f"[inova] cena construida em {time.time() - t0:.1f}s | objetos: {n_obj}")
    return fachada, calib, cfg_cam, cfg_render, cams_val, cams_mov


def main():
    a = _args()
    _preparar_blender()
    fachada, calib, cfg_cam, cfg_render, cams_val, cams_mov = construir_cena(a.sem_contexto)

    rel = externas.verificar_projecao(cams_val, calib, cfg_cam["resolucao_validacao"])
    os.makedirs(os.path.join(config.SAIDA, "validacao"), exist_ok=True)
    with open(os.path.join(config.SAIDA, "validacao", "verificacao_cameras_blender.json"), "w", encoding="utf-8") as fh:
        json.dump(rel, fh, indent=2, ensure_ascii=False)
    print("[inova] reprojecao pelas cameras do Blender (px):", {k: v["medio"] for k, v in rel.items()})

    if a.render in ("validacao", "tudo"):
        disp = perfis.aplicar(cfg_render, a.perfil or "validacao")
        print(f"[inova] render de validacao em {disp}")
        for chave in a.cameras.split(","):
            t0 = time.time()
            arq = os.path.join(config.SAIDA, "validacao", f"render_{chave}.png")
            perfis.still(cams_val[chave], arq)
            print(f"[inova] {arq} ({time.time() - t0:.0f}s)")

    if a.render in ("movimentos", "tudo"):
        perfil = a.perfil or "previa"
        disp = perfis.aplicar(cfg_render, perfil)
        nomes = a.movimentos.split(",") if a.movimentos else list(cams_mov)
        for nome in nomes:
            cam = cams_mov[nome]
            pasta = os.path.join(config.SAIDA, "previas", nome)
            t0 = time.time()
            perfis.sequencia(cam, pasta, cam["quadros"], a.passo)
            mp4 = perfis.montar_video(pasta, os.path.join(config.SAIDA, "previas", f"{nome}.mp4"), cfg_cam["fps"], a.passo)
            print(f"[inova] {mp4} ({time.time() - t0:.0f}s em {disp})")

    if a.salvar:
        caminho = os.path.join(config.RAIZ, a.salvar) if not os.path.isabs(a.salvar) else a.salvar
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        bpy.context.scene.camera = cams_val["B"]
        bpy.ops.wm.save_as_mainfile(filepath=caminho, compress=True)
        print(f"[inova] cena salva em {caminho}")


if __name__ == "__main__":
    main()
