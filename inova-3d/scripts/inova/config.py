"""Caminhos do projeto e leitura dos arquivos de configuracao."""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(RAIZ, "config")
TEXTURAS = os.path.join(RAIZ, "texturas")
REFERENCIAS = os.path.join(RAIZ, "referencias")
SAIDA = os.path.join(RAIZ, "saida")
CENAS = os.path.join(RAIZ, "cenas")


def carregar(nome):
    """Le config/<nome>.json."""
    with open(os.path.join(CONFIG, nome + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def textura(nome):
    return os.path.join(TEXTURAS, nome)
