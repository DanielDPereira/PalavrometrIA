import spacy
from langdetect import detect
from collections import Counter
from .utils import POS_MAP, NER_MAP # Importa o novo mapa NER_MAP

# Carrega os modelos de linguagem
MODELOS = {
    'pt': spacy.load('pt_core_news_sm'),
    'en': spacy.load('en_core_web_sm')
}

def detectar_idioma(texto):
    """Detecta o idioma do texto."""
    try:
        return detect(texto)
    except:
        return 'unknown'

def processar_texto(texto, idioma):
    """Processa o texto com o modelo SpaCy adequado."""
    nlp = MODELOS.get(idioma, MODELOS['en'])
    return nlp(texto)

def estatisticas(doc):
    """Calcula estatísticas básicas do texto processado."""
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
    """Extrai palavras-chave (Substantivos, Nomes Próprios, Verbos)."""
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
    """Conta a frequência de cada classe gramatical (POS)."""
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

# --- NOVA FUNÇÃO ---
def extrair_entidades(doc):
    """Extrai e agrupa as Entidades Nomeadas (NER) do texto."""
    entidades_agrupadas = {}
    
    # Usamos setdefault para criar a lista se a chave (tipo) ainda não existir
    # Usamos um set() para garantir que entidades idênticas não se repitam
    for ent in doc.ents:
        tipo = NER_MAP.get(ent.label_, ent.label_) # Traduz o rótulo
        texto = ent.text.strip()
        if texto:
             entidades_agrupadas.setdefault(tipo, set()).add(texto)
    
    # Converte os sets de volta para listas ordenadas para o JSON
    resultado_final = {tipo: sorted(list(textos)) for tipo, textos in entidades_agrupadas.items()}
    
    # Retorna None se nenhum item foi encontrado, para facilitar no Jinja2
    return resultado_final if resultado_final else None

def tempo_leitura(total_palavras, wpm=130):
    """Calcula o tempo de leitura."""
    minutos = total_palavras / wpm
    return round(minutos, 2)

def grau_legibilidade(texto):
    """Calcula o índice de legibilidade Gulpease (simplificado)."""
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

def frequencia_palavras(doc, top_n=10):
    """Encontra as palavras (lemas) mais frequentes."""
    palavras = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]
    freq = Counter(palavras)
    return freq.most_common(top_n)

def analisar_texto_completo(texto):
    """Função principal que orquestra toda a análise do texto."""
    if not texto.strip():
        return None

    idioma = detectar_idioma(texto)
    doc = processar_texto(texto, idioma)
    
    # Recalcula total de palavras para evitar passar o doc inteiro
    total_palavras_alpha = len([t for t in doc if t.is_alpha])

    resultado = {
        "idioma": idioma,
        "estatisticas": estatisticas(doc),
        "palavras_chave": extrair_palavras_chave(doc, top_n=7),
        "freq_palavras": frequencia_palavras(doc, top_n=10),
        "tipos_palavras": contagem_tipos_palavras(doc),
        "entidades": extrair_entidades(doc), # <-- NOVA LINHA
        "tempo_leitura": tempo_leitura(total_palavras_alpha),
        "legibilidade": grau_legibilidade(texto),
        # Salva apenas um trecho do texto
        "texto": texto[:500] + ("..." if len(texto) > 500 else "") 
    }
    return resultado