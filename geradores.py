#!/usr/bin/env python3
"""
Gerador de Documentos PRONAF / Banco da Amazônia
Gera os 4 documentos com layout o mais idêntico possível aos originais.
"""

import os
from datetime import datetime
import reportlab
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT


def _candidate_font_path(*paths):
    """Retorna o primeiro caminho existente; devolve None se nenhum existir."""
    for path in paths:
        if path and os.path.exists(path):
            return path
    return None


def _register_font(alias, *paths):
    """Registra a fonte com o primeiro arquivo físico verdadeiramente presente."""
    font_path = _candidate_font_path(*paths)
    if font_path:
        pdfmetrics.registerFont(TTFont(alias, font_path))
    else:
        # Último fallback defensivo: usa a família Vera do ReportLab.
        fallback_path = os.path.join(os.path.dirname(reportlab.__file__), 'fonts', 'Vera.ttf')
        if os.path.exists(fallback_path):
            pdfmetrics.registerFont(TTFont(alias, fallback_path))


# Registrar fontes com fallbacks portáteis (Linux/Windows/ReportLab)
windows_font_dir = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'Fonts')
reportlab_fonts_dir = os.path.join(os.path.dirname(reportlab.__file__), 'fonts')

_register_font('Liberation',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    os.path.join(windows_font_dir, 'arial.ttf'),
    os.path.join(reportlab_fonts_dir, 'Vera.ttf'),
)
_register_font('Liberation-Bold',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    os.path.join(windows_font_dir, 'arialbd.ttf'),
    os.path.join(reportlab_fonts_dir, 'VeraBd.ttf'),
)
_register_font('Liberation-Italic',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf',
    os.path.join(windows_font_dir, 'ariali.ttf'),
    os.path.join(reportlab_fonts_dir, 'VeraIt.ttf'),
)
_register_font('Liberation-BoldItalic',
    '/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf',
    os.path.join(windows_font_dir, 'arialbi.ttf'),
    os.path.join(reportlab_fonts_dir, 'VeraBI.ttf'),
)
_register_font('DejaVu',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    os.path.join(windows_font_dir, 'arial.ttf'),
    os.path.join(reportlab_fonts_dir, 'Vera.ttf'),
)
_register_font('DejaVu-Bold',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    os.path.join(windows_font_dir, 'arialbd.ttf'),
    os.path.join(reportlab_fonts_dir, 'VeraBd.ttf'),
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gerados")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cores
VERDE_HEADER = HexColor("#2E7D32")
VERDE_CLARO = HexColor("#4CAF50")
CINZA = HexColor("#333333")
CINZA_CLARO = HexColor("#666666")
AZUL_BANCO = HexColor("#003366")

DADOS_EXEMPLO = {
    "nome": "JOÃO DA SILVA",
    "cpf": "12345678909",
    "rg": "1234567",
    "orgao_rg": "SSP",
    "uf_rg": "MA",
    "data_expedicao_rg": "15/06/2015",
    "data_nascimento": "12/03/1988",
    "local_nascimento": "BOM JARDIM",
    "uf_nascimento": "MA",
    "estado_civil": "SOLTEIRO(A)",
    "regime_casamento": "",
    "genero": "Masculino",
    "nome_mae": "MARIA DA SILVA",
    "nacionalidade": "Brasileira",
    "endereco": "SÍTIO SÃO BENEDITO",
    "bairro": "ZONA RURAL",
    "cidade": "BOM JARDIM",
    "uf": "MA",
    "cep": "65450-000",
    "complemento": "",
    "conjuge_nome": "",
    "conjuge_cpf": "",
    "nome_propriedade": "FAZENDA SÃO JOÃO",
    "area_ha": "15",
    "numero_caf": "1234567890",
    "atividade": "agricultora",
    "tipo_atividade": "pecuária",
    "tempo_atividade": "05 (cinco)",
    "tempo_posse": "2 (dois)",
    "qualificacao": "Pecuarista",
    "latitude": "05° 15' 20\"S",
    "longitude": "45° 40' 10\"O",
    "ano_inicio_posse": "2018",
    "comprovante_energia": "SIM",
    "croqui": "SIM",
    "nome_tecnica": "AMANDA APARECIDA MILEN LIRA",
    "cfta": "07752713309",
    "empresa": "F E A DA SILVA JUNIOR LTDA",
    "empresa_cnpj": "51.786.165/0001-71",
    "cidade_agencia": "SANTA INÊS",
    "cidade_agencia_outra": "",
    "data_declaracao": "06/10/2026",
    "pep": "Não",
    "proposito": "Realizar empréstimos ou financiamentos.",
    "coordenadas": "Lat: 05° 15' 20\"S Lon: 45° 40' 10\"O",
}


def gerar_todos(dados: dict = None, output_dir: str = None):
    """Gera os quatro documentos usando um único dicionário de dados."""
    if dados is None:
        dados = DADOS_EXEMPLO
    if output_dir is None:
        output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    nome_safe = str(dados.get("nome", "CLIENTE")).replace(" ", "_")[:30] or "CLIENTE"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    arquivos = {}

    atividade_path = os.path.join(output_dir, f"DECLARACAO_ATIVIDADE_{nome_safe}_{ts}.pdf")
    gerar_declaracao_atividade(dados, atividade_path)
    arquivos["atividade"] = os.path.basename(atividade_path)

    posse_path = os.path.join(output_dir, f"DECLARACAO_POSSE_MANSA_{nome_safe}_{ts}.pdf")
    gerar_declaracao_posse_mansa(dados, posse_path)
    arquivos["posse"] = os.path.basename(posse_path)

    vizinhanca_path = os.path.join(output_dir, f"DECLARACAO_VIZINHANCA_{nome_safe}_{ts}.pdf")
    gerar_declaracao_vizinhanca(dados, vizinhanca_path)
    arquivos["vizinhanca"] = os.path.basename(vizinhanca_path)

    ficha_path = os.path.join(output_dir, f"FICHA_CADASTRAL_{nome_safe}_{ts}.pdf")
    gerar_ficha_cadastral(dados, ficha_path)
    arquivos["ficha"] = os.path.basename(ficha_path)

    return arquivos


def format_cpf(cpf: str) -> str:
    cpf = "".join(filter(str.isdigit, str(cpf)))
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def format_date_br(date_str: str) -> str:
    """Aceita DD/MM/YYYY ou YYYY-MM-DD e retorna DD/MM/YYYY"""
    if not date_str:
        return ""
    date_str = date_str.strip()
    if "-" in date_str and len(date_str) == 10:
        y, m, d = date_str.split("-")
        return f"{d}/{m}/{y}"
    return date_str


def data_extenso(date_str: str) -> str:
    """Converte data para formato '16 de Janeiro de 2026'"""
    meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    try:
        d = format_date_br(date_str)
        dia, mes, ano = d.split("/")
        return f"{int(dia)} de {meses[int(mes)]} de {ano}"
    except Exception:
        return date_str


# ============================================================
# 1. DECLARAÇÃO DE ATIVIDADE
# ============================================================
def gerar_declaracao_atividade(dados: dict, output_path: str = None):
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "DECLARACAO_DE_ATIVIDADE.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

     # ===== HEADER VERDE =====
    c.setFillColor(VERDE_HEADER)
    c.rect(0, height - 38*mm, width, 38*mm, fill=1, stroke=0)

   # Texto da empresa (lado esquerdo / centro)
    c.setFillColor(white)
    c.setFont("Liberation-Bold", 13)
    c.drawCentredString(width/2, height - 18*mm, "F E A DA SILVA JUNIOR LTDA")
    c.setFont("Liberation", 12)
    c.drawCentredString(width/2, height - 24*mm, "ELABORAÇÃO DE PROJETOS PARA")
    c.drawCentredString(width/2, height - 30*mm, "FINANCIAMENTOS AGROPECUÁRIOS")
    c.setFont("Liberation-Bold", 12)
    c.drawCentredString(width/2, height - 37*mm, f"CNPJ: {dados.get('empresa_cnpj', '51.786.165/0001-71')}")

    # Logo Rural CRED (lado direito)
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "logo_ruralcred.png")
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, width - 48*mm, height - 36*mm, width=38*mm, height=32*mm, mask='auto')
        except Exception:
            pass

    # ===== TÍTULO =====
    y = height - 65*mm
    c.setFillColor(black)
    c.setFont("Liberation-Bold", 14)
    c.drawCentredString(width/2, y, "DECLARAÇÃO DE ATIVIDADE")
    # Sublinhado
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    text_w = c.stringWidth("DECLARAÇÃO DE ATIVIDADE", "Liberation-Bold", 14)
    c.line(width/2 - text_w/2, y - 2*mm, width/2 + text_w/2, y - 2*mm)

    # ===== CORPO =====
    y = height - 85*mm
    left = 25*mm
    right = width - 25*mm
    max_width = right - left

    # Dados variáveis
    nome_tecnica = dados.get("nome_tecnica", "AMANDA APARECIDA MILEN LIRA")
    cfta = dados.get("cfta", "07752713309")
    empresa = dados.get("empresa", "F E A DA SILVA JUNIOR LTDA")
    cidade_agencia = dados.get("cidade_agencia", "SANTA INÊS")
    nome_cliente = dados.get("nome", "").upper()

    genero = dados.get("genero", "").lower()
    eh_masculino = genero in ["masculino", "masc"]

    nacionalidade = "brasileiro" if eh_masculino else "brasileira"

    estado_civil_raw = dados.get("estado_civil", "").upper()
    if eh_masculino:
        estado_civil = (
           estado_civil_raw
           .replace("SOLTEIRA", "SOLTEIRO")
           .replace("CASADA", "CASADO")
           .replace("DIVORCIADA", "DIVORCIADO")
           .replace("VIÚVA", "VIÚVO")
           .replace("VIUVA", "VIUVO")
           .lower()
       )
    else:
      estado_civil = estado_civil_raw.lower()

    atividade = "agricultor" if eh_masculino else "agricultora"
    tratamento = "o Sr." if eh_masculino else "a Sra."
    portador = "portador" if eh_masculino else "portadora"
    domiciliado = "domiciliado" if eh_masculino else "domiciliada"

    rg = dados.get("rg", "")
    orgao_rg = dados.get("orgao_rg", "SSP")
    uf_rg = dados.get("uf_rg", "MA")
    cpf = format_cpf(dados.get("cpf", ""))
    endereco = dados.get("endereco", "")
    bairro = dados.get("bairro", "Zona Rural")
    cidade = dados.get("cidade", "")
    uf = dados.get("uf", "MA")
    tempo_atividade = dados.get("tempo_atividade", "05 (cinco)")
    tipo_atividade = dados.get("tipo_atividade", "pecuária")

    texto = (
    f"Eu, <b>{nome_tecnica}</b>, técnica agrícola em agropecuária CFTA nº "
    f"<b>{cfta}</b>, responsável técnica da empresa <b>{empresa}</b> prestadora "
    f"de serviço de assistência técnica no estado do Maranhão, credenciamento no "
    f"<b>BANCO DA AMAZÔNIA/{cidade_agencia.upper()} – MA</b>, vem através desta "
    f"declaração para os devidos fins de direitos e a quem mais possa interessar que "
    f"{tratamento} <b>{nome_cliente}</b>, {nacionalidade}, {estado_civil}, {atividade}, "
    f"{portador} da carteira de identidade Nº <b>{rg} {orgao_rg}/{uf_rg}</b> "
    f"CPF nº <b>{cpf}</b> residente e {domiciliado} no <b>{endereco}</b>, "
    f"<b>{bairro}</b>, Município de <b>{cidade}</b>, estado do Maranhão, "
    f"desempenha as atividades <b>{tipo_atividade}</b> há mais de <b>{tempo_atividade}</b> "
    f"anos em sua propriedade."
)

    style = ParagraphStyle(
        "corpo",
        fontName="Liberation",
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        textColor=black,
    )

    p = Paragraph(texto, style)
    w, h = p.wrap(max_width, 200*mm)
    p.drawOn(c, left, y - h)

    # ===== LOCAL E DATA =====
    y = y - h - 25*mm
    data_dec = dados.get("data_declaracao", datetime.now().strftime("%d/%m/%Y"))
    c.setFont("Liberation", 11)
    c.drawRightString(right, y, "Bom Jardim/MA")
    c.drawRightString(right, y - 6*mm, data_extenso(data_dec))

    c.save()
    print(f"✓ Gerado: {output_path}")
    return output_path


