"""Animacao 2.5D das cenas em estilo Pixar (imagens geradas sem logomarca).

Pipeline por cena:
  1. aplica a logomarca OFICIAL (texturas/) nos pontos definidos no rig, com o
     sombreamento da imagem original, para parecer impressa no material;
  2. recorta o personagem (rembg) e reconstroi o fundo atras dele (inpaint);
  3. anima o personagem por deformacao suave (respiracao, cabeca, fala, braco)
     e piscadas;
  4. move a camera com paralaxe entre fundo e personagem, adiciona particulas
     de poeira na luz e a legenda do roteiro;
  5. gera MP4 1920x1080 24 fps.

Uso:
    python scripts/animacao_2d.py cenas_pixar/rig/c03.json
"""
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W_SAIDA, H_SAIDA, FPS = 1920, 1080, 24


# --- logomarca ----------------------------------------------------------------

def _logo(variante):
    arq = {"completa": "logo_fachada.png", "icone": "emblema_icone.png"}[variante]
    im = Image.open(os.path.join(RAIZ, "texturas", arq)).convert("RGBA")
    if variante == "icone":
        # mesmo icone da variante de fachada: partes brancas em grafite (regra 4)
        a = np.asarray(im).astype(np.float32)
        sat = a[..., :3].max(-1) - a[..., :3].min(-1)
        branco = (sat < 40) & (a[..., 3] > 0)
        a[branco, :3] = (43, 43, 46)
        im = Image.fromarray(a.astype(np.uint8))
    bbox = im.getbbox()
    return im.crop(bbox)


def aplicar_logos(img, logos):
    """img: float32 RGB 0..1. Cada logo: variante, centro [x,y], largura, rotacao."""
    base = img.copy()
    lum = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), (0, 0), 6)
    for lg in logos:
        im = _logo(lg["variante"])
        w = int(lg["largura"])
        h = int(round(im.height * w / im.width))
        im = im.resize((w, h), Image.LANCZOS)
        if lg.get("rotacao"):
            im = im.rotate(lg["rotacao"], resample=Image.BICUBIC, expand=True)
        a = np.asarray(im).astype(np.float32) / 255.0
        cx, cy = lg["centro"]
        x0, y0 = int(cx - a.shape[1] / 2), int(cy - a.shape[0] / 2)
        x1, y1 = x0 + a.shape[1], y0 + a.shape[0]
        reg = base[y0:y1, x0:x1]
        # sombreamento: a luz da superficie original modula a cor da logo
        l = lum[y0:y1, x0:x1]
        ref = np.percentile(lum[max(0, y0 - 20):y1 + 20, max(0, x0 - 20):x1 + 20], 80)
        sombra = np.clip(l / max(ref, 1e-3), 0.55, 1.15)[..., None]
        cor = a[..., :3] * sombra * lg.get("intensidade", 0.95)
        alfa = a[..., 3:4] * lg.get("opacidade", 0.97)
        reg[:] = reg * (1 - alfa) + cor * alfa
    return base


# --- recorte e fundo ---------------------------------------------------------

def recortar(caminho_img, cache):
    if os.path.exists(cache):
        return np.asarray(Image.open(cache)).astype(np.float32)[..., 3] / 255.0
    from rembg import new_session, remove
    out = remove(Image.open(caminho_img), session=new_session("isnet-general-use"))
    out.save(cache)
    return np.asarray(out).astype(np.float32)[..., 3] / 255.0


