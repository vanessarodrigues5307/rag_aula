# MetricaIA - Assistente Inteligente de Métricas de Software

## 📋 O que é o MetricaIA?

**MetricaIA** é um assistente inteligente especializado em **Métricas e Medição de Software**. Ele usa a técnica de **Retrieval-Augmented Generation (RAG)** combinada com um modelo de linguagem (Ollama) para responder perguntas sobre métricas de software, qualidade e medição.

### Objetivo Principal
Apoiar estudantes, profissionais e pesquisadores com informações técnicas sobre:
- Métricas de processo (Velocity, Lead Time, Cycle Time)
- Métricas de código (Complexidade, Cobertura de Testes, Duplicação)
- Métricas de qualidade (Defeitos, Confiabilidade, Manutenibilidade)
- Padrões internacionais (ISO/IEC 25010, CMMI, GQM, Six Sigma)

---

## 🏗️ Estrutura do Projeto

```
rag_aula/
├── app.py                    # Aplicação Flask principal
├── requirements.txt          # Dependências do projeto
├── README.md                 # Este arquivo
├── test_connection.py        # Script para testar conexão com Ollama e vectorstore
│
├── rag/                      # Pasta do sistema RAG (Retrieval-Augmented Generation)
│   ├── vectorstore.py        # Cria e gerencia índice FAISS de busca vetorial
│   ├── llm.py                # Integração com Ollama para geração de respostas
│   ├── index.faiss           # Índice vetorial pré-computado (gerado automaticamente)
│   ├── docs.npy              # Documentos em array numpy (gerado automaticamente)
│   └── meta.json             # Metadados para detectar mudanças (gerado automaticamente)
│
├── data/                     # Pasta com dados de conhecimento
│   └── cafe_conhecimento.txt # Base de conhecimento em texto sobre métricas
│
├── documentos/               # Pasta com PDFs
│   ├── cafe_conhecimento.pdf          # PDF sobre métricas gerais
│   ├── metricas_loc.pdf                # PDF detalhado sobre LOC
│   ├── pontos_de_funcao.pdf            # PDF detalhado sobre Pontos de Função
│   └── metricas_qualidade_e_complexidade.pdf # PDF sobre qualidade e complexidade
│
├── templates/                # Pasta com páginas HTML do frontend
│   ├── base.html             # Layout base (header, menu, footer)
│   ├── index.html            # Aba "Sobre" - explicação do sistema
│   ├── chat.html             # Aba "Chat" - interface de chat com IA
│   ├── recursos.html         # Aba "Recursos" - referências e links
│   └── sobre.html            # Página antiga (não usada)
│
├── static/                   # Pasta com arquivos CSS
│   └── style.css             # Estilos do site (cores azuis, layout responsivo)
│
└── venv/                     # Ambiente virtual Python (não commitado)
```

---

## 🔧 Como Funciona

### Fluxo da Aplicação

1. **Usuário abre `/chat`** → Página com interface de chat
2. **Usuário digita pergunta** → Enviada para backend via `/ask`
3. **Backend processa**:
   - Busca documentos relevantes no índice FAISS (`vectorstore.py`)
   - Monta um prompt contextualizado (`llm.py`)
   - Envia para Ollama gerar resposta em streaming
4. **Resposta retorna** → Exibida no chat em tempo real

---

## 📁 Detalhamento das Pastas

### `/rag` - Motor de Busca e IA

Esta pasta contém o coração do sistema RAG:

#### `vectorstore.py`
**Para que serve:** Cria e gerencia o índice FAISS para busca semântica rápida.

**Por que assim:**
- Converte documentos em vetores numéricos (embeddings)
- FAISS indexa esses vetores para busca O(log n) eficiente
- Detecta mudanças nos PDFs e reindexá automaticamente
- Salva índice em disco para não recomputar a cada execução

**Funções principais:**
- `create_vectorstore()` - Cria ou carrega índice
- `retrieve(query, index, docs, top_k=4)` - Busca documentos similares à pergunta
- `compute_source_hash()` - Detecta mudanças em PDFs

#### `llm.py`
**Para que serve:** Gerencia comunicação com modelo Ollama e construção de prompts.

**Por que assim:**
- Define o "personagem" da IA (especialista em métricas)
- Monta o contexto (documentos relevantes + pergunta do usuário)
- Envia para Ollama e retorna resposta em streaming (não bloqueia UI)

**Funções principais:**
- `montar_prompt()` - Constrói prompt contextualizado
- `gerar_resposta_stream()` - Chama Ollama e retorna streaming

#### Arquivos gerados automaticamente
- `index.faiss` - Índice de busca binário (gerado uma vez)
- `docs.npy` - Array numpy com 4 documentos mais similares (gerado uma vez)
- `meta.json` - Hash dos PDFs (para detectar mudanças)

---

### `/data` - Base de Conhecimento em Texto

