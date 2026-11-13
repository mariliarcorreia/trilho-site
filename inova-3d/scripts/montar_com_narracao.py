"""Monta o filme encaixando cada cena no tempo da narracao.

1. Normaliza o volume de cada paragrafo (audio/narracao_ia/p1..p6) e corta o
   silencio das pontas.
2. Detecta as pausas da fala e divide cada paragrafo nos trechos do roteiro;
   cada corte de cena cai na pausa mais proxima da divisao proporcional por
   palavras.
3. Ajusta cada clipe a duracao do seu trecho: ate 1,25x mais lento (de 30 para
   24 qps, sem quadro repetido); acima disso, ida e volta (boomerang).
4. Junta tudo com corte seco, a narracao e a legenda sincronizada.

Uso: python scripts/montar_com_narracao.py
Saida: saida/filme_narrado_v1.mp4 e saida/filme_narrado_v1_leve.mp4
"""
import json
import os
import re
import subprocess
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NARR = os.path.join(RAIZ, "audio", "narracao_ia")
FPS = 24
INTRO = 3.0          # abertura sem fala
PAUSA = 0.7          # respiro entre paragrafos
LOGO = 4.0           # cartela final
FUSAO_LEGENDA = 0.2

# paragrafo -> trechos (clipe, legenda). A legenda e o texto falado do trecho.
ROTEIRO = [
    [("saida/previas/MOV_B_aproximacao_frontal.mp4", "Bem-vindo à Inova Industrial."),
     ("clipes_ia/c03_apresentador_v1.mov", "Mais do que fabricar equipamentos, nós damos vida a projetos e transformamos desafios em soluções de alta performance."),
     ("clipes_ia/c04_soldador_v1.mov", "Cada peça que sai da nossa fábrica carrega o nosso nome e a nossa determinação"),
     ("clipes_ia/c05_frigorifico_v1.mov", "em ser o melhor suporte para a indústria frigorífica.")],
    [("saida/previas/MOV_A_orbita_descendente.mp4", "Nascemos em 2015, mas nossa base foi construída com mais de duas décadas de experiência"),
     ("clipes_ia/c07_dedo_levantado_v1.mov", "e um propósito inegociável: a excelência."),
     ("clipes_ia/c08_projeto_v1.mov", "Ser a parceira mais ágil e assertiva do mercado exige mais do que tecnologia;"),
     ("clipes_ia/c09_qualidade_v1.mov", "exige olhar para cada detalhe com a responsabilidade de quem sabe que a nossa qualidade é o que garante o sucesso do nosso cliente."),
     ("clipes_ia/c10_apresentador_joinha_v1.mov", "Na Inova, o padrão 'bom' não basta. Nós entregamos o impecável.")],
    [("clipes_ia/c11_boas_vindas_v1.mov", "Você entra hoje para um time que valoriza o ser humano acima de tudo."),
     ("clipes_ia/c12_harmonia_v1.mov", "Acreditamos que grandes resultados são frutos de um ambiente de respeito e harmonia."),
     ("clipes_ia/c14_apontando_v1.mov", "Você é o protagonista desta engrenagem. Sua dedicação e o seu capricho são os elementos que mantêm a Inova como referência de confiança e inovação.")],
    [("clipes_ia/c15_seguranca_v1.mov", "Mas lembre-se: para alcançarmos a excelência externa, precisamos de cuidado interno. Sua segurança é o nosso maior valor."),
     ("clipes_ia/c16_epis_v1.mov", "O uso de EPIs, como protetor auricular, óculos e botinas,"),
     ("clipes_ia/c17_faixa_seguranca_v1.mov", "e o respeito rigoroso aos procedimentos não são apenas regras; são o compromisso que você assume consigo mesmo e com seus colegas."),
     ("clipes_ia/c18_cuidado_v1.mov", "Na Inova, cuidamos uns dos outros para que todos cresçam juntos.")],
    [("clipes_ia/c19_mao_no_peito_v1.mov", "Estamos felizes em ter você aqui. Mais do que um colaborador, você é o novo embaixador da nossa qualidade."),
     ("clipes_ia/c20_caminhada_v1.mov", "Prepare-se para uma jornada onde seu esforço será valorizado e sua evolução será constante.")],
    [("saida/previas/MOV_A_orbita_descendente.mp4", "Inova Industrial: mais do que produzir equipamentos, um compromisso com a excelência, com o cliente e com o seu futuro.")],
]
ABERTURA = "saida/previas/MOV_C_travelling_avenida.mp4"
# clipes em que andar de tras para frente ficaria visivel: so camera lenta com mistura de quadros
SEM_REVERSO = {"c17_faixa_seguranca_v1.mov", "c20_caminhada_v1.mov", "c04_soldador_v1.mov"}


