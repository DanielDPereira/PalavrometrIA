from fpdf import FPDF
from datetime import datetime

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

def criar_relatorio_pdf(resultado):
    """Gera o relatório em PDF com base nos dados da análise."""
    try:
        pdf = PDF()
        pdf.add_page()
        
        # --- Seção 1: Resumo ---
        pdf.chapter_title('Resumo da Análise')
        pdf.add_key_value('Idioma Detectado:', resultado.get('idioma', 'N/A'))
        pdf.add_key_value('Tempo de Leitura (130 PPM):', f"{resultado.get('tempo_leitura', 0)} min")
        pdf.add_key_value('Grau de Legibilidade:', resultado.get('legibilidade', 'N/A'))
        pdf.ln(5)

        # --- Seção 2: Estatísticas Principais ---
        pdf.chapter_title('Estatísticas do Texto')
        stats = resultado.get('estatisticas', {})
        pdf.add_key_value('Total de palavras:', stats.get('total_palavras', 0))
        pdf.add_key_value('Total de frases:', stats.get('total_frases', 0))
        pdf.add_key_value('Palavras únicas (lemas):', stats.get('palavras_unicas', 0))
        pdf.add_key_value('Média de palavras/frase:', stats.get('media_palavras_por_frase', 0))
        pdf.add_key_value('Tamanho médio/palavra:', stats.get('tamanho_medio_palavra', 0))
        pdf.ln(5)

        # --- Seção 3: Conteúdo ---
        pdf.chapter_title('Conteúdo Principal')
        
        # Palavras-chave
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'Palavras-chave Principais:', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, ", ".join(resultado.get('palavras_chave', [])))
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
        for palavra, freq in resultado.get('freq_palavras', []):
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
        tipos_palavras = resultado.get('tipos_palavras', {})
        for tipo, qtd in sorted(tipos_palavras.items(), key=lambda item: item[1], reverse=True):
            pdf.cell(60, 6, tipo, 1)
            pdf.cell(30, 6, str(qtd), 1, 1, 'C')
        pdf.ln(5)

        # --- Geração da Resposta ---
        # Retorna os dados do PDF em bytes
        return pdf.output(dest='S').encode('latin-1')

    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        raise