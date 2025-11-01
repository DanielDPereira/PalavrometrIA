# PalavrometrIA

[](https://opensource.org/licenses/MIT)

Analisador web inteligente para extração de estatísticas, semântica e métricas de texto.

O PalavrometrIA é uma ferramenta web robusta projetada para analisar textos de múltiplas fontes. Seja colando um texto, fornecendo uma URL ou carregando um arquivo (`.txt`, `.pdf`, `.docx`), a aplicação processa o conteúdo e retorna um relatório detalhado com métricas linguísticas, análise semântica e visualizações de dados.

## Prévia

<img src="PalavrometrIA GIF.gif">

## Índice

1.  [Objetivo](#1-objetivo)
2.  [O Problema que Resolve](#2-o-problema-que-resolve)
3.  [Funcionalidades Principais](#3-funcionalidades-principais)
4.  [Aplicações Práticas](#4-aplicações-práticas)
5.  [Métodos e Fórmulas (Como Funciona)](#5-métodos-e-fórmulas-como-funciona)
6.  [Tecnologias Utilizadas](#6-tecnologias-utilizadas)
7.  [Manual de Instalação](#7-manual-de-instalação)
8.  [Como Usar](#8-como-usar)
9.  [Como Contribuir](#9-como-contribuir)
10. [Licença](#10-licença)
11. [Créditos](#11-créditos)

-----

### 1\. Objetivo

O objetivo central do PalavrometrIA é democratizar a análise de texto. A ferramenta fornece insights complexos de Processamento de Linguagem Natural (PLN) de forma acessível e visual, permitindo que usuários, independentemente de seu conhecimento técnico, possam entender profundamente a estrutura, o conteúdo e a complexidade de um documento.

### 2\. O Problema que Resolve

A análise manual de textos para extrair métricas, identificar temas ou avaliar a complexidade é um processo lento, subjetivo e suscetível a erros. O PalavrometrIA resolve isso ao:

  * **Automatizar** a coleta de métricas estatísticas (contagem de palavras, frases, etc.).
  * **Quantificar** aspectos subjetivos como "legibilidade" e "tempo de leitura".
  * **Extrair** informações semânticas chave, como palavras-chave e entidades nomeadas (pessoas, locais, organizações).
  * **Centralizar** a análise, aceitando diferentes formatos de entrada (texto, URL, arquivos) em um único lugar.

### 3\. Funcionalidades Principais

O PalavrometrIA oferece um dashboard de resultados completo, incluindo:

  * **Múltiplas Fontes de Entrada:** Aceita texto colado, URLs de páginas web ou upload de arquivos (`.txt`, `.pdf`, `.docx`).
  * **Detecção de Idioma:** Identifica automaticamente o idioma do texto (suportando português e inglês para processamento).
  * **Estatísticas Detalhadas:** Informa o total de palavras, frases, palavras únicas (lemas), média de palavras por frase e tamanho médio das palavras.
  * **Métricas de Leitura:** Calcula o tempo estimado de leitura (baseado em 130 PPM) e o grau de legibilidade (Fácil, Médio, Difícil).
  * **Análise de Frequência:** Exibe um gráfico de barras com as 10 palavras (lemas) mais frequentes no texto, desconsiderando *stopwords*.
  * **Classes Gramaticais (POS):** Apresenta uma lista e um gráfico de pizza (Doughnut) distribuindo as palavras por suas classes gramaticais (Substantivo, Verbo, Adjetivo, etc.).
  * **Extração de Palavras-chave:** Identifica e exibe as 7 palavras mais relevantes (substantivos, nomes próprios e verbos) que representam o núcleo do texto.
  * **Reconhecimento de Entidades (NER):** Localiza e agrupa entidades nomeadas como Pessoas (PER), Locais (LOC), Organizações (ORG) e mais.
  * **Exportação de Relatório:** Permite ao usuário exportar o relatório completo da análise para um arquivo PDF.
  * **Interface Moderna:** Design responsivo com suporte a modo claro (Light) e escuro (Dark).

### 4\. Aplicações Práticas

  * **Estudantes e Pesquisadores:** Para rapidamente avaliar a complexidade de artigos, extrair palavras-chave para revisão bibliográfica e identificar as principais entidades em um documento.
  * **Redatores e Criadores de Conteúdo:** Para otimizar textos para SEO (identificando palavras-chave), ajustar o tom (verificando a legibilidade) e garantir que o tempo de leitura esteja adequado ao público-alvo.
  * **Editores e Revisor:** Para padronizar a complexidade de textos, verificar a densidade de palavras e obter uma visão geral rápida do conteúdo antes da revisão.
  * **Analistas de Dados e Negócios:** Para extrair rapidamente nomes de pessoas, organizações ou produtos de relatórios não estruturados.

### 5\. Métodos e Fórmulas (Como Funciona)

A aplicação utiliza uma pipeline de serviços para processar o texto:

1.  **Extração de Texto:**

      * **URL:** Utiliza `requests` para buscar o HTML e `BeautifulSoup` para parsear e extrair o texto limpo do `<body>`, removendo tags `<script>` e `<style>`.
      * **Arquivos:** Utiliza `PyMuPDF` (fitz) para extrair texto de arquivos `.pdf`, `python-docx` para `.docx` e leitura padrão para `.txt`.

2.  **Processamento de NLP (via `SpaCy`):**
    O texto extraído é passado para a função `analisar_texto_completo`.

      * O idioma é detectado com `langdetect`.
      * Um modelo SpaCy (`pt_core_news_sm` ou `en_core_web_sm`) é carregado.
      * O SpaCy tokeniza o texto e gera um documento (`doc`) que contém a análise de *tokens*, *lemas*, *POS tags* e *NER*.

3.  **Cálculo de Métricas:**

      * **Tempo de Leitura:** A fórmula utilizada é uma média padrão de mercado:
        ```
        Minutos = Total de Palavras / 130 PPM (Palavras Por Minuto)
        ```
      * **Grau de Legibilidade (Índice Gulpease):** O projeto utiliza uma implementação simplificada do índice Gulpease, adaptado para o português:
        ```
        Gulpease = 89 + (300 * Total de Frases - 10 * Total de Letras) / Total de Palavras
        ```
          * `>= 80`: Fácil
          * `>= 60`: Médio
          * `< 60`: Difícil

4.  **Geração do Relatório PDF:**

      * Quando o usuário solicita a exportação, os dados salvos na sessão são usados.
      * A biblioteca `FPDF` é utilizada para construir um documento PDF estruturado, adicionando títulos, tabelas (para palavras frequentes e tipos de palavras) e listas (para estatísticas e entidades).

### 6\. Tecnologias Utilizadas

| Categoria | Tecnologia | Propósito |
| :--- | :--- | :--- |
| **Backend** | `Python` | Linguagem principal do projeto. |
| | `Flask` | Micro-framework web para servir a aplicação e gerenciar rotas. |
| **NLP** | `SpaCy` | Biblioteca principal para tokenização, lematização, POS-tagging e NER. |
| | `langdetect` | Para detecção do idioma do texto. |
| **Extração** | `PyMuPDF (fitz)` | Extração de texto de arquivos `.pdf`. |
| | `python-docx` | Extração de texto de arquivos `.docx`. |
| | `BeautifulSoup4` | Parseamento de HTML para extração de texto de URLs. |
| | `Requests` | Realização de requisições HTTP para buscar conteúdo de URLs. |
| **Frontend** | `HTML5` | Estrutura da página web. |
| | `CSS3` | Estilização, layout responsivo e temas (light/dark). |
| | `JavaScript (ES6+)` | Manipulação do DOM, lógica da UI (loader, inputs) e temas. |
| | `Chart.js` | Renderização dos gráficos de barra e pizza. |
| **Relatórios** | `FPDF` | Geração dinâmica de relatórios em formato `.pdf`. |

### 7\. Manual de Instalação

1.  **Clone o Repositório:**

    ```bash
    git clone https://github.com/DanielDPereira/PalavrometrIA.git
    cd PalavrometrIA
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**

    ```bash
    # Use python3 ou python, dependendo da sua instalação
    python3 -m venv venv
    ```

3.  **Ative o Ambiente Virtual:**

    ```bash
    # No Linux/macOS
    source venv/bin/activate

    # No Windows
    .\venv\Scripts\activate
    ```

4.  **Instale as Dependências:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Baixe os Modelos SpaCy:**
    Estes modelos são *necessários* para a análise em PT e EN.

    ```bash
    python -m spacy download pt_core_news_sm
    python -m spacy download en_core_web_sm
    ```

6.  **Execute a Aplicação:**

    ```bash
    python run.py
    ```

7.  **Acesse no Navegador:**
    Acesse `http://localhost:5000` (ou `http://127.0.0.1:5000/`) e comece a usar.

### 8\. Como Usar

A interface do PalavrometrIA é dividida em três métodos de entrada:

1.  **Colar Texto:** Simplesmente cole o texto que deseja analisar na área de texto principal.
2.  **Inserir URL:** Cole o link completo (`http://` ou `https://`) da página web da qual deseja extrair e analisar o texto.
3.  **Escolher Arquivo:** Clique no botão "Escolher arquivo" e selecione um documento `.txt`, `.pdf` ou `.docx` do seu computador.

Após fornecer a entrada em *apenas um* desses campos, clique no botão **"Analisar"**.

Aguarde o processamento e os resultados aparecerão abaixo do formulário. Se desejar salvar os resultados, clique no botão **"Exportar Relatório em PDF"** no final da página de resultados.

### 9\. Como Contribuir

Contribuições são bem-vindas\! Se você tem ideias para novas funcionalidades, melhorias na performance de NLP ou correções de bugs:

1.  Faça um *fork* deste repositório.
2.  Crie uma nova *branch* (`git checkout -b feature/minha-feature`).
3.  Faça o *commit* de suas mudanças (`git commit -m 'Adiciona nova feature'`).
4.  Faça o *push* para a *branch* (`git push origin feature/minha-feature`).
5.  Abra um *Pull Request*.

### 10\. Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

### 11\. Créditos

Este projeto foi criado e é mantido por **Daniel Dias Pereira**.
