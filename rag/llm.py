import json
import requests
from typing import List
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:8b"

def montar_prompt (contexto: str, pergunta: str, historico: List[str] = None) -> str:
    historico_formatado = ""
    if historico:
        
        historico_formatado= "\n".join(historico)
    prompt = f"""
Você é um assitente especializado em cafeicultura, agronomia e produção de café.
Seu objetivo é apoiar produtores, tecnicos e pesquisadores com informações tecnicas, praticas e baseadas
em evidencias sobre  o cultivo do café.
Diretrizes: 
-responda de forma clara, objetiva e tecnica
-utilize linguagem acessivel ao produtor real, mas com base cientifica.
-priorize recomendações praticas quando acessivel.
-se a pergunta envolver manejo, detalhe etapas e boas praticas.
-se a pergunta envolver pragas e doenças, explique sintomas, causas e controle.
- se a resposta nao estiver no contexto fornecido, diga:
"não encontrei essa infromação na base de conhecimento sobre cafeicultura."
- não invente informações, mas pode usar a base que você foi pré-treinada para responder sobre café.
areas de domínio:
cafeicultura, manejo cafeeiro, pragas e doenças do café (ex: ferrugem, cercosporiose), 
adubação e nutrição, clima e solo,  pós-colheita e qualidade do café

historico da conversa:
{historico_formatado}

contexto rag:
{contexto}

pergunta do usuário:
{pergunta}

resposta:
"""
    return prompt

def gerar_resposta_stream (contexto, pergunta, historico=None):
    prompt = montar_prompt(contexto, pergunta, historico)
    response= requests.post(
        OLLAMA_URL, 
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True
        },
        stream=True
    )
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            texto = chunk.get("response", "")
            yield texto



