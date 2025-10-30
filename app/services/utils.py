import os

UPLOAD_FOLDER = 'app/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# Mapa de tradução das Part-of-Speech (usado em text_processor)
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
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Cria o diretório de uploads se ele não existir."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)