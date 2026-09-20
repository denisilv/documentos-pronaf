#!/usr/bin/env python3
"""
Site para geração de documentos PRONAF / Banco da Amazônia
Rode com: python app.py
Acesse: http://127.0.0.1:5000
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from geradores import (
    gerar_declaracao_atividade,
    gerar_declaracao_posse_mansa,
    gerar_declaracao_vizinhanca,
    gerar_ficha_cadastral,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pronaf-docs-2026'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GERADOS_DIR = os.path.join(BASE_DIR, 'gerados')
os.makedirs(GERADOS_DIR, exist_ok=True)

# Lista de cidades de agências do Banco da Amazônia no Maranhão (pode expandir)
AGENCIAS_MA = [
    "ALTO PARNAÍBA",
    "BACABAL",
    "BALSAS",
    "CAROLINA",
    "CAXIAS",
    "COROATÁ",
    "ESTREITO",
    "IMPERATRIZ",
    "PINHEIRO",
    "SANTA INÊS",
    "SÃO LUÍS",
    "VITÓRIA DO MEARIM",
]


@app.route('/')
def index():
    agencias_ordenadas = sorted(AGENCIAS_MA)
    return render_template('index.html', agencias=agencias_ordenadas)


@app.route('/gerar', methods=['POST'])
def gerar():
    try:
        # Coleta todos os campos do formulário
        dados = {
            # Pessoais
            "nome": request.form.get("nome", "").strip().upper(),
            "cpf": request.form.get("cpf", "").strip(),
            "rg": request.form.get("rg", "").strip(),
            "orgao_rg": request.form.get("orgao_rg", "SSP").strip().upper(),
            "uf_rg": request.form.get("uf_rg", "MA").strip().upper(),
            "data_expedicao_rg": request.form.get("data_expedicao_rg", "").strip(),
            "data_nascimento": request.form.get("data_nascimento", "").strip(),
            "local_nascimento": request.form.get("local_nascimento", "").strip().upper(),
            "uf_nascimento": request.form.get("uf_nascimento", "MA").strip().upper(),
            "estado_civil": request.form.get("estado_civil", "").strip().upper(),
            "regime_casamento": request.form.get("regime_casamento", "").strip().upper(),
            "genero": request.form.get("genero", "").strip(),
            "nome_mae": request.form.get("nome_mae", "").strip().upper(),
            "nacionalidade": request.form.get("nacionalidade", "brasileira").strip().lower(),

            # Endereço
            "endereco": request.form.get("endereco", "").strip().upper(),
            "bairro": request.form.get("bairro", "ZONA RURAL").strip().upper(),
            "cidade": request.form.get("cidade", "").strip().upper(),
            "uf": request.form.get("uf", "MA").strip().upper(),
            "cep": request.form.get("cep", "").strip(),
            "complemento": request.form.get("complemento", "").strip(),

            # Cônjuge
            "conjuge_nome": request.form.get("conjuge_nome", "").strip().upper(),
            "conjuge_cpf": request.form.get("conjuge_cpf", "").strip(),

            # Imóvel / Atividade
            "nome_propriedade": request.form.get("nome_propriedade", "").strip().upper(),
            "area_ha": request.form.get("area_ha", "").strip(),
            "numero_caf": request.form.get("numero_caf", "").strip().upper(),
            "atividade": request.form.get("atividade", "agricultora").strip().lower(),
            "tipo_atividade": request.form.get("tipo_atividade", "pecuária").strip().lower(),
            "tempo_atividade": request.form.get("tempo_atividade", "05 (cinco)").strip(),
            "tempo_posse": request.form.get("tempo_posse", "2 (dois)").strip(),
            "qualificacao": request.form.get("qualificacao", "Pecuarista").strip(),
            "latitude": request.form.get("latitude", "").strip(),
            "longitude": request.form.get("longitude", "").strip(),
            "ano_inicio_posse": request.form.get("ano_inicio_posse", "").strip(),
            "comprovante_energia": request.form.get("comprovante_energia", "NÃO").strip().upper(),
            "croqui": request.form.get("croqui", "SIM").strip().upper(),

            # Técnica
            "nome_tecnica": request.form.get("nome_tecnica", "AMANDA APARECIDA MILEN LIRA").strip().upper(),
            "cfta": request.form.get("cfta", "07752713309").strip(),
            "empresa": request.form.get("empresa", "F E A DA SILVA JUNIOR LTDA").strip().upper(),
            "empresa_cnpj": request.form.get("empresa_cnpj", "51.786.165/0001-71").strip(),
            "cidade_agencia": request.form.get("cidade_agencia", "SANTA INÊS").strip().upper(),
            "cidade_agencia_outra": request.form.get("cidade_agencia_outra", "").strip().upper(),

            # Outros
            "data_declaracao": request.form.get("data_declaracao", datetime.now().strftime("%d/%m/%Y")).strip(),
            "pep": request.form.get("pep", "Não").strip(),
            "proposito": request.form.get("proposito", "Realizar empréstimos ou financiamentos.").strip(),
        }

        # Junta Latitude + Longitude no formato que os documentos usam
        lat = request.form.get("latitude", "").strip()
        lon = request.form.get("longitude", "").strip()

        # Garante o S e o O no final
        if lat and not lat.upper().endswith("S"):
            lat = lat.rstrip('"') + '"S'
        if lon and not lon.upper().endswith("O"):
            lon = lon.rstrip('"') + '"O'

        if lat and lon:
            dados["coordenadas"] = f"Lat: {lat} Lon: {lon}"
        elif lat:
            dados["coordenadas"] = f"Lat: {lat}"
        elif lon:
            dados["coordenadas"] = f"Lon: {lon}"
        else:
            dados["coordenadas"] = ""

        # Se escolheu "OUTRA", usa o campo livre
        if "OUTRA" in dados["cidade_agencia"].upper():
            if dados["cidade_agencia_outra"]:
                dados["cidade_agencia"] = dados["cidade_agencia_outra"]

        # Gera timestamp para os arquivos
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_safe = dados["nome"].replace(" ", "_")[:30] if dados["nome"] else "cliente"

        arquivos = {}

        # Gera os 4 documentos
        path1 = os.path.join(GERADOS_DIR, f"DECLARACAO_ATIVIDADE_{nome_safe}_{ts}.pdf")
        gerar_declaracao_atividade(dados, path1)
        arquivos["atividade"] = os.path.basename(path1)

        path2 = os.path.join(GERADOS_DIR, f"DECLARACAO_POSSE_MANSA_{nome_safe}_{ts}.pdf")
        gerar_declaracao_posse_mansa(dados, path2)
        arquivos["posse"] = os.path.basename(path2)

        path3 = os.path.join(GERADOS_DIR, f"DECLARACAO_VIZINHANCA_{nome_safe}_{ts}.pdf")
        gerar_declaracao_vizinhanca(dados, path3)
        arquivos["vizinhanca"] = os.path.basename(path3)

        path4 = os.path.join(GERADOS_DIR, f"FICHA_CADASTRAL_{nome_safe}_{ts}.pdf")
        gerar_ficha_cadastral(dados, path4)
        arquivos["ficha"] = os.path.basename(path4)

        return render_template('resultado.html', arquivos=arquivos, nome=dados["nome"])

    except Exception as e:
        return f"<h2>Erro ao gerar documentos</h2><pre>{str(e)}</pre><a href='/'>Voltar</a>", 500


@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(GERADOS_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Arquivo não encontrado", 404


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*50)
    print("  Site de Documentos PRONAF")
    print(f"  Porta: {port}")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
