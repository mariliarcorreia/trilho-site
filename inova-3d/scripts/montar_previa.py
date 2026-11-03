"""Monta a previa visual do filme (sem narracao), com o texto do roteiro em legenda.

Cada trecho e normalizado para 1920x1080 a 24 fps; dos clipes do CapCut sai a
marca "Ai" do canto e a borda arredondada. Os trechos sao unidos com cortes secos.

Uso: python scripts/montar_previa.py
Saida: saida/previa_filme_v2.mp4
"""
import os
import subprocess
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUSAO = 0.4

# (arquivo, inicio, duracao, legenda)
LINHA_DO_TEMPO = [
    ("saida/previas/MOV_C_travelling_avenida.mp4", 0, 6.0, ""),
    ("saida/previas/MOV_B_aproximacao_frontal.mp4", 0, 6.0, "Bem-vindo à Inova Industrial."),
    ("clipes_ia/c03_apresentador_v1.mov", 0, 5.0, "Mais do que fabricar equipamentos, nós damos vida a projetos e transformamos desafios em soluções de alta performance."),
    ("clipes_ia/c04_soldador_v1.mov", 0, 5.0, "Cada peça que sai da nossa fábrica carrega o nosso nome e a nossa determinação"),
    ("clipes_ia/c05_frigorifico_v1.mov", 0, 5.0, "em ser o melhor suporte para a indústria frigorífica."),
    ("saida/previas/MOV_A_orbita_descendente.mp4", 0, 5.0, "Nascemos em 2015, mas nossa base foi construída com mais de duas décadas de experiência"),
    ("clipes_ia/c07_dedo_levantado_v1.mov", 0, 5.0, "e um propósito inegociável: a excelência."),
    ("clipes_ia/c08_projeto_v1.mov", 0, 5.0, "Ser a parceira mais ágil e assertiva do mercado exige mais do que tecnologia;"),
    ("clipes_ia/c09_qualidade_v1.mov", 0, 5.0, "exige olhar para cada detalhe com a responsabilidade de quem sabe que a nossa qualidade é o que garante o sucesso do nosso cliente."),
    ("clipes_ia/c10_apresentador_joinha_v1.mov", 0, 5.0, "Na Inova, o padrão 'bom' não basta. Nós entregamos o impecável."),
    ("clipes_ia/c11_boas_vindas_v1.mov", 0, 5.0, "Você entra hoje para um time que valoriza o ser humano acima de tudo."),
    ("clipes_ia/c12_harmonia_v1.mov", 0, 5.0, "Acreditamos que grandes resultados são frutos de um ambiente de respeito e harmonia."),
    ("clipes_ia/c14_apontando_v1.mov", 0, 5.0, "Você é o protagonista desta engrenagem. Sua dedicação e o seu capricho mantêm a Inova como referência de confiança e inovação."),
    ("clipes_ia/c15_seguranca_v1.mov", 0, 5.0, "Mas lembre-se: para alcançarmos a excelência externa, precisamos de cuidado interno. Sua segurança é o nosso maior valor."),
    ("clipes_ia/c16_epis_v1.mov", 0, 5.0, "O uso de EPIs, como protetor auricular, óculos e botinas,"),
    ("clipes_ia/c17_faixa_seguranca_v1.mov", 0, 5.0, "e o respeito rigoroso aos procedimentos são o compromisso que você assume consigo mesmo e com seus colegas."),
    ("clipes_ia/c18_cuidado_v1.mov", 0, 5.0, "Na Inova, cuidamos uns dos outros para que todos cresçam juntos."),
    ("clipes_ia/c19_mao_no_peito_v1.mov", 0, 5.0, "Estamos felizes em ter você aqui. Mais do que um colaborador, você é o novo embaixador da nossa qualidade."),
    ("clipes_ia/c20_caminhada_v1.mov", 0, 5.0, "Prepare-se para uma jornada onde seu esforço será valorizado e sua evolução será constante."),
    ("saida/previas/MOV_A_orbita_descendente.mp4", 0, 7.0, "Inova Industrial: mais do que produzir equipamentos, um compromisso com a excelência, com o cliente e com o seu futuro."),
    ("LOGO", 0, 4.0, ""),
]


def _ass(texto, dur, caminho):
    def tc(s):
        return f"0:00:{s:05.2f}"
    cab = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, "
        "Alignment, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow\n"
        "Style: L,DejaVu Sans,46,&H00FFFFFF,&H00000000,&H80000000,1,2,160,160,70,1,3,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Text\n"
    )
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(cab + f"Dialogue: 0,{tc(0.15)},{tc(dur - 0.25)},L,{{\\fad(200,200)}}{texto}\n")


def normalizar(i, arq, ini, dur, texto, tmp):
    saida = os.path.join(tmp, f"t{i:02d}.mp4")
    if arq == "LOGO":
        logo = os.path.join(RAIZ, "texturas", "logo_original_fundo_escuro.png")
        cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x1d1f21:s=1920x1080:d={dur}:r=24",
               "-loop", "1", "-i", logo, "-filter_complex",
               "[1]scale=1100:-1,format=rgba,fade=in:st=0.3:d=0.8:alpha=1[l];[0][l]overlay=(W-w)/2:(H-h)/2",
               "-t", str(dur), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", saida]
        subprocess.run(cmd, check=True)
        return saida
    caminho = os.path.join(RAIZ, arq)
    filtros = []
    if arq.startswith("clipes_ia/"):
        # remove borda arredondada e a marca "Ai" do canto superior esquerdo
        filtros += ["crop=iw-16:ih-16:8:8", "delogo=x=42:y=32:w=72:h=70"]
    filtros += ["scale=1920:1080:flags=lanczos", "fps=24", "setsar=1"]
    if texto:
        ass = os.path.join(tmp, f"t{i:02d}.ass")
        _ass(texto, dur, ass)
        filtros.append(f"ass={ass}")
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(ini), "-i", caminho, "-t", str(dur), "-an",
           "-vf", ",".join(filtros), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", saida]
    subprocess.run(cmd, check=True)
    return saida


def main():
    tmp = tempfile.mkdtemp(prefix="previa_", dir=os.path.join(RAIZ, "saida"))
    trechos = [normalizar(i, *t, tmp) for i, t in enumerate(LINHA_DO_TEMPO)]
    # cortes secos (como na referencia), com fade curto so na entrada e na saida do filme
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as fh:
        for p in trechos:
            fh.write(f"file '{p}'\n")
    total = sum(t[2] for t in LINHA_DO_TEMPO)
    saida = os.path.join(RAIZ, "saida", "previa_filme_v2.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista,
           "-vf", f"settb=AVTB,setpts=N/24/TB,fps=24,fade=in:st=0:d=0.5,fade=out:st={total - 0.6}:d=0.6",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", saida]
    subprocess.run(cmd, check=True)
    print("ok", saida)


if __name__ == "__main__":
    main()
