import os
from flask import Blueprint, render_template, request, session, make_response
from werkzeug.utils import secure_filename
from fpdf import FPDF 
from datetime import datetime 
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import docx
from langdetect import detect
import spacy
from collections import Counter

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'app/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MODELOS = {
    'pt': spacy.load('pt_core_news_sm'),
    'en': spacy.load('en_core_web_sm')
}

POS_MAP = {
    "ADJ": "Adjetivo",
    "ADP": "Preposição",
    "ADV": "Advérbio",
    "AUX": "Verbo Auxiliar",
    "CONJ": "Conjunção",
    "CCONJ": "Conjunção Coordenativa",
    "DET": "Determinante",
    "INTJ": "Interjeição",
    "NOUN": "Substantivo",
    "NUM": "Número",
    "PART": "Partícula",
    "PRON": "Pronome",
    "PROPN": "Nome Próprio",
    "PUNCT": "Pontuação",
    "SCONJ": "Conjunção Subordinativa",
    "SYM": "Símbolo",
    "VERB": "Verbo",
    "X": "Outro",
    "_": "Desconhecido"
}

# CLASSE HELPER PARA O PDF (pyfpdf lida com UTF-8)
class PDF(FPDF):
    def header(self):
        # Arial bold 14
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'PalavrometrIA - Relatório de Análise', 0, 1, 'C')
        # Arial regular 9
        self.set_font('Arial', '', 9)
        self.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240) # Fundo cinza claro
        self.cell(0, 7, title, 0, 1, 'L', 1)
        self.ln(4)

    def add_key_value(self, key, value):
        key_col_width = 70 # Largura da coluna da chave
        self.set_font('Arial', 'B', 10)
        self.cell(key_col_width, 6, key)
        self.set_font('Arial', '', 10)
        # multi_cell para o valor, caso quebre a linha
        self.multi_cell(0, 6, str(value)) 
        self.ln(2) # Espaçamento menor após kv

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detectar_idioma(texto):
    try:
        return detect(texto)
    except:
        return 'unknown'

def processar_texto(texto, idioma):
    nlp = MODELOS.get(idioma, MODELOS['en'])
    return nlp(texto)

def estatisticas(doc):
    total_palavras = len([t for t in doc if t.is_alpha])
    total_frases = len(list(doc.sents))
    palavras_unicas = len(set(t.lemma_.lower() for t in doc if t.is_alpha))
    media_palavras_por_frase = round(total_palavras / total_frases, 2) if total_frases else 0
    tamanho_medio_palavra = round(
        sum(len(t.text) for t in doc if t.is_alpha) / total_palavras, 2
    ) if total_palavras else 0
    return {
        "total_palavras": total_palavras,
        "total_frases": total_frases,
        "palavras_unicas": palavras_unicas,
        "media_palavras_por_frase": media_palavras_por_frase,
        "tamanho_medio_palavra": tamanho_medio_palavra
    }

def extrair_palavras_chave(doc, top_n=7):
    palavras_relevantes = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN", "VERB"] and not token.is_stop and token.is_alpha:
            palavras_relevantes.append(token)
    freq = Counter([t.lemma_.lower() for t in palavras_relevantes])
    lemmas_ordenados = [item[0] for item in freq.most_common(top_n)]
    resultado = []
    for lemma in lemmas_ordenados:
        token_original = next((t for t in palavras_relevantes if t.lemma_.lower() == lemma), None)
        if token_original:
            if token_original.pos_ == "PROPN":
                palavra = token_original.text
            else:
                palavra = lemma.lower()
            resultado.append(palavra)
    return resultado

def contagem_tipos_palavras(doc):
    tipos = {}
    for token in doc:
        if token.is_space:
            continue  # remove espaços
        pos = token.pos_
        tipos[pos] = tipos.get(pos, 0) + 1
    tipos_traduzidos = {}
    for k, v in tipos.items():
        nome = POS_MAP.get(k, k)
        tipos_traduzidos[nome] = v
    return tipos_traduzidos

def tempo_leitura(total_palavras, wpm=130):
    minutos = total_palavras / wpm
    return round(minutos, 2)

def grau_legibilidade(texto):
    letras = sum(c.isalpha() for c in texto)
    palavras = len(texto.split())
    frases = texto.count('.') + texto.count('!') + texto.count('?')
    if palavras == 0 or frases == 0:
        return "Indefinido"
    gulpease = 89 + (300 * frases - 10 * letras) / palavras
    if gulpease >= 80:
        return "Fácil"
    elif gulpease >= 60:
        return "Médio"
    else:
        return "Difícil"

def extrair_texto_arquivo(path, ext):
    if ext == 'txt':
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == 'pdf':
        doc = fitz.open(path)
        texto = ""
        for page in doc:
            texto += page.get_text()
        return texto
    elif ext == 'docx':
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

def frequencia_palavras(doc, top_n=10):
    palavras = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
    freq = Counter(palavras)
    return freq.most_common(top_n)