def fundo_sem_personagem(img, alfa):
    m = (alfa > 0.05).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((31, 31), np.uint8))
    peq = cv2.resize((img * 255).astype(np.uint8), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    mpeq = cv2.resize(m, (peq.shape[1], peq.shape[0]), interpolation=cv2.INTER_NEAREST)
    rec = cv2.inpaint(peq, mpeq, 21, cv2.INPAINT_TELEA)
    rec = cv2.resize(rec, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
    rec = cv2.GaussianBlur(rec, (0, 0), 7)
    mf = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 9)[..., None]
    return img * (1 - mf) + rec * mf


# --- curvas de animacao -------------------------------------------------------

def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def fala(t, inicio, fim):
    """Envelope de fala (0..1) com silabas a ~4-6 Hz."""
    if t < inicio or t > fim:
        return 0.0
    env = min(1.0, (t - inicio) / 0.2, (fim - t) / 0.2)
    v = 0.55 + 0.45 * math.sin(2 * math.pi * 4.7 * t) * math.sin(2 * math.pi * 1.3 * t + 0.7)
    v += 0.25 * math.sin(2 * math.pi * 6.1 * t + 1.9)
    return max(0.0, min(1.0, v)) * env


def piscada(t, tempos, dur=0.2):
    for tp in tempos:
        if tp <= t <= tp + dur:
            u = (t - tp) / dur
            return 1 - abs(2 * u - 1)  # fecha e abre
    return 0.0


# --- deformacao ---------------------------------------------------------------

def _peso_regiao(X, Y, r):
    """Peso suave: retangulo (x0,y0,x1,y1) com borda de transicao 'borda'."""
    x0, y0, x1, y1 = r["caixa"]
    b = r.get("borda", 40)
    wx = suave((X - (x0 - b)) / b) * suave(((x1 + b) - X) / b)
    wy = suave((Y - (y0 - b)) / b) * suave(((y1 + b) - Y) / b)
    return wx * wy


def campo_deformacao(X, Y, rig, t, pesos):
    dx = np.zeros_like(X)
    dy = np.zeros_like(Y)
    # respiracao: estica o tronco para cima a partir da cintura
    r = rig["respiracao"]
    s = r["amplitude"] * math.sin(2 * math.pi * t / r["periodo"])
    acima = np.clip((r["cintura_y"] - Y) / r["cintura_y"], 0, 1)
    dy += -(r["cintura_y"] - Y) * s * acima
    # cabeca: rotacao em torno do pescoco + aceno durante a fala
    c = rig["cabeca"]
    ang = math.radians(c["giro_graus"] * math.sin(2 * math.pi * t / c["periodo"])
                      + 0.4 * c["giro_graus"] * math.sin(2 * math.pi * t / (c["periodo"] * 0.43) + 1.1))
    px, py = c["pivo"]
    f = fala(t, *rig["fala"]["intervalo"])
    aceno = c.get("aceno_px", 0) * f
    w = pesos["cabeca"]
    rx = (X - px) * math.cos(ang) - (Y - py) * math.sin(ang) + px
    ry = (X - px) * math.sin(ang) + (Y - py) * math.cos(ang) + py
    dx += (rx - X) * w
    dy += ((ry - Y) + aceno) * w
    # mandibula: abre a boca acompanhando a fala
    m = rig["boca"]
    dy += m["abertura_px"] * f * pesos["boca"]
    # braco: aceno da mao em torno do ombro
    b = rig["braco"]
    ang = math.radians(b["giro_graus"] * math.sin(2 * math.pi * t / b["periodo"]))
    px, py = b["pivo"]
    rx = (X - px) * math.cos(ang) - (Y - py) * math.sin(ang) + px
    ry = (X - px) * math.sin(ang) + (Y - py) * math.cos(ang) + py
    dx += (rx - X) * pesos["braco"]
    dy += (ry - Y) * pesos["braco"]
    return dx, dy


def desenhar_palpebras(img, olhos, fechamento):
    """Piscada por remapeamento: a pele acima do olho desce e o olho se comprime.

    Usa a propria textura e luz da imagem (nada de cor chapada).
    """
    if fechamento <= 0.01:
        return img
    out = img.copy()
    f = min(fechamento, 0.94)
    for o in olhos:
        cx, cy, rx, ry = o["elipse"]
        x0, x1 = int(cx - rx - 8), int(cx + rx + 8)
        y0, y1 = int(cy - ry - 30), int(cy + ry + 6)
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        nx = np.clip((xx - cx) / rx, -1, 1)
        meia = ry * np.sqrt(np.clip(1 - nx * nx, 0, 1))  # meia altura do olho em cada coluna
        topo = cy - meia
        base = cy + meia
        borda = topo + (base - topo) * f  # onde esta a palpebra agora
        sy = yy.copy()
        # acima da borda (palpebra): pele limpa da bochecha logo abaixo do olho
        acima = (yy >= topo - 1) & (yy < borda)
        frac = np.where(borda - topo > 1e-3, (yy - topo) / np.maximum(borda - topo, 1e-3), 0)
        sy = np.where(acima, cy + ry + o.get("pele_dy", 12) + frac * 16, sy)
        # abaixo da borda: o olho inteiro comprimido no espaco que sobra
        abaixo = (yy >= borda) & (yy <= base)
        frac2 = np.where(base - borda > 1e-3, (yy - borda) / np.maximum(base - borda, 1e-3), 1)
        sy = np.where(abaixo, topo + frac2 * (base - topo), sy)
        mapx = xx.astype(np.float32)
        mapy = sy.astype(np.float32)
        reg = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        # palpebra levemente mais escura no alto (volume arredondado)
        vol = np.where(acima, 0.9 + 0.1 * frac, 1.0)[..., None]
        reg = reg * vol
        liso = cv2.GaussianBlur(reg, (0, 0), 2.2)
        reg = np.where(acima[..., None], liso, reg)
        # mascara suave so dentro do contorno do olho
        dentro = np.clip((meia + 2 - np.abs(yy - cy)) / 2.5, 0, 1) * np.clip((1 - np.abs((xx - cx) / (rx + 2))) * 6, 0, 1)
        # cilios na borda
        cil = np.exp(-((yy - borda) / 1.4) ** 2) * dentro * min(1.0, f * 1.5)
        reg = reg * (1 - 0.75 * cil[..., None]) + np.array([0.07, 0.045, 0.035]) * 0.75 * cil[..., None]
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - dentro[..., None]) + reg * dentro[..., None]
    return out


