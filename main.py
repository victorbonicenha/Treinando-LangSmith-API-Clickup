import os
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import requests
from dotenv import load_dotenv
load_dotenv()

USER_ID = int(os.getenv("USER_ID_CLICKUP"))

# =========================
# CONFIG POR "INSTÂNCIA"
# =========================
TENANT = "lakatos"  # troque para: paranoa, daicast, etc

os.environ["LANGSMITH_PROJECT"] = f"rpa-{TENANT}"

# =========================
# ESTADO DO GRAFO
# =========================
class Estado(TypedDict):
    entrada: str
    resposta: str

# =========================
# MODELO
# =========================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# =========================
# NÓS DO GRAFO
# =========================
def modelo_node(state: Estado) -> Estado:
    resp = llm.invoke(state["entrada"])
    return {
        "entrada": state["entrada"],
        "resposta": resp.content
    }

# =========================
# MONTAGEM DO GRAFO
# =========================
graph = StateGraph(Estado)

graph.add_node("modelo", modelo_node)

graph.set_entry_point("modelo")
graph.add_edge("modelo", END)

app = graph.compile()

def criar_task_clickup(titulo, descricao, status, assignees=None):
    token = os.getenv("API_KEY_CLICKUP")
    list_id = os.getenv("LISTA_CLICKUP_ID")

    payload = {
        "name": titulo,
        "description": descricao,
        "status": status
    }

    if assignees:
        payload["assignees"] = assignees

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    resp = requests.post(
        f"https://api.clickup.com/api/v2/list/{list_id}/task",
        headers=headers,
        json=payload
    )

    if resp.status_code not in (200, 201):
        raise Exception(f"Erro ClickUp: {resp.status_code} - {resp.text}")

    return resp.json()

if __name__ == "__main__":
    resultado = app.invoke(
        {"entrada": "Explique o que é um robô RPA em uma frase"},
        config={
            "run_name": "Robo_Ponto",
            "tags": [
                f"tenant:{TENANT}",
                "robo:teste",
                "env:dev"
            ]
        }
    )

    print("Resposta final:")
    print(resultado["resposta"])


    # =========================
    # CRIA TASK AUTOMÁTICA NO CLICKUP
    # =========================

criar_task_clickup(
    titulo="Plataforma nova + integração do ClickUp via API",
    descricao=(
        "Task criada automaticamente via API ClickUp.\n\n"
        "Instância do projeto: Paranoá\n"
        "Origem: LangSmith + API ClickUp\n"
        "Objetivo: Criar task automaticamente com base na orquestração da plataforma nova"
    ),
    status="Fazendo",
    assignees=[USER_ID]
)

print("Tarefa criada automatica via API")
