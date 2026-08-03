# agents/security.py
import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class SecurityState(TypedDict):
    user_request: str
    architecture: dict
    security_report: dict

def _get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
    )

def security_node(state: SecurityState):
    llm = _get_llm()
    prompt = f"""
You are a Lead Application Security Engineer.

Your task is to analyze the proposed architecture and define security constraints and audits.

Given:
- USER REQUEST: {state["user_request"]}
- ARCHITECTURE: {json.dumps(state.get("architecture", {}), indent=2)}

Return ONLY valid JSON matching this schema:

{{{{
    "security_report": {{{{
        "threat_model": [
            "External attacker attempts brute-forcing JWT secrets",
            "Malicious SQL Injection inputs passed to backend API"
        ],
        "auth_security": {{{{
            "type": "JWT",
            "hashing_algorithm": "bcrypt",
            "token_expiration": "15m",
            "mfa": "Suggested for admin roles"
        }}}},
        "vulnerability_mitigation": [
            {{{{
                "vulnerability": "SQL Injection",
                "mitigation_strategy": "Use ORM parameterization strictly (e.g. SQLAlchemy, Prisma)"
            }}}}
        ],
        "headers_and_cors": {{{{
            "cors_policy": "Restrict to trusted client domains",
            "security_headers": ["Content-Security-Policy", "X-Frame-Options", "Strict-Transport-Security"]
        }}}},
        "compliance": ["GDPR (data sanitization)", "OWASP Top 10 Compliance Checklist"]
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
        security_report = json.loads(text)
    except json.JSONDecodeError as e:
        raise Exception(f"Security Agent returned invalid JSON. Error: {e} Text: {text}")

    return {"security_report": security_report}

if __name__ == "__main__":
    graph = StateGraph(SecurityState)
    graph.add_node("security_engineer", security_node)
    graph.set_entry_point("security_engineer")
    graph.add_edge("security_engineer", END)
    security_graph = graph.compile()
