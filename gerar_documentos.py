#!/usr/bin/env python3
"""Ponto de entrada simples para gerar os documentos de exemplo do projeto."""

import os
import sys

# Torna o script executável a partir da raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from geradores import gerar_todos, DADOS_EXEMPLO


if __name__ == "__main__":
    print("Gerando documentos de exemplo...")
    gerar_todos(DADOS_EXEMPLO)
