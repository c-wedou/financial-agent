from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import yfinance as yf
import pdfplumber 

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
def calculator(operation : str, values : str):
    """ Calcule les rations financier courants. Les calculs comme si s'était un expert financier qui veut faire un bechmarking"""
    valeur1, valeur2 = values.split(',', maxsplit= 1)
    valeur1, valeur2 = float(valeur1), float(valeur2)

    if operation == "ratio":
        return str(valeur1/valeur2)
    elif operation == "variation":
        return str(((valeur2-valeur1)/valeur1)*100)
    else:
        return str((valeur1/valeur2)*100)


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
def generate_report(data : str):
    """Génère un rapport financier structuré final à partir des données collectées. Vraiment un rapport complet et bien structuré et aussi il y a pas de styles IA sans les * les - style vraiment naturel"""
    return f"""
    Rapport D'analyse Financière Confidentiel 


    {data}  

    
    Ce rapport est généré par Financial Analysis Agent """