# ============================================================
# 2. DECLARAÇÃO DE POSSE MANSA E PACÍFICA
# ============================================================
def gerar_declaracao_posse_mansa(dados: dict, output_path: str = None):
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "DECLARACAO_DE_POSSE_MANSA.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Classificação (canto superior direito)
    c.setStrokeColor(black)
    c.setLineWidth(0.7)
    c.rect(width - 55*mm, height - 22*mm, 40*mm, 14*mm)
    c.setFont("Liberation", 8)
    c.drawCentredString(width - 35*mm, height - 12*mm, "Classificação da")
    c.drawCentredString(width - 35*mm, height - 16*mm, "informação")
    c.setFont("Liberation-Bold", 8)
    c.drawCentredString(width - 35*mm, height - 20.5*mm, "PÚBLICO")

    # Título do apêndice
    c.setFont("Liberation", 10)
    c.drawString(25*mm, height - 25*mm, "Apêndice D – Declaração de Posse Mansa e Pacífica")

    # Título DECLARAÇÃO
    y = height - 50*mm
    c.setFont("Liberation-Bold", 13)
    c.drawCentredString(width/2, y, "DECLARAÇÃO")
    text_w = c.stringWidth("DECLARAÇÃO", "Liberation-Bold", 13)
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    c.line(width/2 - text_w/2, y - 2*mm, width/2 + text_w/2, y - 2*mm)

    # Corpo
    y = height - 70*mm
    left = 25*mm
    right = width - 25*mm
    max_width = right - left

    nome = dados.get("nome", "").upper()
    numero_caf = dados.get("numero_caf", "")
    tempo_posse = "2 (dois)"

    texto = (
        f"Declaro para os devidos fins de direito que tenho a posse mansa e pacífica, nos termos "
        f"do Código Civil, Lei 10.406 de 10.01.2002, do imóvel descrito na DAP – Declaração de Aptidão "
        f"ao Pronaf nº <b>{numero_caf}</b>, o qual exploro há mais de <b>{tempo_posse}</b> anos."
    )

    style = ParagraphStyle(
        "corpo",
        fontName="Liberation",
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
    )
    p = Paragraph(texto, style)
    w, h = p.wrap(max_width, 100*mm)
    p.drawOn(c, left, y - h)

    # Local e data
    y = y - h - 20*mm
    cidade = dados.get("cidade", "Bom Jardim")
    data_dec = dados.get("data_declaracao", datetime.now().strftime("%d/%m/%Y"))
    c.setFont("Liberation", 11)
    c.drawString(left, y, "Bom Jardim-MA")
    c.drawString(left, y - 6*mm, format_date_br(data_dec))

    # Linha de assinatura (acima do nome)
    y = y - 25*mm
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    c.line(left, y, left + 120*mm, y)   # linha maior

    # Dados abaixo da linha
    y = y - 5*mm
    c.setFont("Liberation", 10)
    c.drawString(left, y, "Nome: " + nome)
    c.drawString(left, y - 6*mm, "Endereço: " + dados.get("endereco_completo", dados.get("endereco", "") + ", " + dados.get("bairro", "")))
    c.drawString(left, y - 12*mm, "Qualificação: " + dados.get("qualificacao", "Pecuarista"))

    # Testemunhas
    y = y - 45*mm
    c.setFont("Liberation-Bold", 11)
    c.drawString(left, y, "Testemunhas:")

    y = y - 25*mm
    c.setFont("Liberation", 10)
    c.drawString(left, y, "Nome: ________________________________________________________")
    c.drawString(left, y - 10*mm, "CPF: ___________________________________")

    y = y - 25*mm
    c.drawString(left, y, "Nome: ________________________________________________________")
    c.drawString(left, y - 10*mm, "CPF: ___________________________________")

    c.save()
    print(f"✓ Gerado: {output_path}")
    return output_path


