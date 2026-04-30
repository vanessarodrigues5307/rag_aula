# ==============================
# IMPORTAÇÕES
# ==============================
import os
# Manipulação de arquivos e diretórios
import faiss
# Biblioteca para busca vetorial eficiente (Facebook AI)
import numpy as np
# Operações numéricas (arrays, matrizes)
from sentence_transformers import SentenceTransformer
# Modelo para gerar embeddings de texto
from pypdf import PdfReader
# Leitura de arquivos PDF
# ==============================
# CONFIGURAÇÕES DE CAMINHOS
# ==============================

DATA_PATH = "data/cafe_conhecimento.txt"
# Arquivo TXT com base de conhecimento

DOCS_FOLDER = "documentos"
# Pasta contendo PDFs

INDEX_PATH = "rag/index.faiss"
# Caminho onde o índice vetorial será salvo

DOCS_PATH = "rag/docs.npy"
# Caminho onde os documentos (chunks) serão salvos

# ==============================
# MODELO DE EMBEDDINGS
# ==============================

# Modelo leve e eficiente para gerar vetores semânticos
# Cada texto → vetor numérico que representa significado
model = SentenceTransformer("all-MiniLM-L6-v2")


# ==============================
# FUNÇÃO: DIVIDIR TEXTO EM BLOCOS
# ==============================

def dividir_em_blocos(texto, tamanho=800, sobreposicao=150):
    """
    Divide texto em blocos menores (chunks) com sobreposição.

    Por quê?
    - Modelos têm limite de tokens
    - Evita cortar contexto importante
    - Melhora qualidade da busca (RAG)

    Parâmetros:
    - tamanho: tamanho de cada bloco
    - sobreposicao: quantidade de texto repetido entre blocos
    """

    blocos = []

    # Define o passo do corte (com sobreposição)
    passo = tamanho - sobreposicao

    # Percorre o texto em janelas
    for i in range(0, len(texto), passo):

        # Cria um bloco de texto
        bloco = texto[i:i+tamanho]

        # Ignora blocos vazios
        if bloco.strip():
            blocos.append(bloco.strip())

    return blocos


# ==============================
# FUNÇÃO: EXTRAIR TEXTO DE PDF
# ==============================
def extrair_texto_pdf(caminho):
    """
    Lê um arquivo PDF e extrai todo o texto.
    """
    reader = PdfReader(caminho)
    texto = ""
    # Percorre cada página do PDF
    for pagina in reader.pages:
        # Extrai o texto da página
        conteudo = pagina.extract_text()
        # Verifica se há conteúdo (evita None)
        if conteudo:
            texto += conteudo + "\n"
    return texto

# ==============================
# CARREGAMENTO DE DOCUMENTOS TXT
# ==============================
def load_txt_documents():
    """
    Carrega documentos de um arquivo TXT
    e divide em blocos.
    """
    docs = []
    # Verifica se o arquivo existe
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            texto = f.read()
            # Divide o texto em chunks
            docs.extend(dividir_em_blocos(texto))
    return docs

# ==============================
# CARREGAMENTO DE DOCUMENTOS PDF
# ==============================
def load_pdf_documents():
    """
    Lê todos os PDFs da pasta e transforma em blocos de texto.
    """
    docs = []
    # Se a pasta não existir, retorna vazio
    if not os.path.exists(DOCS_FOLDER):
        return docs
    # Percorre todos os arquivos da pasta
    for arquivo in os.listdir(DOCS_FOLDER):
        # Filtra apenas PDFs
        if arquivo.endswith(".pdf"):
            caminho = os.path.join(DOCS_FOLDER, arquivo)
            print(f"Carregando PDF: {arquivo}")
            # Extrai texto do PDF
            texto = extrair_texto_pdf(caminho)
            # Divide em blocos
            blocos = dividir_em_blocos(texto)
            docs.extend(blocos)
    return docs


# ==============================
# CRIAÇÃO DO VECTORSTORE (FAISS)
# ==============================

def create_vectorstore():
    """
    Cria ou carrega um índice vetorial FAISS.

    Fluxo:
    1. Verifica se já existe índice salvo
    2. Se sim → carrega
    3. Se não → cria novo índice
    """

    # ==============================
    # CARREGAMENTO DO ÍNDICE EXISTENTE
    # ==============================

    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):

        print("Carregando índice FAISS salvo...")

        # Carrega índice FAISS
        index = faiss.read_index(INDEX_PATH)

        # Carrega documentos salvos
        docs = np.load(DOCS_PATH, allow_pickle=True).tolist()

        return index, docs

    # ==============================
    # CRIAÇÃO DE NOVO ÍNDICE
    # ==============================
    print("Criando novo índice vetorial...")
    docs = []
    # Carrega documentos TXT
    docs.extend(load_txt_documents())
    # Carrega documentos PDF
    docs.extend(load_pdf_documents())
    # Se não houver documentos, lança erro
    if not docs:
        raise ValueError("Nenhum documento encontrado para indexação.")
    print("Total de blocos carregados:", len(docs))
    # ==============================
    # GERAÇÃO DE EMBEDDINGS
    # ==============================
    # Converte cada bloco em vetor numérico
    embeddings = model.encode(
        docs,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    # Dimensão dos vetores (ex: 384)
    dimension = embeddings.shape[1]


    # ==============================
    # CRIAÇÃO DO ÍNDICE FAISS
    # ==============================
    # IndexFlatL2 → usa distância euclidiana (L2)
    index = faiss.IndexFlatL2(dimension)
    # Adiciona os embeddings ao índice
    index.add(embeddings)
    # ==============================
    # SALVAMENTO EM DISCO
    # ==============================
    # Salva o índice
    faiss.write_index(index, INDEX_PATH)
    # Salva os documentos
    np.save(DOCS_PATH, docs)
    print("Índice FAISS criado e salvo com sucesso.")
    return index, docs


# ==============================
# FUNÇÃO DE BUSCA (RETRIEVAL)
# ==============================
def retrieve(query, index, docs, top_k=4):
    """
    Retorna os blocos mais relevantes para uma consulta.
    Parâmetros:
    - query: pergunta do usuário
    - index: índice FAISS
    - docs: lista de blocos
    - top_k: quantidade de resultados
    """

    # ==============================
    # EMBEDDING DA CONSULTA
    # ==============================

    query_embedding = model.encode(
        [query],              # lista com uma única pergunta
        convert_to_numpy=True
    )
    # ==============================
    # BUSCA NO FAISS
    # ==============================
    # distances → quão "longe" cada resultado está
    # indices → índices dos documentos mais próximos
    distances, indices = index.search(query_embedding, top_k)


    # ==============================
    # RECUPERA OS TEXTOS
    # ==============================
    resultados = []
    for i in indices[0]:
        # Garante que o índice é válido
        if i < len(docs):
            resultados.append(docs[i])
    return resultados