"""Filme narrado v3: so cortes, nenhum clipe acelerado ou desacelerado.

O apresentador aparece apenas enquanto a boca dele mexe no clipe (medido quadro
a quadro). Quando a frase continua depois disso, a narracao segue sobre cenas de
apoio (planos abertos ou fechados de outros clipes). A legenda aparece so enquanto
a voz fala.

Uso: python scripts/montar_v3.py
Saida: saida/filme_narrado_v3.mp4 e saida/filme_narrado_v3_leve.mp4
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar_com_narracao as base  # noqa: E402

RAIZ = base.RAIZ
base.NARR = os.path.join(RAIZ, "audio", "narracao_ia_v2")
FPS = base.FPS
INTRO = 3.0
PAUSA = 0.7
FINAL = 0.6
LOGO = 4.0
DUR_CLIPE = 5.1

C = "clipes_ia/{}_v1.mov".format
# plano fechado: (centro x, centro y, tamanho), em fracao do quadro
FECHADO = {
    "c09_qualidade": (0.35, 0.55, 0.65),
    "c04_soldador": (0.55, 0.55, 0.70),
    "c08_projeto": (0.32, 0.58, 0.62),
    "c05_frigorifico": (0.60, 0.50, 0.70),
    "c17_faixa_seguranca": (0.38, 0.44, 0.75),
    "c11_boas_vindas": (0.58, 0.50, 0.85),
}

# Por paragrafo: planos (inicio no paragrafo, clipe, inicio no clipe, fechado?).
# Cada plano vai ate o inicio do seguinte. Legendas: (inicio, fim, texto), tempos da voz.
PARAGRAFOS = [
    {"planos": [(0.0, "saida/previas/MOV_C_travelling_avenida.mp4", 3.0, False),
                (2.0, C("c03_apresentador"), 0.0, False),
                (7.1, C("c04_soldador"), 0.0, False),
                (12.2, C("c05_frigorifico"), 0.0, False)],
     "legendas": [(0.0, 1.70, "Bem-vindo à Inova Industrial."),
                  (2.18, 8.31, "Mais do que fabricar equipamentos, nós damos vida a projetos e transformamos desafios em soluções de alta performance."),
                  (8.88, 12.98, "Cada peça que sai da nossa fábrica carrega o nosso nome e a nossa determinação"),
                  (12.98, 15.43, "em ser o melhor suporte para a indústria frigorífica.")]},
    {"planos": [(0.0, "saida/previas/MOV_B_aproximacao_frontal.mp4", 0.0, False),
                (5.85, C("c07_dedo_levantado"), 0.0, False),
                (9.3, C("c08_projeto"), 0.0, False),
                (14.3, C("c09_qualidade"), 0.0, False),
                (19.4, C("c09_qualidade"), 1.5, True),
                (22.9, C("c10_apresentador_joinha"), 0.0, False)],
     "legendas": [(0.0, 5.70, "Nascemos em 2015, mas nossa base foi construída com mais de duas décadas de experiência"),
                  (6.0, 9.22, "e um propósito inegociável: a excelência."),
                  (9.33, 14.1, "Ser a parceira mais ágil e assertiva do mercado exige mais do que tecnologia;"),
                  (14.1, 17.93, "exige olhar para cada detalhe com a responsabilidade de quem sabe"),
                  (18.07, 22.28, "que a nossa qualidade é o que garante o sucesso do nosso cliente."),
                  (22.99, 25.25, "Na Inova, o padrão “bom” não basta."),
                  (25.46, 27.13, "Nós entregamos o impecável.")]},
    {"planos": [(0.0, C("c11_boas_vindas"), 0.0, False),
                (3.7, C("c12_harmonia"), 0.0, False),
                (8.5, C("c14_apontando"), 0.2, False),
                (10.75, C("c04_soldador"), 2.0, True),
                (13.0, C("c08_projeto"), 0.45, True)],
     "legendas": [(0.0, 3.34, "Você entra hoje para um time que valoriza o ser humano acima de tudo."),
                  (3.80, 8.16, "Acreditamos que grandes resultados são frutos de um ambiente de respeito e harmonia."),
                  (8.57, 10.47, "Você é o protagonista desta engrenagem."),
                  (10.87, 16.69, "Sua dedicação e o seu capricho são os elementos que mantêm a Inova como referência de confiança e inovação.")]},
    {"planos": [(0.0, C("c15_seguranca"), 0.85, False),
                (2.0, C("c07_dedo_levantado"), 3.3, False),
                (3.8, C("c17_faixa_seguranca"), 0.0, False),
                (7.5, C("c16_epis"), 0.0, False),
                (12.6, C("c05_frigorifico"), 0.3, True),
                (16.9, C("c17_faixa_seguranca"), 2.95, True),
                (19.05, C("c18_cuidado"), 0.0, False)],
     "legendas": [(0.12, 2.74, "Mas lembre-se: para alcançarmos a excelência externa,"),
                  (3.0, 4.53, "precisamos de cuidado interno."),
                  (4.93, 6.84, "Sua segurança é o nosso maior valor."),
                  (7.60, 10.97, "O uso de EPIs, como protetor auricular, óculos e botinas,"),
                  (11.21, 14.64, "e o respeito rigoroso aos procedimentos não são apenas regras;"),
                  (15.0, 18.57, "são o compromisso que você assume consigo mesmo e com seus colegas."),
                  (19.05, 22.60, "Na Inova, cuidamos uns dos outros para que todos cresçam juntos.")]},
    {"planos": [(0.0, C("c19_mao_no_peito"), 0.05, False),
                (3.65, C("c20_caminhada"), 0.0, False),
                (8.75, C("c11_boas_vindas"), 1.2, True)],
     "legendas": [(0.0, 1.68, "Estamos felizes em ter você aqui."),
                  (2.35, 6.04, "Mais do que um colaborador, você é o novo embaixador da nossa qualidade."),
                  (6.76, 11.64, "Prepare-se para uma jornada onde seu esforço será valorizado e sua evolução será constante.")]},
    {"planos": [(0.0, "saida/previas/MOV_A_orbita_descendente.mp4", 0.3, False)],
     "legendas": [(0.0, 5.96, "Inova Industrial: mais do que produzir equipamentos, um compromisso com a excelência, com o cliente e com o seu futuro.")]},
]


def cortar(arq, ini, dur, fechado, saida):
    """Trecho em velocidade normal: so corte, escala e (opcional) plano fechado."""
    caminho = os.path.join(RAIZ, arq)
    limite = base.duracao(caminho)
    if ini + dur > limite + 0.01:
        raise SystemExit(f"{arq}: pede {ini:.2f}+{dur:.2f}s, o clipe tem {limite:.2f}s")
    f = []
    if arq.startswith("clipes_ia/"):
        f += ["crop=iw-16:ih-16:8:8", "delogo=x=42:y=32:w=72:h=70"]
    if fechado:
        cx, cy, s = FECHADO[os.path.basename(arq).replace("_v1.mov", "")]
        f.append(f"crop=iw*{s}:ih*{s}:iw*{cx - s / 2:.4f}:ih*{cy - s / 2:.4f}")
    f += ["scale=1920:1080:flags=lanczos", "setsar=1", f"fps={FPS}"]
    base.rodar(["ffmpeg", "-y", "-v", "error", "-ss", f"{ini:.3f}", "-i", caminho, "-t", f"{dur:.3f}", "-an",
                "-vf", ",".join(f), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", saida])
    return saida


def main():
    tmp = tempfile.mkdtemp(prefix="narrado_v3_", dir=os.path.join(RAIZ, "saida"))
    trechos = [("saida/previas/MOV_C_travelling_avenida.mp4", 0.0, INTRO, False)]
    legendas, audios, mapa = [], [], []
    t = INTRO
    for i, p in enumerate(PARAGRAFOS, 1):
        wav, d, _ = base.preparar_paragrafo(i, tmp)
        audios.append((wav, t))
        fim_par = d + (PAUSA if i < len(PARAGRAFOS) else FINAL)
        planos = p["planos"]
        for k, (ini, arq, ini_fonte, fechado) in enumerate(planos):
            fim = planos[k + 1][0] if k + 1 < len(planos) else fim_par
            trechos.append((arq, ini_fonte, fim - ini, fechado))
            mapa.append({"paragrafo": i, "inicio": round(t + ini, 2), "duracao": round(fim - ini, 2),
                         "clipe": os.path.basename(arq), "inicio_no_clipe": ini_fonte, "fechado": fechado})
        legendas += [(t + a, t + min(b, d), texto) for a, b, texto in p["legendas"]]
        t += fim_par
    total = t + LOGO

    arquivos = [cortar(a, ini, dur, fch, os.path.join(tmp, f"t{n:02d}.mp4"))
                for n, (a, ini, dur, fch) in enumerate(trechos)]
    arquivos.append(base.cartela_logo(tmp))
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as fh:
        fh.writelines(f"file '{a}'\n" for a in arquivos)

    ass = os.path.join(tmp, "legendas.ass")
    with open(ass, "w", encoding="utf-8") as fh:
        fh.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\n"
                 "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Alignment, "
                 "MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow\n"
                 "Style: L,DejaVu Sans,46,&H00FFFFFF,&H00000000,&H80000000,1,2,200,200,70,1,3,1\n\n"
                 "[Events]\nFormat: Layer, Start, End, Style, Text\n")
        for a, b, texto in legendas:
            fh.write(f"Dialogue: 0,{base.tc(a)},{base.tc(b + 0.15)},L,{{\\fad(120,150)}}{texto}\n")

    entradas, atrasos = [], []
    for k, (wav, ini) in enumerate(audios):
        entradas += ["-i", wav]
        ms = int(ini * 1000)
        atrasos.append(f"[{k + 1}:a]adelay={ms}|{ms}[a{k}]")
    mix = ";".join(atrasos) + ";" + "".join(f"[a{k}]" for k in range(len(audios))) + \
        f"amix=inputs={len(audios)}:normalize=0,apad,atrim=0:{total:.3f}[aout]"
    saida = os.path.join(RAIZ, "saida", "filme_narrado_v3.mp4")
    base.rodar(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, *entradas,
                "-filter_complex", f"[0:v]settb=AVTB,setpts=N/{FPS}/TB,fps={FPS},ass={ass},"
                                   f"fade=in:st=0:d=0.5,fade=out:st={total - 0.6:.2f}:d=0.6[v];{mix}",
                "-map", "[v]", "-map", "[aout]", "-t", f"{total:.3f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", saida])
    leve = saida.replace(".mp4", "_leve.mp4")
    base.rodar(["ffmpeg", "-y", "-v", "error", "-i", saida, "-vf", "scale=1280:-2", "-c:v", "libx264",
                "-crf", "25", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", leve])
    with open(saida.replace(".mp4", "_mapa.json"), "w") as fh:
        json.dump(mapa, fh, ensure_ascii=False, indent=1)
    print(f"ok {saida} ({total:.1f} s)")


if __name__ == "__main__":
    main()
