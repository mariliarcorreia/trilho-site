# Inova Industrial | Produção 3D cinematográfica

Projeto Blender + Python (bpy) do filme institucional da Inova Industrial.
Esta pasta contém a **Fase 1: reconstrução da fachada**, com três câmeras calibradas nas fotos reais do drone e três movimentos de drone para aprovação. Ainda não há personagens.

## 1. Estrutura de pastas

```
inova-3d/
├── config/                     parâmetros editáveis (JSON)
│   ├── fachada.json            dimensões, posições, fonte e confiança de cada medida
│   ├── calibracao.json         câmeras e dimensões resolvidas a partir das fotos (gerado)
│   ├── cameras.json            câmeras de validação e movimentos de drone
│   └── render.json             luz, cor e perfis de render (teste, previa, validacao, final)
├── referencias/
│   ├── fotos_drone/            recortes 1290x726 dos quadros reais (A, B, C)
│   ├── identidade/             logomarca oficial e referência de uniforme
│   └── pontos_correspondencia.json   pixels marcados nas fotos para a calibração
├── texturas/                   logomarca (variante da fachada) e ícone do emblema
├── scripts/
│   ├── run.py                  ponto de entrada (constrói, renderiza, salva)
│   └── inova/
│       ├── config.py           caminhos e leitura de JSON
│       ├── core/cena.py        coleções idempotentes e primitivas
│       ├── geometria/          galpoes, administrativo, terreno (piso, gradil, poste), veiculos
│       ├── materiais/          biblioteca de materiais PBR
│       ├── iluminacao/         céu físico + sol
│       ├── cameras/            câmeras de validação e movimentos de drone
│       ├── render/             perfis Cycles, stills, sequências, MP4
│       ├── personagens/        fase 3 (técnico de segurança)
│       ├── equipamentos/       fase 4
│       ├── vfx/                fase 4
│       └── composicao/         fase 5 (áudio, letterings, exportação)
├── ferramentas/
│   ├── calibrar_cameras.py     resolve câmeras + dimensões a partir das fotos
│   ├── retroprojetar.py        pixel da foto -> coordenada métrica num plano conhecido
│   └── comparar.py             render x foto: lado a lado, cortina, mescla, bordas, métricas
├── cenas/                      arquivos .blend gerados
├── audio/                      narração, trilha e efeitos (fase 5)
├── saida/
│   ├── validacao/              renders das câmeras A, B, C
│   ├── comparacao/             imagens de comparação e metricas.json
│   └── previas/                MP4 dos movimentos de drone
└── docs/                       relatórios de cada marco
```

## 2. Arquitetura dos scripts

`scripts/run.py` lê os JSON de `config/` e chama, em ordem, um construtor por módulo. Cada construtor:

1. obtém a sua coleção sob `INOVA/...` com `cena.colecao_limpa()`, que apaga o conteúdo anterior;
2. cria a geometria em coordenadas de mundo (metros), com materiais da `biblioteca`;
3. não depende de estado deixado por execuções anteriores.

Por isso o script pode ser executado quantas vezes for preciso, inclusive sobre um `.blend` já salvo, sem duplicar objetos. Materiais são recriados pelo nome; veículos e motos usam coleções-modelo (`MODELO_*`) instanciadas, o que mantém a cena leve.

| Módulo | Responsabilidade |
|---|---|
| `geometria/galpoes.py` | G1 (casca nervurada, faixa branca, colunas, letreiro, reservatório, telhado duas águas), anexo lateral, G2 com base em blocos, painéis solares |
| `geometria/administrativo.py` | corpo de dois pavimentos, fachada envidraçada com caixilhos, janelas recuadas com brises, beiral em ACM, torre grafite com juntas e emblema, jardineira |
| `geometria/terreno.py` | pátio, calçada, meio-fio, avenida duplicada com canteiro e sinalização, rua lateral, terreno de terra vermelha, muros, gradil com concertina, poste |
| `geometria/veiculos.py` | carros, motos e bicicletas nas posições do dia da filmagem; volumes vizinhos de contexto |
| `materiais/biblioteca.py` | materiais PBR procedurais (metal nervurado, alvenaria, ACM, vidro fumê, asfalto, terra, módulos FV, tela soldada, logomarca) |
| `iluminacao/externa.py` | céu físico (multiple scattering) + sol direcional |
| `cameras/externas.py` | `CAM_A/B/C` calibradas; `MOV_*` animadas; verificação de reprojeção |
| `render/perfis.py` | Cycles com denoiser, AgX, perfis, sequências PNG/EXR, MP4 via ffmpeg |

## 3. Recursos necessários

| Recurso | Uso | Situação |
|---|---|---|
| Blender 4.2 LTS ou mais recente (testado com 5.1.2) | modelagem, animação, Cycles | obrigatório |
| GPU NVIDIA (OptiX) ou Apple Silicon (Metal) | render final 4K em tempo viável | recomendado; o script detecta sozinho |
| Python 3.11+ com `numpy`, `scipy`, `pillow` | calibração e comparação (fora do Blender) | obrigatório para as ferramentas |
| ffmpeg | montar MP4 das prévias e do filme | obrigatório |
| Vídeos originais do drone (DJI_0171, DJI_0174) | mais ângulos para calibração e texturas | **pendente**: não foi possível baixar do Drive neste ambiente |
| Roteiro de integração da Inova | storyboard, tempos de cada tomada, narração | **pendente**: não veio anexado |
| Planta ou medidas reais (opcional) | substituir estimativas por medidas exatas | desejável |
| Fotos do interior e dos EPIs reais | cenas internas e personagem | necessário para as fases 3 e 4 |