# --- camera, particulas, legenda ---------------------------------------------

def transformar(img, zoom, centro, tamanho):
    h, w = tamanho
    cx, cy = centro
    M = np.array([[zoom, 0, w / 2 - zoom * cx], [0, zoom, h / 2 - zoom * cy]], np.float32)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


class Particulas:
    def __init__(self, n, w, h, semente=4):
        rng = np.random.default_rng(semente)
        self.p = rng.uniform([0, 0], [w, h], (n, 2))
        self.v = rng.uniform([-6, -14], [10, -3], (n, 2))
        self.r = rng.uniform(1.2, 3.8, n)
        self.a = rng.uniform(0.15, 0.5, n)
        self.fase = rng.uniform(0, 6.28, n)
        self.w, self.h = w, h

    def desenhar(self, img, t):
        cam = np.zeros(img.shape[:2], np.float32)
        pos = self.p + self.v * t
        pos[:, 0] += 6 * np.sin(t * 0.7 + self.fase)
        pos[:, 0] %= self.w
        pos[:, 1] %= self.h
        for (x, y), r, a, f in zip(pos, self.r, self.a, self.fase):
            brilho = a * (0.6 + 0.4 * math.sin(t * 2.1 + f))
            cv2.circle(cam, (int(x), int(y)), int(math.ceil(r)), float(brilho), -1, lineType=cv2.LINE_AA)
        cam = cv2.GaussianBlur(cam, (0, 0), 1.4)[..., None]
        quente = np.array([1.0, 0.86, 0.62], np.float32)
        return img * (1 - cam) + quente * cam


def _fonte(tam):
    for nome in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nome, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def legenda(frame_u8, texto, alfa):
    if not texto or alfa <= 0:
        return frame_u8
    im = Image.fromarray(frame_u8).convert("RGBA")
    cam = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    fonte = _fonte(40)
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=fonte) > im.width * 0.78:
            linhas.append(atual)
            atual = p
        else:
            atual = teste
    linhas.append(atual)
    alt_l = 52
    y = im.height - 70 - alt_l * len(linhas)
    for i, l in enumerate(linhas):
        tw = d.textlength(l, font=fonte)
        x = (im.width - tw) / 2
        yy = y + i * alt_l
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2)):
            d.text((x + ox, yy + oy), l, font=fonte, fill=(0, 0, 0, int(200 * alfa)))
        d.text((x, yy), l, font=fonte, fill=(255, 255, 255, int(255 * alfa)))
    return np.asarray(Image.alpha_composite(im, cam).convert("RGB"))


