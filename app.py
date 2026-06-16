import streamlit as st
from src.agent import app
from langchain_core.messages import HumanMessage
import uuid
from config import MAX_ITERATIONS
import plotly.graph_objects as go
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
import io


def extraire_donnees_graphiques(messages):
    """Extrait les données de cours de bourse depuis les messages de l'agent."""
    graphiques = {}
    for message in messages:
        if hasattr(message, 'content') and message.content:
            try:
                data = json.loads(message.content)
                if isinstance(data, dict) and "ticker" in data and "dates" in data:
                    graphiques[data["ticker"]] = data
            except (json.JSONDecodeError, TypeError):
                pass
    return graphiques


def creer_graphique(data):
    """Crée un graphique Plotly du cours de bourse."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["dates"],
        y=data["prices"],
        mode="lines",
        name=data["company_name"],
        line=dict(color="#1f77b4", width=2)
    ))
    fig.update_layout(
        title=f"Cours de bourse — {data['company_name']}",
        xaxis_title="Date",
        yaxis_title="Prix (€/$)",
        height=400,
        template="plotly_white"
    )
    return fig

def generer_pdf(rapport_texte):
    """Génère un PDF professionnel depuis le texte du rapport."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    contenu = []

    for ligne in rapport_texte.split("\n"):
        ligne = ligne.strip()
        if ligne.startswith("[GRAPHIQUE:"):
            continue  # on saute les marqueurs graphiques dans le PDF
        elif ligne.isupper() and len(ligne) > 3:
            contenu.append(Paragraph(ligne, styles["Heading1"]))
            contenu.append(Spacer(1, 0.3*cm))
        elif ligne:
            contenu.append(Paragraph(ligne, styles["Normal"]))
            contenu.append(Spacer(1, 0.2*cm))

    doc.build(contenu)
    buffer.seek(0)
    return buffer


st.set_page_config(
    page_title="Financial Analysis Agent",
    page_icon="📈",
    layout="wide" 
)


with st.sidebar:
    st.title("📈 Financial Agent")
    st.markdown("---")
    st.markdown("### Comment utiliser l'agent ?")
    st.markdown("""
    - **Analyser une entreprise** : *Analyse Apple*
    - **Comparer deux entreprises** : *Compare Apple et Microsoft*
    - **Données financières** : *Donne-moi le PE ratio de Tesla*
    """)
    st.markdown("---")
    st.markdown("### À propos")
    st.markdown("""
    Agent IA autonome basé sur **LangGraph** et **GPT-4o-mini**.
    
    Outils disponibles :
    - 🔍 Recherche web
    - 📊 Données Yahoo Finance
    - 🧮 Calcul de ratios
    - 📄 Analyse de PDFs
    - 📝 Génération de rapport
    """)


st.title("Financial Analysis Agent")
st.markdown("Analysez n'importe quelle entreprise cotée en bourse.")

question = st.text_input(
    label="Votre question",
    placeholder="Ex : Analyse Apple ou Compare Apple et Microsoft"
)

if st.button("Analyser", type="primary"):
    if question.strip()=="":
        st.warning("Veuillez entrer une question.")
    else:
        with st.spinner("L'agent analyse en cours... (peut prendre 1-2 minutes)"):
            thread_id = str(uuid.uuid4())
            result = app.invoke(
            {"messages": [HumanMessage(content=question)]},
            {"configurable": {"thread_id": thread_id}, "recursion_limit": MAX_ITERATIONS}
            )
            response = result["messages"][-1].content
        st.markdown("---")
        st.markdown("### 📋 Rapport financier")

        # Extraire les données graphiques depuis les messages
        graphiques = extraire_donnees_graphiques(result["messages"])

        # Parser le rapport et afficher section par section
        sections = response.split("\n")
        for ligne in sections:
            ligne_stripped = ligne.strip()
            if ligne_stripped.startswith("[GRAPHIQUE:") and ligne_stripped.endswith("]"):
                # Extraire le ticker et afficher le graphique
                ticker = ligne_stripped[11:-1]
                if ticker in graphiques:
                    st.plotly_chart(creer_graphique(graphiques[ticker]), use_container_width=True)
                else:
                    st.info(f"Graphique non disponible pour {ticker}")
            elif ligne_stripped:
                st.markdown(ligne)

        # Bouton export PDF
        st.markdown("---")
        pdf_buffer = generer_pdf(response)
        st.download_button(
            label="📄 Exporter en PDF",
            data=pdf_buffer,
            file_name="rapport_financier.pdf",
            mime="application/pdf"
        )


