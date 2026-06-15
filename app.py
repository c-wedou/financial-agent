import gradio as gr
from src.agent import app
from langchain_core.messages import HumanMessage
import uuid
from config import MAX_ITERATIONS


def analyze(question):
    thread_id = str(uuid.uuid4())
    result = app.invoke(
        {"messages": [HumanMessage(content=question)]},
        {"configurable": {"thread_id": thread_id}, "recursion_limit": MAX_ITERATIONS}
    )
    return result["messages"][-1].content

interface = gr.Interface(
    fn=analyze,
    inputs=gr.Textbox(label = "Votre question", placeholder = "EX : Analyse Wedfinance"),
    outputs=gr.Textbox(label = "Rapport financier", lines = 40),
    title="Financial Analysis Agent",
    description="Analysez n'importe quelle entreprise cotée en bourse. Exemple : Analyse Wedfinance ou Compare Wedfinance et CHEfinance."
)

interface.launch(server_name="0.0.0.0", server_port=7860)