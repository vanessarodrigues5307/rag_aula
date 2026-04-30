from flask import Flask, render_template, request, Response
from rag.vectorstore import create_vectorstore
import requests
import json
from rag.vectorstore import retrieve
from rag.llm import gerar_resposta_stream

app= Flask(__name__)

index, docs= create_vectorstore()
print("Vectorstore", len(docs))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/recursos")
def recursos():
    return render_template("recursos.html")

@app.route("/ask", methods = ["POST"])

def ask():
    data=request.get_json()
    question = data["question"]
    try:
        #resultados = index.similarity_search(question, k=4)
        resultados = retrieve(question, index, docs, top_k=4)

        #contexto_relevante = "/n".join([doc.page_content for doc in resultados])
        contexto_relevante = "\n\n --- \n\n".join(resultados)

    except Exception as e:
        print("erro no vectorstore:",e)
        contexto_relevante= "\n".join(docs[:4])
    
    def gerar():
        try:
            yield from gerar_resposta_stream(contexto_relevante, question)
        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            yield f"Erro ao gerar resposta: {str(e)}"
    
    return Response(gerar(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
