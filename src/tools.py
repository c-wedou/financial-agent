from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import yfinance as yf
import pdfplumber 
import plotly.graph_objects as go
import json

@tool
def web_search(parametre : str):
    """Recherche des articles et actualités sur internet à partir d'une requête. Toutes les actualités intéressantes sur internet qui porte sur la requête je veux que tu les cherches."""
    search = DuckDuckGoSearchRun()
    results = search.run(parametre)
    return results

@tool
def get_financial_data(ticker: str) -> str:
    """Récupère les données financières depuis Yahoo Finance.
    Le paramètre ticker doit être un symbole boursier Yahoo Finance 
    (ex: 'ATE.PA' pour Alten, 'MC.PA' pour LVMH, 'AAPL' pour Apple).
    Si tu ne connais pas le ticker, utilise web_search d'abord pour le trouver."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return f"""
    Entreprise : {info.get('longName', 'N/A')}
    Prix actuel : {info.get('currentPrice', 'N/A')}
    PE Ratio: {info.get('trailingPE', 'N/A')}
    Chiffre d'affaires: {info.get('totalRevenue', 'N/A')}
    Capitalisation: {info.get('marketCap', 'N/A')}
    Dette/Equity: {info.get('debtToEquity', 'N/A')}
    """
@tool
def calculator(operation: str, values: str):
    """Calcule les ratios financiers courants. 
    Le paramètre values doit contenir UNIQUEMENT deux nombres séparés par une virgule.
    Exemple : '25.5,30.2' et non 'PE Ratio,30.2'"""
    try:
        parties = values.split(',', maxsplit=1)
        if len(parties) != 2:
            return "Erreur : values doit contenir exactement deux nombres séparés par une virgule"
        
        valeur1 = float(parties[0].strip())
        valeur2 = float(parties[1].strip())

        if operation == "ratio":
            return str(round(valeur1 / valeur2, 4))
        elif operation == "variation":
            return str(round(((valeur2 - valeur1) / valeur1) * 100, 4))
        else:
            return str(round((valeur1 / valeur2) * 100, 4))
    except ValueError as e:
        return f"Erreur de calcul : les valeurs doivent être des nombres. Reçu : {values}"

@tool
def read_pdf(chemin : str):
    """ Lire des pdf et il retour un rapport annuel bien structuré."""
    with pdfplumber.open(chemin) as pdf:
        pages_text =[]
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            pages_text.append({
                "page" : i+1,
                "text" : text
            }) 
    return "\n\n".join([f"Page {p['page']}:\n{p['text']}" for p in pages_text if p['text']])
    


@tool
def get_stock_history(ticker: str) -> str:
    """Récupère l'historique du cours de bourse sur 1 an pour générer un graphique.
    Retourne les données en JSON pour affichage graphique.
    Le paramètre ticker doit être un symbole boursier Yahoo Finance
    (ex: 'AAPL' pour Apple, 'MC.PA' pour LVMH)."""
    stock = yf.Ticker(ticker)
    history = stock.history(period="1y")
    
    if history.empty:
        return json.dumps({"error": f"Aucune donnée trouvée pour {ticker}"})
    
    data = {
        "ticker": ticker,
        "dates": history.index.strftime("%Y-%m-%d").tolist(),
        "prices": [round(p, 2) for p in history["Close"].tolist()],
        "company_name": stock.info.get("longName", ticker)
    }
    return json.dumps(data)



@tool 
def generate_report(data : str):
    """Génère un rapport financier structuré final à partir des données collectées. Vraiment un rapport complet et bien structuré et aussi il y a pas de styles IA sans les * les - style vraiment naturel"""
    return f"""
    Rapport D'analyse Financière Confidentiel 


    {data}  

    
    Ce rapport est généré par Financial Analysis Agent """


