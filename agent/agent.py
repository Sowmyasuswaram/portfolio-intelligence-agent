import os
from dotenv import load_dotenv
from groq import Groq
import json
import duckdb

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'portfolio.duckdb')

def query_portfolio(sql: str) -> str:
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        result = con.execute(sql).df()
        con.close()
        return result.to_string(index=False)
    except Exception as e:
        return f"SQL Error: {str(e)}"

def run_agent(question: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": "You are a portfolio analyst. You have access to a database with stock data. Tables: model_risk_metrics (ticker, annualized_return, annualized_volatility, sharpe_ratio, trading_days), model_quarterly (ticker, quarter, quarterly_return, quarterly_volatility). When asked a question, write a SQL query to answer it, then analyze the results."
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nFirst write a SQL query to get the data, then analyze it."
        }
    ]

    # Step 1: Ask LLM to write SQL
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0
    )

    llm_response = response.choices[0].message.content

    # Step 2: Extract SQL and run it
    steps = []
    data_result = ""

    if "SELECT" in llm_response.upper():
        lines = llm_response.split("\n")
        sql_lines = []
        in_sql = False
        for line in lines:
            if "SELECT" in line.upper():
                in_sql = True
            if in_sql:
                sql_lines.append(line)
                if ";" in line or (in_sql and line.strip() == ""):
                    break

        sql = " ".join(sql_lines).replace("```sql", "").replace("```", "").strip()
        if sql:
            steps.append(f"Ran SQL: {sql[:100]}...")
            data_result = query_portfolio(sql)

    # Step 3: Ask LLM to analyze the results
    if data_result:
        messages.append({"role": "assistant", "content": llm_response})
        messages.append({
            "role": "user",
            "content": f"Here are the query results:\n{data_result}\n\nNow give a clear analysis and recommendation."
        })

        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0
        )
        final_answer = final_response.choices[0].message.content
    else:
        final_answer = llm_response

    return {"answer": final_answer, "steps": steps}


if __name__ == "__main__":
    print("Testing agent...")
    result = run_agent("Which stock has the best Sharpe ratio?")
    print("\nSteps taken:")
    for step in result["steps"]:
        print(f"  -> {step}")
    print(f"\nAnswer:\n{result['answer']}")