#### `cafe_conhecimento.txt`
**Para que serve:** Primeira fonte de conhecimento em texto simples.

**Por que assim:**
- Fácil de editar (é um arquivo .txt)
- O sistema lê e divide em blocos de ~800 caracteres
- Indexa cada bloco para busca vetorial

**Conteúdo:**
- Introdução a métricas
- Classificação de métricas
- Métricas de processo, código, qualidade
- Frameworks (GQM, ISO/IEC 25010, CMMI, Six Sigma)
- Estudos de caso

---

### `/documentos` - PDFs com Conteúdo Detalhado

**Para que serve:** Fornecer conteúdo mais aprofundado que é indexado pelo sistema.

**Por que assim:**
- PDFs são convertidos em texto via `pypdf`
- Divididos em blocos (chunks) como o TXT
- Todos os blocos são indexados no FAISS

**Arquivos:**
1. `cafe_conhecimento.pdf` - Métricas gerais
2. `metricas_loc.pdf` - Lines of Code em detalhes
3. `pontos_de_funcao.pdf` - Function Points (Albrecht, IFPUG)
4. `metricas_qualidade_e_complexidade.pdf` - Qualidade, cobertura, confiabilidade

---

### `/templates` - Frontend HTML

Todas as páginas herdam de `base.html` que fornece:
- Header com título "MetricaIA"
- Navegação com 3 abas
- Footer com copyright
- CSS global

#### `index.html` - Aba "Sobre"
- Explica o sistema
- Lista funcionalidades
- Botão "Ir para o Chat"

#### `chat.html` - Aba "Chat"
- Caixa de chat (histórico de mensagens)
- Textarea para digitar pergunta
- Botões "Enviar" e "Limpar Histórico"
- JavaScript para:
  - Enviar pergunta ao servidor
  - Receber resposta em streaming
  - Salvar histórico no localStorage
  - Animar indicador "digitando..."

#### `recursos.html` - Aba "Recursos"
- Livros recomendados
- Padrões e normas (ISO/IEC 25010, CMMI, GQM, Six Sigma)
- Tipos de métricas comuns
- Dicas para começar
- Links úteis

#### `sobre.html` - Página antiga
Não usada (substituída por `index.html`). Fica aqui por compatibilidade.

---

### `/static` - CSS

#### `style.css`
**Para que serve:** Estilizar toda a interface do site.