def rodar(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def duracao(arq):
    r = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq])
    return float(r.stdout.strip())


def preparar_paragrafo(i, tmp):
    """Volume padrao, sem silencio nas pontas. Devolve (wav, duracao, pausas)."""
    saida = os.path.join(tmp, f"p{i}.wav")
    filtro = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,"
              "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse,"
              "loudnorm=I=-16:TP=-1.5:LRA=11")
    rodar(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(NARR, f"p{i}.m4a"), "-af", filtro,
           "-ar", "48000", "-ac", "2", saida])
    d = duracao(saida)
    r = subprocess.run(["ffmpeg", "-i", saida, "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    pausas = [(a + b) / 2 for a, b in zip(ini, fim) if 0.3 < (a + b) / 2 < d - 0.3]
    return saida, d, pausas


def dividir(trechos, d, pausas):
    """Inicio de cada trecho dentro do paragrafo (s), alinhado as pausas."""
    palavras = [len(t.split()) for _, t in trechos]
    total = sum(palavras)
    inicios, acum = [0.0], 0
    for p in palavras[:-1]:
        acum += p
        alvo = d * acum / total
        perto = [x for x in pausas if abs(x - alvo) <= 1.2 and x > inicios[-1] + 1.0]
        inicios.append(min(perto, key=lambda x: abs(x - alvo)) if perto else alvo)
    return inicios


def ajustar_clipe(arq, dur, tmp, nome, inicio_fonte=0.0, fim_fonte=None):
    """Clipe com exatamente `dur` segundos a 24 qps, 1920x1080, sem selo 'Ai'."""
    caminho = os.path.join(RAIZ, arq)
    base = []
    if arq.startswith("clipes_ia/"):
        base += ["crop=iw-16:ih-16:8:8", "delogo=x=42:y=32:w=72:h=70"]
    base += ["scale=1920:1080:flags=lanczos", "setsar=1"]
    d_src = (fim_fonte or duracao(caminho)) - inicio_fonte
    fator = dur / d_src
    saida = os.path.join(tmp, f"{nome}.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(inicio_fonte), "-t", f"{d_src:.3f}", "-i", caminho]
    if fator <= 1.3:
        vf = ",".join(base + [f"setpts={fator:.4f}*PTS", f"fps={FPS}"])
        cmd += ["-vf", vf]
    elif os.path.basename(arq) in SEM_REVERSO:
        vf = ",".join(base + [f"setpts={fator:.4f}*PTS", f"framerate=fps={FPS}"])
        cmd += ["-vf", vf]
    else:
        # ida em camera lenta 1,25x e volta (reverso) ate completar
        ida = d_src * 1.25
        volta = max(0.1, dur - ida)
        fc = (f"[0:v]{','.join(base)},split[a][b];"
              f"[a]setpts=1.25*PTS,fps={FPS}[f];"
              f"[b]reverse,setpts={max(1.0, volta / d_src * 1.0):.4f}*PTS,fps={FPS},trim=duration={volta:.3f}[r];"
              f"[f][r]concat=n=2:v=1[v]")
        cmd += ["-filter_complex", fc, "-map", "[v]"]
    cmd += ["-t", f"{dur:.3f}", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", saida]
    rodar(cmd)
    return saida


def cartela_logo(tmp):
    saida = os.path.join(tmp, "logo.mp4")
    logo = os.path.join(RAIZ, "texturas", "logo_original_fundo_escuro.png")
    rodar(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x1d1f21:s=1920x1080:d={LOGO}:r={FPS}",
           "-loop", "1", "-i", logo, "-filter_complex",
           "[1]scale=1100:-1,format=rgba,fade=in:st=0.3:d=0.8:alpha=1[l];[0][l]overlay=(W-w)/2:(H-h)/2",
           "-t", str(LOGO), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", saida])
    return saida


def tc(s):
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def main():
    tmp = tempfile.mkdtemp(prefix="narrado_", dir=os.path.join(RAIZ, "saida"))
    cenas, legendas, audios = [], [], []
    t = INTRO
    cenas.append((ABERTURA, INTRO, {"inicio_fonte": 6.0 - INTRO}))
    mapa = []
    for i, trechos in enumerate(ROTEIRO, 1):
        wav, d, pausas = preparar_paragrafo(i, tmp)
        audios.append((wav, t))
        inicios = dividir(trechos, d, pausas)
        for k, (arq, texto) in enumerate(trechos):
            ini = t + inicios[k]
            fim = t + (inicios[k + 1] if k + 1 < len(trechos) else d + (PAUSA if i < len(ROTEIRO) else 0.6))
            dur = fim - ini
            opc = {}
            if "MOV_A" in arq and i == 2:
                opc = {"inicio_fonte": 0.0, "fim_fonte": 4.0}
            elif "MOV_A" in arq:
                opc = {"inicio_fonte": 3.0}
            cenas.append((arq, dur, opc))
            legendas.append((ini, ini + min(dur, (inicios[k + 1] - inicios[k]) if k + 1 < len(trechos) else d - inicios[k]), texto))
            mapa.append({"paragrafo": i, "clipe": os.path.basename(arq), "inicio": round(ini, 2), "duracao": round(dur, 2)})
        t += d + (PAUSA if i < len(ROTEIRO) else 0.6)
    total = t + LOGO

    arquivos = []
    for n, (arq, dur, opc) in enumerate(cenas):
        arquivos.append(ajustar_clipe(arq, dur, tmp, f"c{n:02d}", **opc))
    arquivos.append(cartela_logo(tmp))
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as fh:
        fh.writelines(f"file '{a}'\n" for a in arquivos)

    ass = os.path.join(tmp, "legendas.ass")
    with open(ass, "w", encoding="utf-8") as fh:
        fh.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\n"
                 "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Alignment, "
                 "MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow\n"
                 "Style: L,DejaVu Sans,46,&H00FFFFFF,&H00000000,&H80000000,1,2,160,160,70,1,3,1\n\n"
                 "[Events]\nFormat: Layer, Start, End, Style, Text\n")
        for a, b, texto in legendas:
            fh.write(f"Dialogue: 0,{tc(a)},{tc(b - 0.05)},L,{{\\fad(150,150)}}{texto}\n")

    entradas, atrasos = [], []
    for k, (wav, ini) in enumerate(audios):
        entradas += ["-i", wav]
        ms = int(ini * 1000)
        atrasos.append(f"[{k + 1}:a]adelay={ms}|{ms}[a{k}]")
    mix = ";".join(atrasos) + ";" + "".join(f"[a{k}]" for k in range(len(audios))) + \
        f"amix=inputs={len(audios)}:normalize=0,apad,atrim=0:{total:.3f}[aout]"
    saida = os.path.join(RAIZ, "saida", "filme_narrado_v1.mp4")
    rodar(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, *entradas,
           "-filter_complex", f"[0:v]settb=AVTB,setpts=N/{FPS}/TB,fps={FPS},ass={ass},"
                              f"fade=in:st=0:d=0.5,fade=out:st={total - 0.6:.2f}:d=0.6[v];{mix}",
           "-map", "[v]", "-map", "[aout]", "-t", f"{total:.3f}",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", saida])
    leve = saida.replace(".mp4", "_leve.mp4")
    rodar(["ffmpeg", "-y", "-v", "error", "-i", saida, "-vf", "scale=1280:-2", "-c:v", "libx264", "-crf", "25",
           "-preset", "slow", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", leve])
    with open(os.path.join(RAIZ, "saida", "filme_narrado_v1_mapa.json"), "w", encoding="utf-8") as fh:
        json.dump(mapa, fh, indent=1, ensure_ascii=False)
    print("ok", saida, f"{total:.1f}s")


if __name__ == "__main__":
    main()
