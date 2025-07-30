import os
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

import fitz  # PyMuPDF
import docx
from langdetect import detect
import spacy

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'app/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MODELOS = {
    'pt': spacy.load('pt_core_news_sm'),
    'en': spacy.load('en_core_web_sm')
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
    return {
        "total_palavras": len([t for t in doc if t.is_alpha]),
        "total_frases": len(list(doc.sents)),
        "palavras_unicas": len(set(t.lemma_.lower() for t in doc if t.is_alpha))
    }

from collections import Counter

def extrair_palavras_chave(doc, top_n=7):
    # Lista para armazenar (palavra, tipo)
    palavras_relevantes = []

    for token in doc:
        # Filtro: palavras que são substantivos comuns, próprios ou verbos, sem stopwords e alfabéticas
        if token.pos_ in ["NOUN", "PROPN", "VERB"] and not token.is_stop and token.is_alpha:
            palavras_relevantes.append(token)

    # Contar frequência usando lemma lowercase (para agrupar formas)
    freq = Counter([t.lemma_.lower() for t in palavras_relevantes])

    # Selecionar os tokens únicos ordenados por frequência decrescente
    lemmas_ordenados = [item[0] for item in freq.most_common(top_n)]

    resultado = []
    for lemma in lemmas_ordenados:
        # Procurar token original correspondente para verificar se é nome próprio e manter maiúscula
        token_original = next((t for t in palavras_relevantes if t.lemma_.lower() == lemma), None)
        if token_original:
            if token_original.pos_ == "PROPN":
                # Mantém a forma original com maiúscula inicial
                palavra = token_original.text
            else:
                palavra = lemma.lower()
            resultado.append(palavra)

    return resultado


def contagem_tipos_palavras(doc):
    tipos = {}
    for token in doc:
        pos = token.pos_
        tipos[pos] = tipos.get(pos, 0) + 1
    return tipos

def tempo_leitura(total_palavras, wpm=200):
    minutos = total_palavras / wpm
    return round(minutos, 2)

def grau_legibilidade(texto):
    # Implementa o índice Gulpease simples para PT (exemplo simplificado)
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
