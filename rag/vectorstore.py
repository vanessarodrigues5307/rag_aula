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
import hashlib
import json
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

META_PATH = "rag/meta.json"
# Caminho onde os metadados serão salvos

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
# FUNÇÕES DE HASH E METADADOS
# ==============================

def compute_file_hash(caminho):
    hasher = hashlib.sha256()
    with open(caminho, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_source_hash():
    arquivos = []
    if os.path.exists(DATA_PATH):
        arquivos.append(DATA_PATH)
    if os.path.exists(DOCS_FOLDER):
        for arquivo in sorted(os.listdir(DOCS_FOLDER)):
            if arquivo.lower().endswith('.pdf'):
                arquivos.append(os.path.join(DOCS_FOLDER, arquivo))

    hasher = hashlib.sha256()
    for caminho in arquivos:
        hasher.update(compute_file_hash(caminho).encode('utf-8'))
    return hasher.hexdigest()


def load_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_meta(meta):
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ==============================
# CRIAÇÃO DO VECTORSTORE (FAISS)
# ==============================

def create_vectorstore():
    """
    Cria ou carrega um índice vetorial FAISS.

    Fluxo:
    1. Verifica se já existe índice salvo e se as fontes não mudaram
    2. Se sim → carrega
    3. Se não → cria novo índice
    """

    source_hash = compute_source_hash()
    meta = load_meta()

    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH) and meta.get('source_hash') == source_hash:
        print("Carregando índice FAISS salvo...")
        index = faiss.read_index(INDEX_PATH)
        docs = np.load(DOCS_PATH, allow_pickle=True).tolist()
        return index, docs

    if os.path.exists(INDEX_PATH) or os.path.exists(DOCS_PATH):
        print("Fonte alterada ou índice desatualizado. Recriando índice FAISS...")

    # ==============================
    # CRIAÇÃO DE NOVO ÍNDICE
    # ==============================
    docs = []
    docs.extend(load_txt_documents())
    docs.extend(load_pdf_documents())

    if not docs:
        raise ValueError("Nenhum documento encontrado para indexação.")

    print("Total de blocos carregados:", len(docs))

    # ==============================
    # GERAÇÃO DE EMBEDDINGS
    # ==============================
    embeddings = model.encode(
        docs,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    dimension = embeddings.shape[1]

    # ==============================
    # CRIAÇÃO DO ÍNDICE FAISS
    # ==============================
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # ==============================
    # SALVAMENTO EM DISCO
    # ==============================
    faiss.write_index(index, INDEX_PATH)
    np.save(DOCS_PATH, docs)
    save_meta({'source_hash': source_hash})
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