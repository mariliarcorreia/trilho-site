"""Configuracao do Cycles por perfil e funcoes de render (still e sequencia)."""
import os
import subprocess

import bpy


def _dispositivo(cena):
    """Usa GPU se houver (OptiX/CUDA/HIP/Metal); senao CPU."""
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for tipo in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
            try:
                prefs.compute_device_type = tipo
            except TypeError:
                continue
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type != "CPU"]
            if gpus:
                for d in prefs.devices:
                    d.use = True
                cena.cycles.device = "GPU"
                return tipo
        prefs.compute_device_type = "NONE"
    except Exception:
        pass
    cena.cycles.device = "CPU"
    return "CPU"


def aplicar(cfg_render, perfil):
    p = cfg_render["perfis"][perfil]
    cena = bpy.context.scene
    cena.render.engine = "CYCLES"
    disp = _dispositivo(cena)
    cena.render.resolution_x, cena.render.resolution_y = p["resolucao"]
    cena.render.resolution_percentage = 100
    cy = cena.cycles
    cy.samples = p["amostras"]
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02 if perfil in ("teste", "previa") else 0.01
    cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"
    except TypeError:
        pass
    cy.max_bounces = p["rebatimentos"]
    cy.diffuse_bounces = min(4, p["rebatimentos"])
    cy.glossy_bounces = min(4, p["rebatimentos"])
    cy.transmission_bounces = p["rebatimentos"]
    cy.transparent_max_bounces = 16
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.sample_clamp_indirect = 10.0
    cena.render.use_motion_blur = p["desfoque_movimento"]
    cena.render.use_persistent_data = True
    cena.render.film_transparent = False

    cor = cfg_render["cor"]
    vs = cena.view_settings
    try:
        vs.view_transform = cor["transformacao"]
        vs.look = cor["visual"]
    except TypeError:
        vs.view_transform = "Filmic" if "Filmic" in [i.identifier for i in vs.bl_rna.properties["view_transform"].enum_items] else vs.view_transform
    vs.exposure = cor["exposicao"]

    img = cena.render.image_settings
    img.file_format = p["formato"]
    if p["formato"] == "PNG":
        img.color_mode = "RGB"
        img.color_depth = "8"
    else:
        img.color_depth = "16"
    return disp


def still(camera, caminho):
    cena = bpy.context.scene
    cena.camera = camera
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    return caminho


def sequencia(camera, pasta, quadros, passo=1):
    """Renderiza quadros 1..quadros da camera animada em PNG numerado."""
    cena = bpy.context.scene
    cena.camera = camera
    cena.frame_start, cena.frame_end, cena.frame_step = 1, quadros, passo
    os.makedirs(pasta, exist_ok=True)
    cena.render.filepath = os.path.join(pasta, "q_")
    bpy.ops.render.render(animation=True)
    return pasta


def montar_video(pasta, saida_mp4, fps, passo=1):
    """Junta a sequencia PNG em MP4 H.264 (para revisao; o master sai em EXR)."""
    cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(fps / passo), "-pattern_type", "glob",
           "-i", os.path.join(pasta, "q_*.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
           "-vf", f"fps={fps}", saida_mp4]
    subprocess.run(cmd, check=True)
    return saida_mp4
