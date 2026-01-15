import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

load_dotenv()

TENANT = "lakatos"
os.environ["LANGSMITH_PROJECT"] = f"rpa-{TENANT}"

class Estado(TypedDict):
    entrada: str
    resposta: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def modelo_node(state: Estado) -> Estado:
    resp = llm.invoke(state["entrada"])
    return {
        "entrada": state["entrada"],
        "resposta": resp.content
    }

graph = StateGraph(Estado)
graph.add_node("modelo", modelo_node)
graph.set_entry_point("modelo")
graph.add_edge("modelo", END)

app = graph.compile()
