# agents/reviewer.py
import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class ReviewerState(TypedDict):
    user_request: str
    architecture: dict
    database_design: dict
    backend_design: dict
    frontend_design: dict
    review_feedback: dict

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

def reviewer_node(state: ReviewerState):
    prompt = f"""
You are a Principal Tech Lead and Code/Architecture Reviewer.

Your task is to review all generated plans and find gaps, risks, or optimizations.

Given:
- USER REQUEST: {state["user_request"]}
- ARCHITECTURE: {json.dumps(state.get("architecture", {}), indent=2)}
- DATABASE DESIGN: {json.dumps(state.get("database_design", {}), indent=2)}
- BACKEND DESIGN: {json.dumps(state.get("backend_design", {}), indent=2)}
- FRONTEND DESIGN: {json.dumps(state.get("frontend_design", {}), indent=2)}

Return ONLY valid JSON matching this schema:

{{{{
    "review_feedback": {{{{
        "general_evaluation": "Overview of quality and structural completeness",
        "scores": {{{{
            "architecture": 8,
            "backend": 9,
            "frontend": 7,
            "security": 6
        }}}},
        "criticisms": [
            {{{{
                "area": "Security",
                "severity": "high",
                "issue": "Missing rate limiter config in Gateway API contract.",
                "recommendation": "Add a rate limiting middleware on login and signup endpoints."
            }}}}
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
        review_feedback = json.loads(text)
    except json.JSONDecodeError as e:
        raise Exception(f"Reviewer Agent returned invalid JSON. Error: {e} Text: {text}")

    return {"review_feedback": review_feedback}

graph = StateGraph(ReviewerState)
graph.add_node("reviewer_agent", reviewer_node)
graph.set_entry_point("reviewer_agent")
graph.add_edge("reviewer_agent", END)
reviewer_graph = graph.compile()
