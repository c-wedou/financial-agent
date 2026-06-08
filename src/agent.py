from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from src.tools import web_search, get_financial_data, calculator, generate_report, read_pdf
from config import MODEL_NAME, TEMPERATURE
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage
import sqlite3

load_dotenv()  ## charge la clé api depuis .env

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


tools = [web_search, get_financial_data, calculator, read_pdf, generate_report]
llm = ChatOpenAI(model = MODEL_NAME, temperature = TEMPERATURE)
llm_with_tools = llm.bind_tools(tools)



SYSTEM_PROMPT = """Tu es un expert en analyse financière. 
Pour analyser une entreprise : utilise web_search puis get_financial_data puis calculator puis generate_report.
Pour comparer deux entreprises : appelle get_financial_data pour chaque entreprise séparément, calcule les ratios pour les deux, puis génère un rapport comparatif."""

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