# Site Gerador de Documentos PRONAF

Site web simples para preencher dados do cliente e gerar automaticamente os 4 documentos PDF:

1. Declaração de Atividade  
2. Declaração de Posse Mansa e Pacífica  
3. Declaração de Vizinhança  
4. Ficha Cadastral Pessoa Física (PRONAF)

## Como rodar no seu computador

### 1. Instalar dependências

Abra o terminal na pasta do projeto e rode:

```bash
pip install -r requirements.txt
```

(ou: `pip install flask reportlab`)

### 2. Iniciar o site

```bash
python app.py
```

### 3. Abrir no navegador

Acesse: **http://127.0.0.1:5000**

### 4. Usar

- Preencha o formulário
- Estado Civil: se escolher Casado(a) ou União Estável, os campos do cônjuge aparecem automaticamente
- Cidade da Agência: tem lista pronta + opção de digitar outra
- Clique em **Gerar os 4 Documentos PDF**
- Baixe os arquivos na página de resultado

## Estrutura

```
site_documentos/
├── app.py                 ← Servidor Flask
├── geradores.py           ← Funções que criam os PDFs
├── requirements.txt
├── templates/
│   ├── index.html         ← Formulário
│   └── resultado.html     ← Página de download
├── gerados/               ← PDFs gerados (criada automaticamente)
└── README.md
```

## Observações

- Os layouts da **Declaração de Vizinhança** e da **Ficha Cadastral** ainda podem ser refinados para ficarem ainda mais idênticos aos originais do banco.
- Você pode editar o arquivo `geradores.py` para ajustar posições, textos e formatação.
- Os PDFs ficam salvos na pasta `gerados/` com data/hora no nome do arquivo.

Qualquer dúvida ou ajuste necessário, é só falar!