def extrair_texto_url(url):
    try:
        # Adiciona um User-Agent para simular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Lança erro para status ruins (4xx, 5xx)

        # Usa BeautifulSoup para extrair o texto de forma limpa
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove tags de script e style
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Pega o texto do body, remove espaços extras e junta
        texto = ' '.join(soup.body.stripped_strings)
        return texto
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar URL: {e}")
        raise ValueError(f"Não foi possível acessar a URL. Verifique o link ou a conexão.")
    except Exception as e:
        print(f"Erro ao processar HTML: {e}")
        raise ValueError("Ocorreu um erro ao processar o conteúdo da página.")

@main.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    texto = ""

    if request.method == 'GET':
        session.pop('resultado', None)

    if request.method == 'POST':
        session.pop('resultado', None)
        
        try:
            if 'texto' in request.form and request.form['texto'].strip():
                texto = request.form['texto']
            
            elif 'url' in request.form and request.form['url'].strip():
                url = request.form['url']
                texto = extrair_texto_url(url)
            
            # LÓGICA DE ARQUIVO
            elif 'arquivo' in request.files and request.files['arquivo'].filename != '':
                file = request.files['arquivo']
                if file and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    texto = extrair_texto_arquivo(filepath, ext)
                else:
                    resultado = {'erro': 'Formato de arquivo inválido.'}
                    return render_template('index.html', resultado=resultado)
            
        except ValueError as e: # Captura erros da extração de URL
            resultado = {'erro': str(e)}
            return render_template('index.html', resultado=resultado)

        if texto.strip():
            idioma = detectar_idioma(texto)
            doc = processar_texto(texto, idioma)

            freq_palavras = frequencia_palavras(doc)

            resultado = {
                "idioma": idioma,
                "estatisticas": estatisticas(doc),
                "palavras_chave": extrair_palavras_chave(doc, top_n=7),
                "freq_palavras": freq_palavras,
                "tipos_palavras": contagem_tipos_palavras(doc),
                "tempo_leitura": tempo_leitura(len([t for t in doc if t.is_alpha])),
                "legibilidade": grau_legibilidade(texto),
                # Não salvar o texto inteiro na sessão, apenas um trecho
                "texto": texto[:500] + ("..." if len(texto) > 500 else "") 
            }
            
            # Salva o resultado na sessão para o PDF
            session['resultado'] = resultado
        
        # Se houver erro, não salva na sessão
        if resultado and 'erro' in resultado:
            session.pop('resultado', None)

    return render_template('index.html', resultado=resultado)


# ROTA PARA EXPORTAR PDF
@main.route('/exportar-pdf')
def exportar_pdf():
    resultado = session.get('resultado')

    if not resultado:
        return "Nenhum resultado para exportar. Por favor, faça uma análise primeiro.", 404
    
    try:
        pdf = PDF()
        pdf.add_page()
        
        # --- Seção 1: Resumo ---
        pdf.chapter_title('Resumo da Análise')
        pdf.add_key_value('Idioma Detectado:', resultado['idioma'])
        pdf.add_key_value('Tempo de Leitura (130 PPM):', f"{resultado['tempo_leitura']} min")
        pdf.add_key_value('Grau de Legibilidade:', resultado['legibilidade'])
        pdf.ln(5)

        # --- Seção 2: Estatísticas Principais ---
        pdf.chapter_title('Estatísticas do Texto')
        stats = resultado['estatisticas']
        pdf.add_key_value('Total de palavras:', stats['total_palavras'])
        pdf.add_key_value('Total de frases:', stats['total_frases'])
        pdf.add_key_value('Palavras únicas (lemas):', stats['palavras_unicas'])
        pdf.add_key_value('Média de palavras/frase:', stats['media_palavras_por_frase'])
        pdf.add_key_value('Tamanho médio/palavra:', stats['tamanho_medio_palavra'])
        pdf.ln(5)

        # --- Seção 3: Conteúdo ---
        pdf.chapter_title('Conteúdo Principal')
        
        # Palavras-chave
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'Palavras-chave Principais:', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, ", ".join(resultado['palavras_chave']))
        pdf.ln(4)

        # Palavras Frequentes (Tabela)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, '10 Palavras Mais Frequentes:', 0, 1)
        
        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(60, 7, 'Palavra', 1, 0, 'C')
        pdf.cell(30, 7, 'Frequência', 1, 1, 'C')

        # Dados da tabela
        pdf.set_font('Arial', '', 10)
        for palavra, freq in resultado['freq_palavras']:
            pdf.cell(60, 6, palavra, 1)
            pdf.cell(30, 6, str(freq), 1, 1, 'C')
        pdf.ln(5)
        
        # --- Seção 4: Tipos de Palavras (Tabela) ---
        pdf.chapter_title('Contagem por Tipo de Palavra')
        
        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(60, 7, 'Tipo Gramatical', 1, 0, 'C')
        pdf.cell(30, 7, 'Quantidade', 1, 1, 'C')
        
        # Dados da tabela
        pdf.set_font('Arial', '', 10)
        for tipo, qtd in sorted(resultado['tipos_palavras'].items(), key=lambda item: item[1], reverse=True):
            pdf.cell(60, 6, tipo, 1)
            pdf.cell(30, 6, str(qtd), 1, 1, 'C')
        pdf.ln(5)

        # --- Geração da Resposta ---
        pdf_data = pdf.output(dest='S').encode('latin-1')
        
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=PalavrometrIA_Relatorio.pdf'
        
        return response

    except Exception as e:
        return f"Erro ao gerar PDF: {e}", 500