import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import docx

def extrair_texto_url(url):
    """Extrai texto limpo de uma URL."""
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

def extrair_texto_arquivo(path, ext):
    """Extrai texto de arquivos .txt, .pdf ou .docx."""
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