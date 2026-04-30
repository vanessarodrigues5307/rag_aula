#!/usr/bin/env python3
"""Script para testar conexão com Ollama e vectorstore"""
import requests
import json
from rag.vectorstore import create_vectorstore

print("=" * 60)
print("TESTE DE CONEXÃO - MetricaIA")
print("=" * 60)

# Teste 1: Ollama
print("\n[1] Testando conexão com Ollama...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json()
        print("✓ Ollama está rodando!")
        print(f"  Modelos instalados: {[m['name'] for m in models.get('models', [])]}")
        
        # Verifica se llama3:8b está instalado
        model_names = [m['name'] for m in models.get('models', [])]
        if any('llama3' in m for m in model_names):
            print("✓ Modelo llama3 encontrado!")
        else:
            print("✗ Modelo llama3 NÃO encontrado! Execute: ollama pull llama3:8b")
    else:
        print(f"✗ Ollama respondeu com status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("✗ Ollama NÃO está rodando!")
    print("  Execute em outro terminal: ollama serve")
except Exception as e:
    print(f"✗ Erro ao conectar ao Ollama: {e}")

# Teste 2: Vectorstore
print("\n[2] Carregando vectorstore...")
try:
    index, docs = create_vectorstore()
    print(f"✓ Vectorstore carregado com sucesso!")
    print(f"  - Total de documentos: {len(docs)}")
    if len(docs) > 0:
        print(f"  - Primeiro documento (primeiros 100 chars): {docs[0][:100]}...")
    else:
        print("  ✗ Nenhum documento carregado!")
except Exception as e:
    print(f"✗ Erro ao carregar vectorstore: {e}")

# Teste 3: Teste simples de geração
print("\n[3] Testando geração de resposta...")
try:
    from rag.llm import gerar_resposta_stream
    
    contexto_teste = "Métricas de processo: Velocity é a quantidade de trabalho concluída em um sprint."
    pergunta_teste = "O que é velocity?"
    
    print("  Enviando pergunta: 'O que é velocity?'")
    resposta = ""
    for chunk in gerar_resposta_stream(contexto_teste, pergunta_teste):
        resposta += chunk
        print(".", end="", flush=True)
    
    print()
    if resposta:
        print(f"✓ Resposta recebida ({len(resposta)} caracteres)")
        print(f"  Resposta: {resposta[:150]}...")
    else:
        print("✗ Resposta vazia!")
except Exception as e:
    print(f"✗ Erro ao testar geração: {e}")

print("\n" + "=" * 60)
print("FIM DO TESTE")
print("=" * 60)