## 4. Estratégia de reconstrução fiel da fachada

1. **Somente fotos reais como fonte de verdade.** Os três quadros de drone (A aérea oblíqua, B frontal baixa, C frontal ampla) foram recortados sem as bordas do celular. A imagem composta gerada por IA não foi usada para geometria.
2. **Calibração conjunta** (`ferramentas/calibrar_cameras.py`). Foram marcados 43 pixels correspondentes a cantos identificáveis (galpão, prédio, torre, gradil, meio-fio). Um ajuste por mínimos quadrados resolve ao mesmo tempo a pose e a lente das três câmeras e as dimensões principais. A escala vem da pessoa na calçada (1,72 m), da altura típica do gradil e da lente de 24 mm equivalente dos quadros sem zoom.
3. **Retroprojeção dos detalhes** (`ferramentas/retroprojetar.py`). Com as câmeras resolvidas, cada janela, coluna, letreiro, portão, poste e veículo foi medido projetando o pixel da foto sobre o plano conhecido (fachada ou piso).
4. **Parâmetros editáveis com origem registrada.** Todas as medidas estão em `config/fachada.json` com `fonte` e `confianca`. Onde nenhuma foto mostra (fundo dos galpões, parte do telhado), o valor é marcado como estimativa e nada é inventado além do mínimo necessário para fechar o volume.
5. **Logomarca sem alteração.** O arquivo oficial é usado diretamente. Na fachada real, as partes brancas do logo aparecem em grafite; a textura `logo_fachada.png` muda apenas essa cor, mantendo o desenho.

## 5. Câmeras externas

| Câmera | Foto | Posição (m) | Rotação XYZ (°) | Lente (mm, sensor 36) | Erro médio |
|---|---|---|---|---|---|
| `CAM_A` | aérea oblíqua | (39,65; -81,13; 42,90) | (65,27; 2,77; 18,69) | 59,8 | 5,8 px |
| `CAM_B` | frontal baixa | (21,76; -63,92; 11,27) | (78,47; 0,30; 5,74) | 37,4 | 4,4 px |
| `CAM_C` | frontal ampla | (23,50; -89,49; 18,31) | (82,78; 2,36; 5,30) | 25,6 | 3,5 px |

Movimentos de drone (`config/cameras.json`), todos terminando exatamente no enquadramento calibrado:

| Movimento | Duração | Descrição |
|---|---|---|
| `MOV_B_aproximacao_frontal` | 6 s | sobe da altura da avenida e avança até a vista B, revelando a fachada por cima do gradil |
| `MOV_C_travelling_avenida` | 6 s | travelling lateral sobre a avenida até a vista ampla C |
| `MOV_A_orbita_descendente` | 7 s | desce do alto (telhado solar) até a vista oblíqua A, com aproximação de lente |

## 6. Script executável da maquete

`scripts/run.py` (ver cabeçalho do arquivo para todas as opções).

## 7. Como executar

Com Blender instalado:

```bash
cd inova-3d
# constrói a cena e salva para abrir no Blender
blender -b -P scripts/run.py -- --salvar cenas/fachada_v01.blend
# renders de validação (A, B, C) na resolução das fotos
blender -b -P scripts/run.py -- --render validacao
# prévias dos movimentos de drone em MP4
blender -b -P scripts/run.py -- --render movimentos --perfil previa
# prévia rápida: 1 a cada 3 quadros, só um movimento
blender -b -P scripts/run.py -- --render movimentos --perfil teste --passo 3 --movimentos MOV_B_aproximacao_frontal
```

Sem Blender instalado (módulo `bpy` do PyPI, mesma API):

```bash
python -m venv .venv && .venv/bin/pip install bpy==5.1.2 numpy scipy pillow
.venv/bin/python scripts/run.py --render validacao
```

Para editar: abra `cenas/fachada_v01.blend` no Blender, ou altere `config/fachada.json` e rode o script de novo. Para refazer a calibração depois de marcar novos pontos: `python ferramentas/calibrar_cameras.py --overlay`.

## 8. Renderização e comparação com as fotos

1. `--render validacao` gera `saida/validacao/render_{A,B,C}.png` com as câmeras calibradas, na mesma resolução dos recortes das fotos.
2. `python ferramentas/comparar.py` gera, para cada câmera, lado a lado, cortina (metade foto, metade render), mescla 50% e mapa de bordas (vermelho = só na foto, ciano = só no render, branco = coincidem), além de `metricas.json` com a distância entre contornos.
3. O arquivo `saida/validacao/verificacao_cameras_blender.json` confirma que as câmeras do Blender reproduzem a calibração (erro de reprojeção dos pontos marcados).
4. As diferenças encontradas e as pendências ficam registradas em `docs/fase1_relatorio.md`.
