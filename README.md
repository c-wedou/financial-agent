# Financial Analysis Agent

Agent IA autonome basé sur LangGraph et GPT-4o-mini pour générer des rapports financiers complets sur n'importe quelle entreprise cotée en bourse. L'agent orchestre 5 outils en autonomie : recherche web, données Yahoo Finance en temps réel, calcul de ratios, analyse de PDFs et génération de rapport structuré.

## Problème résolu

Les professionnels de la finance et les investisseurs individuels ont besoin d'accéder rapidement à une analyse financière complète d'une entreprise — données en temps réel, actualités récentes, ratios calculés — sans passer des heures à consolider des sources disparates.

GPT-4o-mini est choisi pour trois raisons : connaissance métier financier intégrée, génération de rapports fluides et structurés, et coût par token minimal pour un usage intensif.

## Architecture

```
financial-agent/
├── .env                    ← clés API (jamais committé sur GitHub)
├── .gitignore              ← exclut .env, __pycache__, outputs/
├── config.py               ← paramètres centralisés : modèle, température, iterations
├── requirements.txt        ← dépendances du projet
├── app.py                  ← interface Gradio — test en ligne
├── data/
│   └── documents/          ← PDFs à analyser
└── src/
    ├── tools.py            ← 5 outils : web_search, get_financial_data, calculator, read_pdf, generate_report
    ├── agent.py            ← AgentState, nodes, edges, graphe LangGraph, mémoire SQLite
    └── main.py             ← interface terminal
```


## Installation

```bash
git clone https://github.com/wedou/financial-agent
cd financial-agent
pip install -r requirements.txt
```

Copie `.env.example` en `.env` et ajoute tes clés API :

```bash
cp .env.example .env
# Édite .env et renseigne OPENAI_API_KEY et LANGCHAIN_API_KEY
```

## Lancement

**Interface Gradio :**
```bash
python app.py
```

**Interface terminal :**
```bash
python -m src.main
```



## Décisions techniques

**LangGraph plutôt que LangChain simple** : LangGraph permet un flux dynamique — l'agent décide à chaque étape quel outil appeler et dans quel ordre. Pour une comparaison entre deux entreprises, il peut appeler web_search deux fois, get_financial_data deux fois, calculator plusieurs fois. LangChain simple impose un ordre fixe défini à l'avance.

**GPT-4o-mini** : coût par token minimal pour un usage intensif, connaissance métier financier intégrée, génération de rapports fluides et structurés. Le meilleur rapport qualité/prix pour ce cas d'usage.

**SQLite pour la mémoire** : zéro configuration, pas de serveur, fichier unique. Chaque conversation est sauvegardée avec son thread_id — rechargeable entre les sessions sans refaire l'analyse.

**Yahoo Finance (yfinance)** : API gratuite sans clé, données en temps réel — prix, PE ratio, chiffre d'affaires, capitalisation, dette/equity. Aucun coût supplémentaire.

**LangSmith** : observabilité complète en production — chaque appel d'outil est tracé avec ses paramètres, le nombre de tokens consommés, la latence et les erreurs. Permet de déboguer et d'optimiser l'agent sans modifier le code.