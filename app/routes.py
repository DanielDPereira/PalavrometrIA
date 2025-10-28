import os
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

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

@main.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    texto = ""

    if request.method == 'POST':
        if 'texto' in request.form and request.form['texto'].strip():
            texto = request.form['texto']
        elif 'arquivo' in request.files:
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
                "texto": texto
            }

    return render_template('index.html', resultado=resultado)
 
