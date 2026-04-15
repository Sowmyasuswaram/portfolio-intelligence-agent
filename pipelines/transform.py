import duckdb

def run_sql_models():
    con = duckdb.connect("database/portfolio.duckdb")

    print("Building model 1: daily returns...")
    con.execute("""
        CREATE OR REPLACE TABLE model_returns AS
        SELECT
            ticker,
            date,
            close_price,
            LAG(close_price) OVER (PARTITION BY ticker ORDER BY date) AS prev_close,
            ROUND(
                (close_price - LAG(close_price) OVER (PARTITION BY ticker ORDER BY date))
                / LAG(close_price) OVER (PARTITION BY ticker ORDER BY date), 6
            ) AS daily_return
        FROM raw_prices
    """)

    print("Building model 2: risk metrics...")
    con.execute("""
        CREATE OR REPLACE TABLE model_risk_metrics AS
        SELECT
            ticker,
            ROUND(AVG(daily_return) * 252, 4) AS annualized_return,
            ROUND(STDDEV(daily_return) * SQRT(252), 4) AS annualized_volatility,
            ROUND(
                (AVG(daily_return) * 252 - 0.05)
                / (STDDEV(daily_return) * SQRT(252)), 4
            ) AS sharpe_ratio,
            COUNT(*) AS trading_days
        FROM model_returns
        WHERE daily_return IS NOT NULL
        GROUP BY ticker
        ORDER BY sharpe_ratio DESC
    """)

    print("Building model 3: quarterly performance...")
    con.execute("""
        CREATE OR REPLACE TABLE model_quarterly AS
        SELECT
            ticker,
            DATE_TRUNC('quarter', date) AS quarter,
            ROUND(SUM(daily_return), 4) AS quarterly_return,
            ROUND(STDDEV(daily_return) * SQRT(63), 4) AS quarterly_volatility,
            MIN(close_price) AS quarter_low,
            MAX(close_price) AS quarter_high
        FROM model_returns
        WHERE daily_return IS NOT NULL
        GROUP BY ticker, DATE_TRUNC('quarter', date)
        ORDER BY ticker, quarter
    """)

    print("\nAll models built! Here are your risk metrics:")
    print(con.execute("SELECT * FROM model_risk_metrics").df().to_string(index=False))
    con.close()

if __name__ == "__main__":
    run_sql_models()