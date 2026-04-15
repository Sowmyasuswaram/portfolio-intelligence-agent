# Portfolio Intelligence Agent

A multi-cloud agentic analytics system that answers business questions about financial portfolios using natural language.

**Live Demo:** [Click here to try it](https://portfolio-intelligence-agent-fckvu9wv9lvafermrcxpqw.streamlit.app)

---

## What It Does

Ask a question in plain English. The agent queries real financial data, reasons through the answer, and returns a written analysis with recommendations.

**Example questions:**
- Which stock has the best Sharpe ratio?
- Show me the top 5 performers by return
- Which stocks are the most volatile?
- Compare AAPL and MSFT performance

---

## Architecture
## Architecture
Yahoo Finance API
↓
AWS S3 (raw data storage)
↓
Azure Data Factory (transformation pipeline)
↓
DuckDB (analytical warehouse)
↓
LangGraph AI Agent (reasoning loop)
↓
Streamlit (web interface)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Ingestion | Python, yfinance, AWS S3 |
| Transformation | Azure Data Factory, SQL |
| Warehouse | DuckDB |
| AI Agent | LangGraph, LangChain, Groq (Llama 3.3) |
| Evaluation | RAGAS |
| Frontend | Streamlit |
| Deployment | Streamlit Cloud |

---

## Data

- **20 stocks** across tech, finance, healthcare, and ETFs
- **15 years** of daily price data (2009-2024)
- **75,000+ rows** of real market data
- **3 SQL models**: daily returns, risk metrics, quarterly performance

---

## SQL Models

**model_risk_metrics** — Annualized return, volatility, and Sharpe ratio per asset

**model_returns** — Daily returns calculated using LAG window functions

**model_quarterly** — Quarterly performance aggregates with STDDEV

---

## Agent Architecture

The agent uses a reasoning loop:

1. Receives a natural language question
2. Writes SQL to query the DuckDB warehouse
3. Executes the query and reads results
4. Synthesizes a written analysis with recommendation
5. Self-corrects if SQL fails

---

## How to Run Locally

```bash
git clone https://github.com/Sowmyasuswaram/portfolio-intelligence-agent.git
cd portfolio-intelligence-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add your Groq API key to `.env`:
GROQ_API_KEY=your_key_here

Build the database:
```bash
python pipelines/ingest.py
python pipelines/transform.py
```

Run the app:
```bash
streamlit run app.py
```

---

## Author

**Sowmya Suswaram**
MS Business Analytics & AI — University of Texas at Dallas
[LinkedIn](https://linkedin.com/in/sowmyasuswaram) | [Portfolio](your-portfolio-link)
