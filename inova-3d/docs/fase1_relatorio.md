# Fase 1: reconstrução da fachada | relatório para aprovação

## Arquivos analisados

| Arquivo | Conteúdo | Uso |
|---|---|---|
| 3 capturas de tela (quadros do drone) | vistas A (aérea oblíqua), B (frontal baixa), C (frontal ampla) | **fonte de verdade** da arquitetura; recortadas em `referencias/fotos_drone/` |
| Logomarca oficial (PNG com transparência) | ícone + INOVA laranja + INDUSTRIAL | letreiros e emblema, sem alteração de desenho |
| Ilustração do técnico com uniforme | camisa azul, capacete branco, óculos, crachá | referência para a fase 3 (não usada agora) |
| Composição de 3 vistas gerada por IA | releitura das fotos | **não usada** como referência arquitetônica (regra 9) |
| 2 arquivos .mov (mesmo vídeo, 2 min 46 s) | filme 3D da Arroz Vasconcelos | referência de linguagem e acabamento (estilo de animação estilizada, iluminação quente, personagem narrador fixo intercalado com cenas) |
| DJI_0171.MP4 e DJI_0174.MP4 (Drive) | vídeos originais do drone | **não acessados**: a rede deste ambiente bloqueia o download e o conector só entrega arquivos pequenos. As capturas enviadas são quadros desses vídeos |
| Roteiro de integração | | **não recebido** |

## Método

1. 43 pontos marcados nas três fotos (`referencias/pontos_correspondencia.json`).
2. Ajuste conjunto de 3 câmeras + 26 dimensões (`ferramentas/calibrar_cameras.py`).
3. Detalhes medidos por retroprojeção da foto B nos planos da fachada e do piso (`ferramentas/retroprojetar.py`).
4. Modelo paramétrico em `config/fachada.json`; cena gerada por `scripts/run.py`.
5. Render com as câmeras calibradas e comparação automática (`ferramentas/comparar.py`).

## Dimensões principais obtidas

| Elemento | Medida estimada | Confiança |
|---|---|---|
| Galpão principal: frente x altura | 35,65 m x 10,75 m | alta |
| Faixa branca inferior do galpão | 3,18 m de altura, colunas grafite a cada ~5,4 m | alta |
| Letreiro INOVA (galpão principal) | 8,4 m x 2,2 m, centro a 8,3 m de altura | alta |
| Prédio administrativo: frente x altura do beiral | 18,4 m x 7,3 m, 13,2 m à frente do galpão | alta |
| Torre grafite | 3,7 m de largura, 8,1 m de altura, avanço de 0,6 m | alta |
| Emblema da torre | Ø 1,6 m, centro a 5,7 m | alta |
| Janelas | 2,25 m de largura; 1,15 m (sup.) e 0,95 m (inf.) de altura | alta |
| Gradil frontal | 2,4 m de altura, a 30,4 m da fachada do galpão | alta |
| Calçada | 4,6 m | média |
| Galpão secundário | frente recuada 19 m, 12 m de altura, letreiro 7,7 m | média |
| Profundidade dos galpões | 60 m e 40 m | **baixa** (não aparece em nenhuma foto) |

A escala absoluta depende de três âncoras (pessoa na calçada, altura do gradil e lente do drone). A incerteza estimada de escala é de 5 a 10%. Uma única medida real (por exemplo, largura do galpão ou altura do prédio) elimina essa incerteza: basta alterar o valor em `config/fachada.json` e calibrar de novo.

## Resultado da comparação

Valores de `saida/comparacao/metricas.json` (distância entre contornos da foto e do render):

| Vista | Mediana foto→render | Bordas da foto a até 5 px | a até 10 px | Mediana render→foto | v01 (antes dos ajustes) foto→render |
|---|---|---|---|---|---|
| A | 3.2 px | 62% | 78% | 3.0 px | 3.2 px |
| B | 3.0 px | 60% | 75% | 3.0 px | 3.6 px |
| C | 4.1 px | 54% | 65% | 3.2 px | 12.0 px |

Reprojeção dos 43 pontos marcados pelas câmeras do Blender: 5,8 px (A), 4,4 px (B), 3,5 px (C) de erro médio, em imagens de 1290 x 726.

Na foto C, parte das bordas da foto vem do bairro ao fundo e dos prédios vizinhos, que só estão representados de forma genérica. Por isso a métrica foto para render é mais alta nessa vista, mesmo com os volumes da Inova alinhados.

## Diferenças encontradas

**Corrigidas nesta fase**
- Céu estourado e falta de contraste: relação sol/céu ajustada (sol 6, céu 0,035, exposição -0,35).
- Painéis solares aparecendo demais acima da platibanda: telhado rebaixado 0,6 m atrás da platibanda e inclinação de 2°.
- Sombra do letreiro duplicando a palavra INDUSTRIAL: letreiro aplicado rente ao revestimento.
- Tela do gradil opaca: espessura do arame corrigida.
- Motos junto ao gradil aparentando estar do lado de fora: recuadas 0,5 m.
- Horizonte vazio: faixa genérica de árvores e casas baixas (marcada como contexto).

**Pendentes (dependem de informação ou ficam para a fase 2)**
1. **Fachada envidraçada à esquerda do prédio administrativo**: nas fotos A e B aparece um veículo atrás do vidro. Modelei como ambiente envidraçado de pé-direito duplo com laje intermediária. Confirmar se é hall, garagem ou showroom.
2. **Ligação entre o prédio administrativo e o galpão**: as fotos não mostram se há vão entre eles. O modelo encosta o prédio no galpão.
3. **Fundo dos galpões, oitões e o restante do telhado**: não aparecem nas fotos. Painéis solares foram colocados só onde a foto A mostra.
4. **Mastro alto e torre treliçada ao fundo**: aparecem nas fotos B e C, mas a triangulação ficou inconclusiva (raios quase paralelos). Não foram incluídos.
5. **Veículos**: modelos volumétricos com silhueta, escala e cor corretas. Detalhamento (faróis, rodas, frisos) na fase 2.
6. **Vizinhança e horizonte**: volumes simplificados e faixa genérica. Para fidelidade total, seria preciso um levantamento do entorno.
7. **Céu**: sem nuvens. As fotos têm cúmulos esparsos, que entram na fase 2 (direção de arte).
8. **Seta de conversão pintada na avenida** (foto C): não incluída.
9. **Cor e textura**: materiais procedurais coerentes com as fotos, ainda sem sujeira, manchas de escorrimento e marcas de pneus, que entram na fase 2.

## Itens que preciso de você

1. Aprovação (ou correções) da volumetria e da implantação.
2. Roteiro de integração (texto da narração).
3. Uma ou duas medidas reais (largura do galpão principal ou altura do prédio administrativo).
4. Se possível, os vídeos do drone em outro formato de compartilhamento (link público direto ou upload na conversa), para conferir os demais ângulos.
5. Confirmação da função do ambiente envidraçado.
