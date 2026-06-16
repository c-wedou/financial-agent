from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from src.tools import web_search, get_financial_data, calculator, generate_report, read_pdf, get_stock_history
from config import MODEL_NAME, TEMPERATURE
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage
import sqlite3

load_dotenv()  ## charge la clé api depuis .env

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


tools = [web_search, get_financial_data, calculator, read_pdf, generate_report, get_stock_history]
llm = ChatOpenAI(model = MODEL_NAME, temperature = TEMPERATURE)
llm_with_tools = llm.bind_tools(tools)


SYSTEM_PROMPT = """Tu es un expert en analyse financière professionnelle.

RÈGLES DE RÉDACTION (obligatoires) :
- Rédige en français, en prose naturelle et professionnelle
- N'utilise JAMAIS de symboles Markdown : pas de **, pas de *, pas de #, pas de ---
- Utilise des titres en MAJUSCULES pour structurer les sections
- Pour insérer un graphique du cours de bourse, écris exactement : [GRAPHIQUE:TICKER]
  Exemple : [GRAPHIQUE:AAPL] pour Apple, [GRAPHIQUE:MC.PA] pour LVMH

PROCESSUS POUR ANALYSER UNE ENTREPRISE :
1. web_search pour les actualités récentes
2. get_financial_data pour les données financières
3. get_stock_history pour l'historique du cours
4. calculator pour les ratios clés
5. generate_report pour le rapport final structuré ainsi :

PRÉSENTATION DE L'ENTREPRISE
[texte]
[GRAPHIQUE:TICKER]
DONNÉES FINANCIÈRES
[texte]
ACTUALITÉS RÉCENTES
[texte]
ANALYSE ET RATIOS
[texte]
CONCLUSION ET RECOMMANDATION
[texte]

PROCESSUS POUR COMPARER N ENTREPRISES :
1. Pour chaque entreprise : web_search, get_financial_data, get_stock_history
2. calculator pour comparer les ratios
3. generate_report avec ce plan :

COMPARAISON DE N ENTREPRISES
[GRAPHIQUE:TICKER1]
[GRAPHIQUE:TICKER2]
... (un graphique par entreprise)
DONNÉES FINANCIÈRES COMPARATIVES
[texte comparatif]
ANALYSE COMPARATIVE
[texte]
CONCLUSION
[texte]

Ce rapport doit être digne d'un cabinet de conseil professionnel."""

def agent_node(state: AgentState) -> dict:

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages":[response]}

tool_node = ToolNode(tools)


## edge conditionnele: si agent node choisit un outil alors on choisit l'outil et sinon on revient vers l'agent do

def should_continue(state : AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")


conn = sqlite3.connect("memory.db", check_same_thread=False)
memory = SqliteSaver(conn)
app = graph.compile(checkpointer=memory)