**Por que assim:**
- Paleta azul (#0066cc) para software (antes era verde de café)
- Layout responsivo com Flexbox
- Classes para diferentes elementos (`.msg`, `.chat-box`, `.btn-chat`, etc.)

**Principais estilos:**
- Header com gradient azul
- Chat com mensagens do usuário à direita, IA à esquerda
- Animação de "digitando..." com 3 pontos
- Responsivo para mobile (media queries)

---

## 🚀 Arquivos Principais

### `app.py` - Aplicação Flask

**Para que serve:** API REST que conecta frontend com RAG.

**Rotas:**
```python
@app.route("/")           # Aba "Sobre"
@app.route("/chat")       # Aba "Chat" interativo
@app.route("/recursos")   # Aba "Recursos"
@app.route("/ask", methods=["POST"])  # Recebe pergunta, retorna resposta em streaming
```

**Por que Flask:**
- Leve e simples
- Suporta streaming de respostas
- Fácil integração com templates Jinja2

---

### `requirements.txt` - Dependências

```
Flask==3.1.3              # Web framework
faiss-cpu==1.13.2         # Busca vetorial
langchain==1.2.13         # Orquestração de LLM
sentence-transformers     # Geração de embeddings
pypdf                     # Leitura de PDFs
requests==2.32.5          # Chamadas HTTP para Ollama
numpy                     # Arrays e computação
```

**Por que cada uma:**
- **Flask**: Serve as páginas HTML e API
- **FAISS**: Busca semântica rápida em vetores
- **Langchain**: Integração com LLMs
- **sentence-transformers**: Converte texto em vetores (all-MiniLM-L6-v2)
- **pypdf**: Extrai texto de PDFs
- **requests**: Comunica com Ollama
- **numpy**: Armazena documentos como arrays

---

### `test_connection.py` - Diagnóstico

**Para que serve:** Testar se tudo está configurado corretamente.

**Testa:**
1. ✅ Ollama está rodando em `http://localhost:11434`
2. ✅ Modelo `llama3:8b` está instalado
3. ✅ Vectorstore carrega com sucesso
4. ✅ Sistema consegue gerar uma resposta

**Como usar:**
```bash
python test_connection.py
```

---

## 🔄 Fluxo de Dados - Exemplo Prático

### Usuário pergunta: "O que é Velocity?"

1. **Frontend** (`chat.html` - JavaScript)
   - Captura texto "O que é Velocity?"
   - Envia POST para `/ask` com JSON: `{"question": "O que é Velocity?"}`

2. **Backend** (`app.py` - rota `/ask`)
   - Recebe pergunta
   - Chama `retrieve()` com o índice FAISS
   - Busca 4 documentos mais similares (que mencionam "velocity")

3. **Busca Vetorial** (`vectorstore.py`)
   - Converte "O que é Velocity?" em embedding com `all-MiniLM-L6-v2`
   - Busca no índice FAISS os 4 documentos mais próximos
   - Retorna trechos como: "Velocity: quantidade de trabalho..."

4. **Prompt** (`llm.py`)
   ```
   Você é um assistente especializado em Métricas de Software...
   
   Contexto RAG:
   [4 trechos dos PDFs sobre velocity]
   
   Pergunta: O que é Velocity?
   ```

5. **Ollama** (modelo llama3:8b)
   - Recebe prompt
   - Gera resposta em streaming
   - Retorna palavra por palavra

6. **Frontend**
   - Recebe stream
   - Atualiza chat em tempo real
   - Salva no localStorage

---

## ⚙️ Por Que É Assim?

### RAG (Retrieval-Augmented Generation)
- ✅ Reduz alucinação (modelo não inventa fatos)
- ✅ Responde baseado em documentos reais
- ✅ Fácil adicionar novos PDFs (não precisa retreinar modelo)

### FAISS
- ✅ Busca O(log n) em vez de O(n)
- ✅ Índice pré-computado = resposta rápida
- ✅ Suporta milões de documentos

### Ollama
- ✅ Roda localmente (privacidade)
- ✅ Streaming = resposta em tempo real
- ✅ Sem custos de API

### 3 Abas
- ✅ Aba "Sobre" = Onboarding claro
- ✅ Aba "Chat" = Foco na interação
- ✅ Aba "Recursos" = Referências confiáveis

### TXT + PDFs
- ✅ TXT é fácil editar
- ✅ PDFs podem ser adicionados pelos usuários
- ✅ Ambos indexados no mesmo sistema

---

## 🚀 Como Usar

### Instalação
```bash
cd rag_aula
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

### Preparar Ollama
```bash
# Em outro terminal
ollama serve

# Em outro terminal
ollama pull llama3:8b
```

### Rodar
```bash
python app.py
```

Acesse: http://localhost:5000

### Adicionar PDFs
1. Coloque arquivos .pdf em `documentos/`
2. Reinicie `python app.py`
3. Sistema detecta mudança e reindexá

---

## 📊 Arquitetura Visual

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/CSS/JS)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │ Sobre    │  │  Chat    │  │  Recursos    │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────┘
                        ↓ POST /ask
┌─────────────────────────────────────────────────────────┐
│                    Flask (app.py)                       │
│                  Rotas HTTP + Lógica                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   RAG System                             │
│  ┌─────────────────────────────────────────────┐        │
│  │ vectorstore.py                              │        │
│  │ - Carrega PDFs + TXT                        │        │
│  │ - Converte em embeddings (sentenceT.)       │        │
│  │ - Indexa com FAISS                          │        │
│  │ - Busca top-4 docs similares                │        │
│  └─────────────────────────────────────────────┘        │
│                        ↓                                 │
│  ┌─────────────────────────────────────────────┐        │
│  │ llm.py                                      │        │
│  │ - Monta prompt com contexto                 │        │
│  │ - Envia para Ollama                         │        │
│  │ - Recebe streaming de resposta              │        │
│  └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Ollama (Modelo llama3:8b)                  │
│            Gera respostas em streaming                  │
└─────────────────────────────────────────────────────────┘

Armazenamento:
├── data/cafe_conhecimento.txt       (TXT com base conhecimento)
├── documentos/*.pdf                 (PDFs adicionados)
├── rag/index.faiss                  (Índice FAISS)
├── rag/docs.npy                     (Documentos em numpy)
└── rag/meta.json                    (Hash de detecção de mudança)
```

---

## 🔍 Debugging

### Testar conexão
```bash
python test_connection.py
```

### Ver logs do Ollama
```bash
ollama serve
```

### Forçar reindexação
```bash
# Delete
del rag/index.faiss
del rag/docs.npy
del rag/meta.json

# Reiniciar
python app.py
```

### Adicionar debug ao chat
No `chat.html`, descomente console.log em `enviarPergunta()`:
```javascript
console.log("Pergunta enviada:", pergunta);
console.log("Resposta:", buffer);
```

---

## 📝 Próximos Passos Possíveis

- [ ] Adicionar autenticação de usuários
- [ ] Salvar histórico de conversa em banco de dados
- [ ] Dashboard com estatísticas de uso
- [ ] Exportar respostas para PDF
- [ ] Modo offline (download de modelo)
- [ ] Interface de admin para gerenciar PDFs
- [ ] Suporte a múltiplos idiomas
- [ ] Integração com Google Drive para PDFs

---

## 📧 Autor

Criado com ❤️ para estudantes e profissionais de Engenharia de Software.

**Última atualização:** Maio 2026
