import os
from flask import Blueprint, render_template, request, session, make_response
from werkzeug.utils import secure_filename

# Importa as funções dos novos módulos de 'services'
from .services.utils import UPLOAD_FOLDER, allowed_file
from .services.file_extractor import extrair_texto_url, extrair_texto_arquivo
from .services.text_processor import analisar_texto_completo
from .services.pdf_generator import criar_relatorio_pdf

main = Blueprint('main', __name__)

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
            
        except ValueError as e: # Captura erros da extração de URL/Arquivo
            resultado = {'erro': str(e)}
            return render_template('index.html', resultado=resultado)
        except Exception as e:
            resultado = {'erro': f'Ocorreu um erro inesperado: {e}'}
            return render_template('index.html', resultado=resultado)


        if texto.strip():
            # Chama a função única de análise
            resultado = analisar_texto_completo(texto)
            
            # Salva o resultado na sessão para o PDF
            if resultado:
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
        # Chama a função única de geração de PDF
        pdf_data = criar_relatorio_pdf(resultado)
        
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=PalavrometrIA_Relatorio.pdf'
        
        return response

    except Exception as e:
        return f"Erro ao gerar PDF: {e}", 500