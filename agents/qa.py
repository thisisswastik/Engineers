# agents/qa.py
import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class QAState(TypedDict):
    user_request: str
    product_requirements: dict
    architecture: dict
    qa_plan: dict

def _get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
    )

def qa_node(state: QAState):
    llm = _get_llm()
    prompt = f"""
You are a Principal QA (Quality Assurance) Engineer.

Your task is to design a comprehensive automated testing strategy and QA plan.

Given:
- USER REQUEST: {state["user_request"]}
- PRODUCT REQUIREMENTS: {json.dumps(state.get("product_requirements", {}), indent=2)}
- ARCHITECTURE: {json.dumps(state.get("architecture", {}), indent=2)}

Return ONLY valid JSON matching this schema:

{{{{
    "qa_plan": {{{{
        "testing_strategy": "Overall automation testing approach",
        "tools": {{{{
            "unit": "Jest / Pytest etc.",
            "integration": "Supertest / Postman etc.",
            "e2e": "Playwright / Cypress etc."
        }}}},
        "test_cases": [
            {{{{
                "id": "TC-01",
                "description": "User login with valid credentials",
                "type": "integration",
                "component": "Authentication Service",
                "steps": [
                    "Send POST to /api/auth/login with valid credentials",
                    "Assert response code is 200",
                    "Assert response contains access token"
                ],
                "expected_result": "User receives access token and status code 200"
            }}}}
        ],
        "ci_test_integration": [
            "Run unit and integration tests on pull request to main",
            "Generate test coverage report"
        ]
    }}}}
}}}}

IMPORTANT:
- Return ONLY valid JSON.
- DO NOT wrap the JSON inside markdown code blocks.
- Every key/string must be in double quotes. No trailing commas.
"""

    response = llm.invoke(prompt)
    text = response.content.strip().replace("```json", "").replace("```", "").strip()

    try:
        qa_plan = json.loads(text)
    except json.JSONDecodeError as e:
        raise Exception(f"QA Agent returned invalid JSON. Error: {e} Text: {text}")

    return {"qa_plan": qa_plan}

if __name__ == "__main__":
    graph = StateGraph(QAState)
    graph.add_node("qa_engineer", qa_node)
    graph.set_entry_point("qa_engineer")
    graph.add_edge("qa_engineer", END)
    qa_graph = graph.compile()
