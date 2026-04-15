import duckdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from langchain.tools import tool
import json

DB_PATH = "database/portfolio.duckdb"

@tool
def query_portfolio(sql: str) -> str:
    """
    Query the portfolio database using SQL.
    Tables available:
    - raw_prices: date, ticker, close_price
    - model_returns: ticker, date, close_price, daily_return
    - model_risk_metrics: ticker, annualized_return, annualized_volatility, sharpe_ratio, trading_days
    - model_quarterly: ticker, quarter, quarterly_return, quarterly_volatility, quarter_low, quarter_high
    Always write valid DuckDB SQL.
    """
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        result = con.execute(sql).df()
        con.close()
        return result.to_string(index=False)
    except Exception as e:
        return f"SQL Error: {str(e)} — Please rewrite the query and try again."

@tool
def get_top_performers(metric: str) -> str:
    """
    Get top 5 and bottom 5 stocks by a metric.
    metric options: sharpe_ratio, annualized_return, annualized_volatility
    """
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        result = con.execute(f"""
            SELECT ticker, {metric}
            FROM model_risk_metrics
            ORDER BY {metric} DESC
        """).df()
        con.close()
        top5 = result.head(5).to_string(index=False)
        bottom5 = result.tail(5).to_string(index=False)
        return f"TOP 5:\n{top5}\n\nBOTTOM 5:\n{bottom5}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def generate_chart(chart_type: str, sql: str, title: str) -> str:
    """
    Generate a chart from SQL data and save it.
    chart_type: 'bar', 'scatter', or 'line'
    sql: query to get the data
    title: chart title
    """
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df = con.execute(sql).df()
        con.close()

        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "bar":
            ax.bar(df.iloc[:, 0], df.iloc[:, 1], color="#4F46E5", alpha=0.8)
            ax.set_xlabel(df.columns[0])
            ax.set_ylabel(df.columns[1])
            plt.xticks(rotation=45)

        elif chart_type == "scatter" and len(df.columns) >= 3:
            ax.scatter(df.iloc[:, 1], df.iloc[:, 2],
                      color="#4F46E5", alpha=0.7, s=100)
            for _, row in df.iterrows():
                ax.annotate(row.iloc[0],
                          (row.iloc[1], row.iloc[2]),
                          fontsize=9, ha='right')
            ax.set_xlabel(df.columns[1])
            ax.set_ylabel(df.columns[2])

        elif chart_type == "line":
            for ticker in df.iloc[:, 0].unique():
                subset = df[df.iloc[:, 0] == ticker]
                ax.plot(subset.iloc[:, 1], subset.iloc[:, 2],
                       label=ticker, linewidth=2)
            ax.legend()
            ax.set_xlabel(df.columns[1])
            ax.set_ylabel(df.columns[2])

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        path = "data/processed/latest_chart.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return f"Chart saved. Title: {title}"
    except Exception as e:
        return f"Chart error: {str(e)}"

ALL_TOOLS = [query_portfolio, get_top_performers, generate_chart]