# ============================================================
# 3. DECLARAÇÃO DE VIZINHANÇA
# ============================================================
def gerar_declaracao_vizinhanca(dados: dict, output_path: str = None):
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "DECLARACAO_DE_VIZINHANCA.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Cabeçalho
    c.setFont("Liberation", 8)
    c.drawString(18*mm, height - 12*mm, "410- GESTÃO DE CRÉDITO")
    c.drawString(18*mm, height - 16*mm, "NP 438- DOCUMENTAÇÃO QUANTO À CONDIÇÃO DO PROPONENTE")
    c.setFont("Liberation-Bold", 9)
    c.drawString(18*mm, height - 20*mm, "Apêndice I - Declaração de Vizinhança")

    # Classificação
    c.setStrokeColor(black)
    c.setLineWidth(0.7)
    c.rect(width - 50*mm, height - 20*mm, 35*mm, 12*mm)
    c.setFont("Liberation", 8)
    c.drawCentredString(width - 32.5*mm, height - 12*mm, "Classificação da")
    c.drawCentredString(width - 32.5*mm, height - 15*mm, "informação")
    c.setFont("Liberation-Bold", 8)
    c.drawCentredString(width - 32.5*mm, height - 18.5*mm, "PÚBLICO")

    # Título principal
    y = height - 25*mm
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(18*mm, y - 6*mm, width - 36*mm, 8*mm)
    c.setFont("Liberation-Bold", 12)
    c.drawCentredString(width/2, y - 3.5*mm, "DECLARAÇÃO DE VIZINHANÇA")

    # ===== 1. IDENTIFICAÇÃO DO POSSEIRO =====
    y = y - 11*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(18*mm, y, "1. IDENTIFICAÇÃO DO POSSEIRO")

    def draw_field(label, value, x, y, label_w=35*mm, field_w=60*mm, height_box=6*mm):
        c.setFont("Liberation", 9)
        c.drawString(x, y + 1.5*mm, label)
        c.setStrokeColor(HexColor("#999999"))
        c.setLineWidth(0.4)
        c.rect(x + label_w, y, field_w, height_box)
        c.setFillColor(black)
        c.setFont("Liberation-Bold", 10)
        c.drawString(x + label_w + 1.5*mm, y + 1.5*mm, str(value)[:40])

    y = y - 8*mm
    # Nome
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 2*mm, "Nome")
    c.setFont("Liberation-Bold", 10)
    c.drawString(35*mm, y + 1*mm, dados.get("nome", "").upper())

    y = y - 9*mm
    # Nacionalidade | Naturalidade | Data Nasc
    c.rect(18*mm, y - 1*mm, 60*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.4*mm, "Nacionalidade")
    c.setFont("Liberation-Bold", 10)
    c.drawString(19*mm, y + 0.1*mm, dados.get("nacionalidade", "BRASILEIRA").upper())

    c.rect(78*mm, y - 1*mm, 65*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(79*mm, y + 3.4*mm, "Naturalidade")
    c.setFont("Liberation-Bold", 10)
    c.drawString(79*mm, y + 0.1*mm, f"{dados.get('local_nascimento', '')}-{dados.get('uf_nascimento', 'MA')}".upper())

    c.rect(143*mm, y - 1*mm, 49*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(144*mm, y + 3.4*mm, "Data de Nascimento")
    c.setFont("Liberation-Bold", 10)
    c.drawString(144*mm, y + 0.1*mm, format_date_br(dados.get("data_nascimento", "")))

     # Estado Civil
    y = y - 9*mm
    c.rect(18*mm, y - 1*mm, 40*mm, 7.5*mm)
    c.setFont("Liberation", 9)

    c.drawString(19*mm, y + 3.4*mm, "Estado Civil")
    estado_civil_raw = dados.get("estado_civil", "").upper()
    genero = dados.get("genero", "").lower()
    if genero in ["masculino", "masc"]:
        estado_civil = (
         estado_civil_raw
         .replace("SOLTEIRA", "SOLTEIRO")
          .replace("CASADA", "CASADO")
          .replace("DIVORCIADA", "DIVORCIADO")
          .replace("VIÚVA", "VIÚVO")
          .replace("VIUVA", "VIUVO")
        )
    else:
        estado_civil = estado_civil_raw
    c.setFont("Liberation-Bold", 10)
    c.drawString(19*mm, y + 0.1*mm, estado_civil)

    # D.I
    c.rect(58*mm, y - 1*mm, 47*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(59*mm, y + 3.4*mm, "D.I TIPO: RG, CTPS, OUTROS")
    c.setFont("Liberation-Bold", 10)
    c.drawString(59*mm, y + 0.1*mm, "RG")

    c.rect(105*mm, y - 1*mm, 50*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(106*mm, y + 3.4*mm, "Número/Emissor")
    c.setFont("Liberation-Bold", 10)
    c.drawString(106*mm, y + 0.1*mm, f"{dados.get('rg', '')} {dados.get('orgao_rg', 'SSP')}/{dados.get('uf_rg', 'MA')}")

    #CPF
    c.rect(155*mm, y - 1*mm, 37*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(156*mm, y + 3.4*mm, "CPF")
    c.setFont("Liberation-Bold", 10)
    c.drawString(156*mm, y + 0.1*mm, format_cpf(dados.get("cpf", "")))

    # ===== 1.1 Cônjuge =====
    y = y - 5*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(18*mm, y, "1.1 Identificação do cônjuge")

    y = y - 8*mm
    c.rect(18*mm, y - 1*mm, width - 73*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.4*mm, "Nome")
    c.setFont("Liberation-Bold", 10)
    c.drawString(19*mm, y + 0.1*mm, dados.get("conjuge_nome", "").upper())

    c.rect(155*mm, y - 1*mm, 37*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(156*mm, y + 3.4*mm, "CPF")
    c.setFont("Liberation-Bold", 10)
    c.drawString(156*mm, y + 0.1*mm, format_cpf(dados.get("conjuge_cpf", "")))

    y = y - 9*mm
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.4*mm, "Endereço Residencial:")
    c.setFont("Liberation-Bold", 10)
    endereco_full = f"{dados.get('endereco', '')}, {dados.get('bairro', '')}"
    c.drawString(55*mm, y + 0.1*mm, endereco_full[:70])

    # ===== 2. DADOS DO IMÓVEL =====
    y = y - 6*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(18*mm, y, "2. DADOS DO IMÓVEL")

    y = y - 9*mm
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.4*mm, "Denominação")
    c.setFont("Liberation-Bold", 10)
    c.drawString(55*mm, y + 0.1*mm, dados.get("nome_propriedade", "").upper())

    y = y - 9*mm
    c.rect(18*mm, y - 1*mm, 80*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.4*mm, "Município de Localização")
    c.setFont("Liberation-Bold", 10)
    c.drawString(19*mm, y + 0.1*mm, dados.get("cidade", "").upper())

    c.rect(98*mm, y - 1*mm, 20*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(99*mm, y + 3.4*mm, "Estado")
    c.setFont("Liberation-Bold", 10)
    c.drawString(99*mm, y + 0.1*mm, dados.get("uf", "MARANHÃO").upper())

    c.rect(118*mm, y - 1*mm, 35*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(119*mm, y + 3.4*mm, "Área (ha)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(119*mm, y + 0.1*mm, str(dados.get("area_ha", "")))

    c.rect(153*mm, y - 1*mm, 39*mm, 7.5*mm)
    c.setFont("Liberation", 9)
    c.drawString(154*mm, y + 3.4*mm, "Ano de Inicio da Posse")
    c.setFont("Liberation-Bold", 10)
    c.drawString(154*mm, y + 0.1*mm, str(dados.get("ano_inicio_posse", "")))

    y = y - 10.5*mm
    c.rect(18*mm, y - 1*mm, width - 36*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 4*mm, "Indicações para o acesso (estradas, ramais etc.):")
  
    # Confrontantes
    y = y - 8*mm
    c.setFont("Liberation", 10)
    c.drawString(18*mm, y, "CONFRONTANTES (mínimo de três):")

    for i in range(1, 4):
        y = y - 10*mm
        c.setFont("Liberation", 9)
        c.drawString(18*mm, y + 2*mm, f"Confrontante {i}")
        c.rect(40*mm, y - 1*mm, 152*mm, 9*mm)
        c.setFont("Liberation", 9)
        c.drawString(41*mm, y + 1*mm, "Assinatura")
        
        y = y - 7*mm
        c.rect(40*mm, y - 1*mm, 152*mm, 7*mm)
        c.drawString(41*mm, y + 1*mm, "Nome/CPF")

    # Coordenadas
    y = y - 9*mm
    c.setStrokeColor(black)
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 1.5*mm, "Coordenadas Geográficas GPS (na residência)")
    c.setFont("Liberation-Bold", 10)
    coords = dados.get("coordenadas", "")
    c.drawString(110*mm, y + 1*mm, coords)

    y = y - 8.5*mm
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 1.5*mm, "Identificação de mercado")
    c.setFont("Liberation-Bold", 10)
    c.drawString(110*mm, y + 0.5*mm, dados.get("nome_propriedade", "").upper())

    # ===== 3. RELAÇÕES =====
    y = y - 6*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(18*mm, y, "3. RELAÇÕES SOCIAIS E ECONOMICAS e DOCUMENTOS")

    y = y - 8*mm
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 1.5*mm, "Documentos de posse (anexar)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(85*mm, y + 0.5*mm, "DECLARAÇÃO DE POSSE MANSA E PACIFICA")

    y = y - 7*mm
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 1.5*mm, "Cartório Firma Reconhecida")
    c.setFont("Liberation-Bold", 10)
    c.drawString(85*mm, y + 0.5*mm, f"COMARCA DE {dados.get('cidade', '').upper()}-MA")

    y = y - 9.5*mm
    c.rect(18*mm, y - 1*mm, 90*mm, 8*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.8*mm, "Comprovante de pagamento de energia elétrica rural (anexar)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(19*mm, y + 0.1*mm, dados.get("comprovante_energia", "NÃO"))

    c.rect(108*mm, y - 1*mm, 84*mm, 8*mm)
    c.setFont("Liberation", 9)
    c.drawString(109*mm, y + 3.8*mm, "Croqui da área (anexar)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(109*mm, y + 0.1*mm, dados.get("croqui", "SIM"))

    y = y - 6*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(18*mm, y, "Detenterior anterior da posse")

    y = y - 8*mm
    c.rect(18*mm, y - 1*mm, 110*mm, 8*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.8*mm, "Nome")

    c.rect(128*mm, y - 1*mm, 64*mm, 8*mm)
    c.setFont("Liberation", 9)
    c.drawString(129*mm, y + 3.8*mm, "CPF")

    y = y - 8*mm
    c.rect(18*mm, y - 1*mm, 174*mm, 8*mm)
    c.setFont("Liberation", 9)
    c.drawString(19*mm, y + 3.8*mm, "Informações sobre litigio ou não da área:")

    # Declaração final
    y = y - 2*mm
    texto_final = (
        "Declaro sob as penas da lei que as informações por mim prestadas acima expressam a verdade e que detenho de fato o "
        "direito de uso, na condição de posseiro do imóvel rural acima descrito. Declaro ainda que este documento não tem "
        "validade para efeito de regularização fundiária, somente para comprovação da posse do imóvel junto ao Banco da "
        "Amazônia S.A."
    )
    style = ParagraphStyle("final", fontName="Liberation", fontSize=9.5, leading=9, alignment=TA_JUSTIFY)
    p = Paragraph(texto_final, style)
    w, h = p.wrap(width - 44*mm, 40*mm)

    # Caixa ao redor do texto
    padding = 2*mm
    c.setStrokeColor(black)
    c.setLineWidth(0.6)
    c.rect(18*mm, y - h - padding, width - 36*mm, h + 1.5*padding)

    # Texto dentro da caixa
    p.drawOn(c, 22*mm, y - h)

    y = y - 25*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(50*mm, y, "__________________________________________________________")

    # Assinatura
    y = y - 4.8*mm
    c.setStrokeColor(HexColor("#FFFFFF"))
    c.rect(18*mm, y - 1*mm, width - 36*mm, 7*mm)
    c.setFont("Liberation-Bold", 10)
    c.drawCentredString(width/2, y, dados.get("nome", "").upper())
    c.setFont("Liberation", 10)
    c.drawCentredString(width/2, y - 5*mm, format_cpf(dados.get("cpf", "")))

    c.save()
    print(f"✓ Gerado: {output_path}")
    return output_path


# ============================================================
# 4. FICHA CADASTRAL PRONAF (versão completa e estruturada)
# ============================================================
def gerar_ficha_cadastral(dados: dict, output_path: str = None):
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "FICHA_CADASTRAL_PRONAF.pdf")

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    def header(page_num):
        c.setFont("Liberation", 7)
        c.setFillColor(HexColor("#666666"))
        c.drawRightString(width - 15*mm, height - 8*mm, "#INTERNA")
        
        # Inserindo a Logo real (Certifique-se de que o arquivo 'logo_banco.png' está na pasta)
        # Parâmetros: (imagem, x, y, largura, altura)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "logo_banco.png")
        if os.path.exists(logo_path):
           try:
               c.drawImage(logo_path, 10*mm, height - 15*mm, width=55*mm, height=7*mm, mask='auto')
           except Exception as e:
               print("Erro ao carregar logo do banco:", e)
        else:
            print("Logo não encontrada em:", logo_path)
            c.setFont("Liberation-Bold", 9)
            c.setFillColor(AZUL_BANCO)
            c.drawString(15*mm, height - 12*mm, "BANCO DA AMAZÔNIA")

        c.setFillColor(black)
        c.setFont("Liberation-Bold", 12)
        # Título centralizado/ajustado ao lado da logo
        c.drawRightString(width - 16*mm, height - 15*mm, "FICHA DE CADASTRO-PESSOA FÍSICA (PRONAF)")

        if page_num == 1:
            largura_util = width - 30 * mm
            estilo_confidencial = ParagraphStyle(
                name="TextoConfidencial",
                fontName="Liberation",
                fontSize=10,
                leading=11,
            )
            texto_aviso = "Informações Confidenciais: Se o espaço não for suficiente em qualquer quadro, informar em uma relação à parte devidamente assinada."
            paragrafo = Paragraph(texto_aviso, estilo_confidencial)
            paragrafo.wrap(largura_util, height)
            paragrafo.drawOn(c, 15 * mm, height - 23 * mm)

    def footer(page_num, total=5):
        c.setStrokeColor(HexColor("#8B0000"))
        c.setLineWidth(2.5)
        c.line(15*mm, 12*mm, width - 15*mm, 12*mm)
        c.setFont("Liberation", 9)
        c.setFillColor(HexColor("#333333"))
        c.drawString(20*mm, 8*mm, "Ficha de Cadastro - Pessoa Física (PRONAF) – Versão 8")
        c.drawRightString(width - 15*mm, 6*mm, f"Página {page_num}")

    # ========== PÁGINA 1 ==========
    header(1)

    y = height - 28*mm
    # Cód Agência / Agência
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.rect(65*mm, y - 5*mm, 40*mm, 8*mm)
    c.setFont("Liberation", 9)
    c.drawString(66*mm, y + 0.1*mm, "Cód. Agência")
    c.rect(105*mm, y - 5*mm, 90*mm, 8*mm)
    c.drawString(106*mm, y + 0.1*mm, "Agência")

    # 1. DADOS BÁSICOS
    y = y - 8*mm
    c.setFont("Liberation-Bold", 9)
    c.setFillColor(black)
    c.drawString(15*mm, y, "1. DADOS BÁSICOS")

    y = y - 6*mm
    c.setStrokeColor(black)
    c.rect(15*mm, y - 6*mm, width - 30*mm, 10*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 1*mm, "NOME (COMPLETO SEM ABREVIATURA)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 4*mm, dados.get("nome", "").upper())

    y = y - 10*mm
    # CPF | Data Nasc | Local Nasc | UF
    campos = [
        (15, 50, "CPF", format_cpf(dados.get("cpf", ""))),
        (65, 40, "Data de Nascimento", format_date_br(dados.get("data_nascimento", ""))),
        (105, 75, "Local de Nascimento", dados.get("local_nascimento", "").upper()),
        (180, 15, "UF", dados.get("uf_nascimento", "MA").upper()),
    ]
    for x, w, label, val in campos:
        c.rect(x*mm, y - 5*mm, w*mm, 9*mm)
        c.setFont("Liberation", 9)
        c.drawString((x+1)*mm, y + 0.5*mm, label)
        c.setFont("Liberation-Bold", 10)
        c.drawString((x+1)*mm, y - 3.5*mm, val)

    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 80*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Estado Civil")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("estado_civil", "").upper())

    c.rect(95*mm, y - 5*mm, 100*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(96*mm, y + 0.5*mm, "Regime de Casamento")
    c.setFont("Liberation-Bold", 10)
    c.drawString(96*mm, y - 3.5*mm, dados.get("regime_casamento", "").upper())

    y = y - 10*mm
    c.setFont("Liberation", 9)
    c.drawString(15*mm, y, "Gênero")
    genero = dados.get("genero", "").lower()
    options = [("Masculino", 30), ("Feminino", 55), ("Não binário", 80), ("Prefiro não informar", 110)]
    for opt, x in options:
        c.rect(x*mm, y - 1*mm, 3.5*mm, 3.5*mm)
        if genero in opt.lower() or (genero == "feminino" and opt == "Feminino") or (genero == "masculino" and opt == "Masculino"):
            c.setFont("Liberation-Bold", 9)
            c.drawString(x*mm + 0.5*mm, y - 0.5*mm, "X")
        c.setFont("Liberation", 9)
        c.drawString((x+5)*mm, y, opt)

    y = y - 8*mm
    c.rect(15*mm, y - 5*mm, width - 30*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 1.5*mm, "Nome da Mãe")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("nome_mae", "").upper())

    # 2. DADOS DA IDENTIFICAÇÃO
    y = y - 10*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(15*mm, y, "2. DADOS DA IDENTIFICAÇÃO")

    y = y - 7*mm
    campos2 = [
        (15, 70, "Tipo Doc. Identificação", "REGISTRO GERAL"),
        (85, 45, "Nº do Documento", dados.get("rg", "")),
        (130, 30, "Órgão Expedidor", dados.get("orgao_rg", "SSP")),
        (160, 10, "UF", dados.get("uf_rg", "MA")),
        (170, 25, "Data Expedição", format_date_br(dados.get("data_expedicao_rg", ""))),
    ]
    for x, w, label, val in campos2:
        c.rect(x*mm, y - 5*mm, w*mm, 9*mm)
        c.setFont("Liberation", 9)
        c.drawString((x+1)*mm, y + 0.5*mm, label)
        c.setFont("Liberation-Bold", 10)
        c.drawString((x+1)*mm, y - 3.5*mm, str(val))

    # 3. DADOS DA LOCALIZAÇÃO
    y = y - 10*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(15*mm, y, "3. DADOS DA LOCALIZAÇÃO")

    y = y - 7*mm
    c.rect(15*mm, y - 5*mm, width - 30*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Endereço")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("endereco", "").upper())

    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 110*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Complemento")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("complemento", ""))

    c.rect(125*mm, y - 5*mm, 70*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(126*mm, y + 0.5*mm, "Bairro/Distrito")
    c.setFont("Liberation-Bold", 10)
    c.drawString(126*mm, y - 3.5*mm, dados.get("bairro", "").upper())

    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 70*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Cidade")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("cidade", "").upper())

    c.rect(85*mm, y - 5*mm, 20*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(86*mm, y + 0.5*mm, "UF")
    c.setFont("Liberation-Bold", 10)
    c.drawString(86*mm, y - 3.5*mm, dados.get("uf", "MA").upper())

    c.rect(105*mm, y - 5*mm, 35*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(106*mm, y + 0.5*mm, "País")
    c.setFont("Liberation-Bold", 10)
    c.drawString(106*mm, y - 3.5*mm, "BRASIL")

    c.rect(140*mm, y - 5*mm, 55*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(141*mm, y + 0.5*mm, "CEP")
    c.setFont("Liberation-Bold", 10)
    c.drawString(141*mm, y - 3.5*mm, dados.get("cep", ""))

    # Telefones e E-mail
    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 60*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Telefone residencial (DDD/DDI Número)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("telefone_residencial", ""))

    c.rect(75*mm, y - 5*mm, 60*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(76*mm, y + 0.5*mm, "Telefone celular (DDD/DDI Número)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(76*mm, y - 3.5*mm, dados.get("telefone_celular", ""))

    c.rect(135*mm, y - 5*mm, 60*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(136*mm, y + 0.5*mm, "Telefone comercial (DDD/DDI Número)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(136*mm, y - 3.5*mm, dados.get("telefone_comercial", ""))

    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 180*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Email")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("email", ""))

    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 180*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Outro Endereço p/correspondência")
    c.setFont("Liberation", 10)
    c.drawString(16*mm, y - 3.5*mm, "Sim [   ] Não [   ]")

    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 110*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Complemento")
    
    c.rect(125*mm, y - 5*mm, 70*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(126*mm, y + 0.5*mm, "Bairro/Distrito")

    y = y - 9*mm
    c.rect(15*mm, y - 5*mm, 70*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Cidade")

    c.rect(85*mm, y - 5*mm, 20*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(86*mm, y + 0.5*mm, "UF")

    c.rect(105*mm, y - 5*mm, 35*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(106*mm, y + 0.5*mm, "País")

    c.rect(140*mm, y - 5*mm, 55*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(141*mm, y + 0.5*mm, "CEP")

    # 4. RELACIONAMENTOS
    y = y - 10*mm
    c.setFont("Liberation-Bold", 9)
    c.drawString(15*mm, y, "4. DADOS DOS RELACIONAMENTOS")

    y = y - 4*mm
    c.setFont("Liberation-Bold", 9)
    c.drawString(15*mm, y, "DADOS DO CÔJUGE")

    y = y - 5*mm
    c.rect(15*mm, y - 5*mm, 130*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(16*mm, y + 0.5*mm, "Nome Completo (Cônjuge)")
    c.setFont("Liberation-Bold", 10)
    c.drawString(16*mm, y - 3.5*mm, dados.get("conjuge_nome", "").upper())

    c.rect(145*mm, y - 5*mm, 50*mm, 9*mm)
    c.setFont("Liberation", 9)
    c.drawString(146*mm, y + 0.5*mm, "CPF")
    c.setFont("Liberation-Bold", 10)
    c.drawString(146*mm, y - 3.5*mm, format_cpf(dados.get("conjuge_cpf", "")))

    # 5. PEP
    y = y - 10*mm
    c.setFont("Liberation-Bold", 9)
    c.drawString(15*mm, y, "5. EXERCÍCIO DE CARGO, EMPREGO OU FUNÇÃO PÚBLICA – PEP")
    y = y - 3*mm
    c.rect(16*mm, y - 11*mm, 179*mm, 11*mm)
    c.setFont("Liberation", 10)
    texto_pep = "De acordo com a Circular BACEN nº. 3.978, de 23/01/2020 o cliente é ou tem relação com pessoa que exerce ou exerceu, nos últimos 5 (cinco) anos, no Brasil, no exterior ou em dependência estrangeira, cargo, emprego ou função pública?"
    style = ParagraphStyle("pep", fontName="Liberation", fontSize=10, leading=8)
    p = Paragraph(texto_pep, style)
    w, h = p.wrap(width - 35*mm, 20*mm)
    p.drawOn(c, 18*mm, y - h)

    y = y - h - 6*mm
    c.rect(16*mm, y - 1.5*mm, 179*mm, 4.9*mm)
    c.setFont("Liberation", 10)
    c.drawString(17*mm, y, "[  ] Não                      [  ] Sim                      [  ] Titular                    [  ] Relacionado")

    y = y - 5*mm
    c.rect(16*mm, y - 9.5*mm, 179*mm, 13*mm)
    c.setFont("Liberation", 10)
    c.drawString(17*mm, y - 0.5, "[  ] Ele mesmo")
    c.setFont("Liberation", 10)
    c.drawString(17*mm, y - 4*mm, "[  ] Parente até 1º grau, cônjuge, companheiro (a) ou enteado (a)")
    c.setFont("Liberation", 10)
    c.drawString(17*mm, y - 8*mm, "[  ] Representante ou pessoa de seu relacionamento próximo (últs. 5 anos)")

    y = y - 15*mm
    c.setFont("Liberation", 10)
    c.drawString(16*mm, y, "*Se o cliente se enquadrar como PEP (titular ou relacionado) deverá preencher formulário específico, na forma do ")
    c.drawString(16*mm, y - 4*mm, "Apêndice F ou G, respectivamente.")
    c.setFillColor(black)

    footer(1)
    c.showPage()

    # ========== PÁGINA 2 - PROPÓSITO ==========
    header(2)
    y = height - 25*mm
    c.setFont("Liberation-Bold", 10)
    c.drawString(15*mm, y, "6. PROPÓSITO DA RELAÇÃO DE NEGÓCIO")

    y = y - 7*mm
    c.rect(15*mm, y - 6.5*mm, 179*mm, 11*mm)
    c.setFont("Liberation", 10)
    c.drawString(16*mm, y, "Em atendimento a exigência legal (Circular BACEN 3.978/2020 e alterações), declaro que minha relação de")
    y = y - 4*mm
    c.drawString(16*mm, y, "negócios com o Banco da Amazônia tem o seguinte propósito e natureza:")

    opcoes = [
        "Realizar movimentações financeiras em conta-corrente e/ou conta investimento e/ou conta de poupança.",
        "Realizar aplicações financeiras (ex.: fundos de investimento, CDB, ações).",
        "Realizar empréstimos ou financiamentos.",
        "Utilizar cartão de crédito.",
        "Realizar operações com moeda estrangeira.",
        "Contratar seguros e/ou previdência e/ou títulos de capitalização.",
        "Prestar Garantia.",
        "Outros: _______________________________",
    ]
    proposito = dados.get("proposito", "Realizar empréstimos ou financiamentos.").lower()

    y = y - 7*mm
    c.rect(15*mm, y - 53*mm, 179*mm, 57.7*mm)
    for opt in opcoes:
        c.rect(18*mm, y - 1*mm, 3.5*mm, 3.5*mm)
        if "empréstimo" in opt.lower() and "empréstimo" in proposito:
            c.setFont("Liberation-Bold", 9)
            c.drawString(18.5*mm, y - 0.5*mm, "X")
        c.setFont("Liberation", 8)
        c.drawString(24*mm, y, opt)
        y -= 7*mm

    footer(2)
    c.showPage()

    # ========== PÁGINAS 3-5 (texto fixo da declaração/autorização) ==========
    # Página 3
    header(3)
    y = height - 28*mm
    c.setFont("Liberation-Bold", 11)
    c.drawCentredString(width/2, y, "DECLARAÇÃO/AUTORIZAÇÃO")

    y = y - 8*mm
    texto_dec = """Declaro que os presentes dados são verdadeiros, e que em observância à Lei 13.709/2018 (LGPD) e demais legislações pertinentes, estou ciente que o Banco da Amazônia S.A., tratará meus dados pessoais aqui fornecidos, ou que venham a ser coletados ou recebidos em meios físicos e digitais, nos processos de negociação e transações bancárias, sendo uma primeira etapa para uma ou mais das seguintes finalidades:

a) possibilitar a oferta e a contratação de produtos e serviços personalizados e adequados;
b) viabilizar a análise e limite de crédito a ser ofertado;
c) possibilitar execução contratual ou procedimentos preliminares relacionados ao contrato do qual seja parte o titular dos dados, a pedido do titular dos dados pessoais;
d) possibilitar a comunicação, mediante correspondências, e-mails, contatos telefônicos, mensagens eletrônicas, bem como, a realização de visitas gerenciais e fiscalizações, necessárias a operacionalização de produtos e serviços;
e) abertura e movimentações financeiras em conta-corrente, conta investimento, conta de poupança;
f) assegurar a proteção ao crédito, a prevenção à fraude, o combate à lavagem de dinheiro e o financiamento do terrorismo ou qualquer outra prática ilícita;
g) realizar empréstimos, financiamentos e/ou a contratação de demais produtos e serviços disponibilizados pelo Banco da Amazônia;
h) realizar aplicações financeiras (ex.: fundos de investimento, CDBs, ações);
i) contratar e utilizar cartão de crédito;
j) realizar operações com moeda estrangeira;
k) contratar seguros e/ou previdência e/ou títulos de capitalização;
l) constituir, reforçar ou substituir garantia;
m) identificar, qualificar e registrar intervenientes, avalistas, fiadores, garantidores, coobrigados, arrendadores, locadores e demais participantes de operações de crédito;
n) identificar, qualificar e registrar prestadores de serviços terceirizados;
o) possibilitar avaliações atuariais, financeiras, estatísticas e demais avaliações e usos típicos da atividade bancária;
p) possibilitar o tratamento e uso compartilhado pela administração pública de dados necessários à execução de políticas públicas previstas em leis e regulamentos ou respaldadas em contratos, convênios ou instrumentos congêneres;
q) para cumprimento de obrigações legais e regulatórias.

i. Comprometo-me comunicar o Banco da Amazônia S.A., de imediato e expressamente, as alterações havidas e apresentar os documentos comprobatórios, dentro do prazo de 5 (cinco) dias úteis, contados a partir da data da comunicação feita ao Banco.

ii. Declaro que a omissão quanto à ausência de comunicação de alteração de endereço (localização) perante o Banco da Amazônia S.A., será de minha inteira responsabilidade, respondendo pelo ônus de minha omissão.

iii. Estou ciente que todos os dados coletados são considerados confidenciais pelo Banco da Amazônia S.A., que se compromete a adotar todos os mecanismos e práticas consolidadas de mercado visando sua preservação.

iv. Estou ciente que são considerados "meios eletrônicos", a Internet, os terminais de autoatendimento, o telefone e outros meios de comunicação à distância tornados disponíveis pelo Banco da Amazônia S.A., para fins de relacionamento e operacionalização de produtos e/ou serviços. Estou ciente ainda, para todos os fins, que para a operacionalização de produtos ou serviços, poderão ser utilizados "meios eletrônicos".

v. Estou ciente que durante a operacionalização de produtos e/ou serviços, o Banco da Amazônia S.A., poderá coletar e realizar o tratamento de meus dados biométricos para garantir a prevenção à fraude e a segurança nos processos de identificação e autenticação de cadastro em sistemas eletrônicos, resguardados os direitos mencionados no art. 9º da lei 13.709/2018 e exceto no caso de prevalecerem direitos e liberdades fundamentais que exijam a proteção dos dados pessoais.

vi. Declaro ser exato e verdadeiro o enquadramento do signatário, marcado como sim ou não, no campo 5 do formulário cadastral, quanto à condição de ser ou não Pessoa Exposta Politicamente (PEP), de que trata a Circular BACEN nº 3.978, de 23/01/2020, condição essa que assumo a responsabilidade de manter permanentemente atualizada perante o Banco da Amazônia S.A.

vii. Declaro estar ciente, sob as penas da lei, que o relacionamento objeto da Declaração de Propósito (campo 6 do formulário) se insere na prevenção e combate às atividades relacionadas com os crimes previstos na Lei nº 9.613, de 03.03.1998 (e alterações), a qual dispõe sobre os crimes de "lavagem" ou ocultação de bens, direitos e valores, assim como a utilização do sistema financeiro nacional para os ilícitos previstos nessa Lei."""

    style = ParagraphStyle("dec", fontName="Liberation", fontSize=10, leading=12.5, alignment=TA_JUSTIFY)
    p = Paragraph(texto_dec.replace("\n\n", "<br/><br/>"), style)
    w, h = p.wrap(width - 32*mm, 235*mm)
    p.drawOn(c, 16*mm, y - h)
    footer(3)
    c.showPage()

    # Página 4 (continuação)
    header(6)
    y = height - 18*mm
    texto_cont = """viii. Na condição de cliente com cidadania americana, declaro estar ciente que as informações financeiras estarão sujeitas às exigências determinadas, conforme Instrução Normativa RFB nº 1571, de 02/07/2015 (e alterações), que disciplina a e-Financeira (conjunto de arquivos digitais referentes a cadastro, abertura, fechamento e auxiliares, e pelo módulo de operações financeiras) e Acordo vigente entre a República Federativa do Brasil e República dos Estados Unidos da América para intercâmbio de informações, melhoria da observância tributária e implementação do Foreign Account Tax Compliance Act (FATCA).

ix. Declaro conhecer que o Sistema de Informações de Crédito do Banco Central do Brasil - SCR e o Sicor são bases de dados que contém informações sobre operações de crédito contratadas pelas instituições integrantes do Sistema Financeiro Nacional (SFN), possibilitando que essas Instituições acompanhem as operações de crédito de seus clientes, visando reforçar os mecanismos de supervisão do Banco Central.

x. Estou ciente de que poderei me credenciar junto ao Banco Central do Brasil, via Internet, através do endereço eletrônico www.bcb.gov.br, atendendo às suas exigências, para ter acesso às minhas informações registradas no SCR. Sei também que os dados registrados pelo Banco da Amazônia na base de dados do SCR, somente poderão ser corrigidos mediante minha solicitação formal.

xi. Estou ciente de que, durante meu relacionamento com o Banco da Amazônia S.A., informações e dados pessoais a meu respeito poderão ser consultadas em sistemas públicos e privados, bancos de dados mantidos por terceiros, bureaus e afins, incluindo, mas não se limitando ao próprio SCR e SERASA, bem como o CADIN e Sicor - Sistema de Operações do Crédito Rural e do Proagro, necessários a proteção do crédito e o atendimento às normas regulatórias que poderão delas se utilizar, respeitadas as disposições legais em vigor.

xii. Autorizo o Banco da Amazônia S.A, nos termos do Artigo 12º, da Resolução CMN nº 5.037, de 29/09/2022, a consultar, de forma detalhada ou consolidada, mensalmente ou quando da confecção, atualização ou renovação do cadastro, estudo ou contratação de operações e respectivas renovações inclusive de limite de crédito, todas as informações registradas em meu (nosso) nome, na qualidade de responsável (is) direto (s) ou coobrigado(s), disponibilizadas pelas Instituições Financeiras no Sistema de Informações de Crédito do Banco Central do Brasil - SCR.

xiii. Estou ciente de que o Banco da Amazônia S.A., poderá compartilhar meus dados pessoais coletados e/ou fornecidos, sem prejuízos do compromisso de confidencialidade:
a) com parceiros e prestadores de serviços restringindo-se às funções e atividades por cada um desempenhadas e em aderência às finalidades estabelecidas;
b) com empresas terceirizadas de cobrança extrajudicial, com a finalidade de recuperação de débitos, exceto dados pessoais sensíveis;
c) com entidades de proteção ao crédito, com a finalidade de atender a contratos e acordos firmados pelo Banco no âmbito do sistema de proteção ao crédito, exceto dados pessoais sensíveis;
d) Para a proteção dos interesses do Banco da Amazônia S.A., em caso de conflito, inclusive em demandas judiciais;
e) mediante ordem judicial ou por requerimento de órgãos e/ou autoridades administrativas que detenha competência legal para sua requisição.

xiv. Estou ciente de que o Banco da Amazônia S.A., em aderência as finalidades estabelecidas, poderá realizar TRANSFERÊNCIAS INTERNACIONAIS de meus dados pessoais nos termos estabelecidos pelo capítulo V da Lei nº 13.709/2018 e demais legislações pertinentes para execução contratual.

xv. Estou ciente que o Banco da Amazônia S.A., poderá manter e tratar meus dados pessoais durante todo o período em que eles forem pertinentes ao alcance das finalidades retrocitadas. Exauridas as finalidades de tratamento e decorrido o prazo legal de guarda o Banco da Amazônia procederá com a eliminação e/ou anonimização de meus dados pessoais no âmbito e nos limites técnicos e legais das atividades.

xvi. Estou ciente e de acordo com os termos da Política de Privacidade e Tratamento de Dados Pessoais do Banco da Amazônia S.A. disponibilizada em seu sítio eletrônico no endereço: https://www.bancoamazonia.com.br/index.php/sobre-o-banco/privacidade.

xvii. Estou ciente que posso utilizar o canal de atendimento OUVIDORIA PRIVACIDADE, disponibilizado no sítio institucional do Banco da Amazônia por meio do endereço eletrônico: https://www.bancoamazonia.com.br/index.php/fale-conosco/formulario-ouvidoria-privacidade, para dúvidas, esclarecimentos e/ou exercer direitos relacionados ao tratamento de meus dados pessoais, e que o atendimento para as pessoas com deficiência auditiva ou de fala, será feito"""

    p = Paragraph(texto_cont.replace("\n\n", "<br/><br/>"), style)
    w, h = p.wrap(width - 32*mm, 235*mm)
    p.drawOn(c, 16*mm, y - h)
    footer(5)
    c.showPage()

    # Página 5
    header(3)
    y = height - 18*mm
    texto_final = """exclusivamente através do telefone 0800 721 18 88. Já para pessoas com deficiência visual, será realizado exclusivamente através do telefone 0800 722 2171. O horário de funcionamento dos canais é de Segunda à Sexta (exceto feriados), das 8h às 18h.<br/><br/>

    Considerando que os termos acima expressos estão consentâneos com os dispositivos da Lei 8.078 de 11.09.1990, Resolução nº 3.694, do Conselho Monetário Nacional, de 26.03.2009, Lei 13.709 de 14.08.2018 e demais legislações atinentes as matérias, e como representa a manifestação fiel de sua livre e espontânea vontade, firma este instrumento perante o Banco da Amazônia S.A, para os devidos fins de direito."""

    p = Paragraph(texto_final, style)
    w, h = p.wrap(width - 32*mm, 40*mm)
    p.drawOn(c, 16*mm, y - h)

    y = y - h - 12*mm
    c.setFont("Liberation", 9)
    c.drawCentredString(width/2, y, f"{dados.get('cidade', 'Bom Jardim')} MA, {format_date_br(dados.get('data_declaracao', datetime.now().strftime('%d/%m/%Y')))}")

    y = y - 20*mm
    c.setStrokeColor(black)
    c.setLineWidth(0.6)
    c.line(width/2 - 50*mm, y, width/2 + 50*mm, y)
    c.setFont("Liberation", 10)
    c.drawCentredString(width/2, y - 5*mm, "Assinatura do Cliente (titular dos dados)")

    # Bloco final de menor de idade
    y = y - 15*mm
    texto_bloco_menor = (
        "PREENCHIMENTO NOS CASOS DE CONSENTIMENTO PARA TRATAMENTO DE DADOS PESSOAIS DE CRIANÇA E ADOLESCENTES\n"
        "(preenchimento obrigatório por pelo menos um dos pais ou responsável legal, caso o Titular dos dados seja menor de idade)"
    )

    p_bloco_menor = Paragraph(
        texto_bloco_menor,
        ParagraphStyle("bloco_menor", fontName="Liberation-Bold", fontSize=10, leading=12, alignment=TA_JUSTIFY)
    )

    w_bloco_menor, h_bloco_menor = p_bloco_menor.wrap(width - 32*mm, 20*mm)
    p_bloco_menor.drawOn(c, 16*mm, y - h_bloco_menor)

    y = y - h_bloco_menor - 8*mm
    texto_menor = "Eu, ____________________________________________________, inscrito(a) no CPF nº ____________________, na qualidade de RESPONSÁVEL LEGAL pelo menor de idade identificado neste instrumento, manifesto o meu CONSENTIMENTO livre, informado e inequívoco para que o BANCO DA AMAZÔNIA S.A., realize o tratamento de seus dados pessoais, em atenção à(s) finalidade(s) e demais disposições deste.<br/><br/>Estou ciente sobre a possibilidade de não fornecer ou revogar este CONSENTIMENTO e sobre as consequências da negativa que inviabilizará o relacionamento do menor de idade com o Banco da Amazônia S.A., ressalvada a nomeação de outro representante legalmente habilitado. A revogação do CONSENTIMENTO poderá ser feita por meio do endereço eletrônico: https://www.bancoamazonia.com.br/index.php/fale-conosco/formulario-ouvidoria-privacidade. Vale ressaltar que a revogação do CONSENTIMENTO não exime o Titular dos Dados dos compromissos creditícios e responsabilidades assumidas perante o Banco da Amazônia."
    
    p_menor = Paragraph(texto_menor, ParagraphStyle("menor", fontName="Liberation-Bold", fontSize=10, leading=12, alignment=TA_JUSTIFY))
    w_m, h_m = p_menor.wrap(width - 32*mm, 60*mm)
    p_menor.drawOn(c, 16*mm, y - h_m)

    y = y - h_m - 15*mm
    c.setFont("Liberation", 10)
    c.drawRightString(width - 16*mm, y - 4*mm, "_______________,________de____________de_____________")

    y = y - h_m - 0.5*mm
    c.line(width/2 - 90*mm, y, width/2 + 30*mm, y)
    c.setFont("Liberation", 10)
    c.drawRightString(width - 127*mm, y - 4*mm, "(Pai, Mãe ou Responsável Legal do Titular)")

    footer(5)
    c.save()
    print(f"✓ Gerado: {output_path}")
    return output_path