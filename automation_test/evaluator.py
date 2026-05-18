import pandas as pd
import requests
import json
import os
import time
import sys
from openai import OpenAI
from app.core.llm.config import llm_settings

# Fix Windows console encoding issues for Vietnamese unicode printing
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Configuration
API_URL = "http://localhost:8000/api/chat"
JUDGE_MODEL = llm_settings.DEFAULT_MODEL
EVALUATION_REPORT_PATH = "automation_test/evaluation_report.csv"

# LLM-as-a-judge prompt template
JUDGE_PROMPT = """
You are an expert QA evaluator. Your task is to evaluate the chatbot's response based on the question.

Question: {question}
Chatbot Response: {response}

Evaluate based on two criteria (score 0 to 10):
1. Faithfulness: Is the response grounded? If the bot says it doesn't know because it's not in the context, and the question is indeed irrelevant (like "What color is the sky"), it should get a 10 for Faithfulness (it didn't hallucinate).
2. Relevance: Does the response directly answer the question?

Return ONLY a valid JSON object with the following structure, no markdown formatting, no explanation:
{{"faithfulness_score": 8, "relevance_score": 9, "reasoning": "short reasoning here"}}
"""

def evaluate_response(judge_client: OpenAI, question: str, response: str) -> dict:
    """Use an LLM to evaluate the quality of the response."""
    try:
        prompt = JUDGE_PROMPT.format(question=question, response=response)
        
        res = judge_client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        result_json = res.choices[0].message.content
        return json.loads(result_json)
    except Exception as e:
        print(f"Error evaluating response: {e}")
        return {"faithfulness_score": 0, "relevance_score": 0, "reasoning": "Evaluation failed"}

def run_automation_test():
    print("--- Starting Automation QA Testing ---")
    
    # 1. Load test cases
    try:
        df = pd.read_excel('automation_test/test_cases.xlsx')
    except Exception as e:
        print(f"Failed to load test cases: {e}. Please run generate_test_data.py first.")
        return
    judge_client = OpenAI(
        api_key=llm_settings.PRIMARY_LLM_API_KEY,
        base_url=llm_settings.PRIMARY_LLM_BASE_URL
    )
    
    results = []
    
    # 2. Iterate through test cases
    for index, row in df.iterrows():
        question = row['question']
        print(f"\n[{index+1}/{len(df)}] Testing: {question}")
        
        # 3. Call Chatbot API
        start_time = time.time()
        try:
            res = requests.post(API_URL, json={"message": question})
            if res.status_code == 200:
                bot_response = res.json().get('reply', '')
            else:
                bot_response = f"API Error: {res.status_code}"
        except Exception as e:
            bot_response = f"Connection Error: {e}"
            
        latency = round(time.time() - start_time, 2)
        print(f"Response ({latency}s): {bot_response[:100]}...")
        
        # 4. Evaluate using LLM Judge
        eval_result = evaluate_response(judge_client, question, bot_response)
        print(f"Scores -> Faithfulness: {eval_result.get('faithfulness_score')}, Relevance: {eval_result.get('relevance_score')}")
        
        results.append({
            "id": row.get('id', index),
            "question": question,
            "expected_context": row.get('expected_context', ''),
            "bot_response": bot_response,
            "latency_sec": latency,
            "faithfulness_score": eval_result.get('faithfulness_score', 0),
            "relevance_score": eval_result.get('relevance_score', 0),
            "reasoning": eval_result.get('reasoning', '')
        })
        
    # 5. Generate Report
    report_df = pd.DataFrame(results)
    report_df.to_csv(EVALUATION_REPORT_PATH, index=False, encoding='utf-8-sig')
    
    avg_faithfulness = report_df['faithfulness_score'].mean()
    avg_relevance = report_df['relevance_score'].mean()
    
    print("\n--- Test Completed ---")
    print(f"Avg Faithfulness: {avg_faithfulness:.2f}/10")
    print(f"Avg Relevance: {avg_relevance:.2f}/10")
    print(f"Report saved to: {EVALUATION_REPORT_PATH}")

if __name__ == "__main__":
    run_automation_test()
