import yfinance as yf
import duckdb
import pandas as pd

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "JPM", "JNJ", "UNH",
    "XOM", "BAC", "WMT", "PG", "V",
    "MA", "HD", "SPY", "QQQ", "GLD"
]

def download_data():
    print("Downloading 15 years of stock data...")
    df = yf.download(TICKERS, start="2009-01-01", end="2024-01-01")
    
    # Keep only closing prices
    prices = df["Close"].reset_index()
    prices = prices.melt(id_vars="Date", var_name="ticker", value_name="close_price")
    prices = prices.dropna()
    prices["date"] = pd.to_datetime(prices["Date"])
    prices = prices[["date", "ticker", "close_price"]]
    
    print(f"Downloaded {len(prices)} rows of data")
    return prices

def load_to_duckdb(df):
    print("Loading into DuckDB...")
    con = duckdb.connect("database/portfolio.duckdb")
    con.execute("DROP TABLE IF EXISTS raw_prices")
    con.execute("""
        CREATE TABLE raw_prices AS 
        SELECT * FROM df
    """)
    count = con.execute("SELECT COUNT(*) FROM raw_prices").fetchone()[0]
    print(f"Loaded {count} rows into DuckDB")
    con.close()

if __name__ == "__main__":
    df = download_data()
    load_to_duckdb(df)
    print("Done! Data is ready.")