# --- cena ---------------------------------------------------------------------

def animar(cfg_path):
    with open(cfg_path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    img = np.asarray(Image.open(os.path.join(RAIZ, cfg["imagem"])).convert("RGB")).astype(np.float32) / 255
    H, W = img.shape[:2]
    img = aplicar_logos(img, cfg.get("logos", []))
    pasta_tmp = os.path.join(RAIZ, "saida", "animacao", cfg["nome"])
    os.makedirs(pasta_tmp, exist_ok=True)
    Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(pasta_tmp, "com_logo.png"))
    alfa = recortar(os.path.join(pasta_tmp, "com_logo.png"), os.path.join(pasta_tmp, "recorte.png"))
    fundo = fundo_sem_personagem(img, alfa)

    rig = cfg["rig"]
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    pesos = {k: _peso_regiao(X, Y, rig[k]["regiao"]) for k in ("cabeca", "braco")}
    bm = rig["boca"]
    mx, my, sx, sy = bm["centro"][0], bm["centro"][1], bm["raio"][0], bm["raio"][1]
    gauss = np.exp(-(((X - mx) / sx) ** 2 + ((Y - my) / sy) ** 2))
    abaixo = suave((Y - bm["linha_labio_y"]) / 10.0)
    pesos["boca"] = gauss * abaixo
    pesos["braco"] *= alfa  # o braco so deforma o proprio personagem

    dur = cfg["duracao_s"]
    n = int(round(dur * FPS))
    cam = cfg["camera"]
    part = Particulas(cfg.get("particulas", 70), W, H)
    rgba = np.dstack([img, alfa])
    quadros = os.path.join(pasta_tmp, "quadros")
    os.makedirs(quadros, exist_ok=True)
    for i in range(n):
        t = i / FPS
        u = suave(t / dur)
        # personagem deformado (mapa inverso aproximado)
        dx, dy = campo_deformacao(X, Y, rig, t, pesos)
        fonte_pers = rgba.copy()
        fonte_pers[..., :3] = desenhar_palpebras(img, rig["olhos"], piscada(t, rig["piscadas_s"]))
        pers = cv2.remap(fonte_pers, X - dx, Y - dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        # camera com paralaxe
        c0, c1 = np.array(cam["centro_inicio"]), np.array(cam["centro_fim"])
        centro = c0 + (c1 - c0) * u
        z_p = cam["zoom_inicio"] + (cam["zoom_fim"] - cam["zoom_inicio"]) * u
        z_f = 1 + (z_p - 1) * cam.get("paralaxe_fundo", 0.55)
        f_bg = transformar(fundo, z_f * 1.02, centro, (H, W))
        f_bg = part.desenhar(f_bg, t)
        f_ps = transformar(pers, z_p * 1.02, centro, (H, W))
        a = f_ps[..., 3:4]
        quadro = f_bg * (1 - a) + f_ps[..., :3] * a
        quadro = cv2.resize(np.clip(quadro, 0, 1), (W_SAIDA, H_SAIDA), interpolation=cv2.INTER_CUBIC)
        q8 = (quadro * 255).astype(np.uint8)
        leg = cfg.get("legenda", {})
        if leg:
            al = min(1.0, max(0.0, (t - leg["inicio"]) / 0.3), max(0.0, (leg["fim"] - t) / 0.3))
            q8 = legenda(q8, leg["texto"], al)
        Image.fromarray(q8).save(os.path.join(quadros, f"q_{i:04d}.png"))
    saida = os.path.join(RAIZ, "saida", "animacao", f"{cfg['nome']}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", os.path.join(quadros, "q_%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", saida], check=True)
    print("ok", saida)
    return saida


if __name__ == "__main__":
    animar(sys.argv[1])
