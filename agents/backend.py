"""
backend_engineer.py

Backend Engineer Agent

Responsibilities
----------------
1. Design backend modules.
2. Define APIs.
3. Design database models.
4. Plan repositories and services.
5. Design authentication.
6. Define middleware.
7. Plan background jobs.
8. Create backend implementation roadmap.
"""

import os
import json
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


# ==========================================================
# STATE
# ==========================================================

class BackendState(TypedDict):
    user_request: str
    business_plan: dict
    product_requirements: dict
    architecture: dict
    backend_design: dict


# ==========================================================
# MODEL
# ==========================================================

def _get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
    )


# ==========================================================
# BACKEND NODE
# ==========================================================

def backend_node(state: BackendState):
    llm = _get_llm()

    prompt = f"""
You are a Principal Backend Engineer.

You are given:

USER REQUEST
------------
{state["user_request"]}

CEO BUSINESS PLAN
-----------------
{json.dumps(state["business_plan"], indent=2)}

PRODUCT REQUIREMENTS
--------------------
{json.dumps(state["product_requirements"], indent=2)}

ARCHITECTURE
------------
{json.dumps(state["architecture"], indent=2)}

Your job is NOT to write code.

Instead produce a Backend Engineering Design Document.

Your responsibilities:

1. Break the backend into modules.
2. Design repositories.
3. Design services.
4. Design database models.
5. Design API contracts.
6. Design authentication.
7. Design middleware.
8. Design background workers.
9. Design caching.
10. Design logging.
11. Design testing strategy.
12. Create implementation roadmap.

Return ONLY valid JSON.

Return EXACTLY this schema.

{{
    "backend_design": {{
        "modules": [
            {{
                "name": "",
                "responsibility": ""
            }}
        ],

        "folder_structure": [],

        "database_models": [
            {{
                "table": "",
                "description": "",
                "relationships": []
            }}
        ],

        "repositories": [],

        "services": [],

        "dto_models": [],

        "middlewares": [],

        "authentication": {{
            "type": "",
            "description": ""
        }},

        "authorization": {{
            "strategy": ""
        }},

        "api_contracts": [
            {{
                "method": "",
                "endpoint": "",
                "description": "",
                "request": {{}},
                "response": {{}}
            }}
        ],

        "background_jobs": [],

        "caching": [],

        "logging": [],

        "testing": [],

        "implementation_order": []
    }}
}}
IMPORTANT JSON RULES

- Return ONLY valid JSON.
- Every key must be inside double quotes.
- Every string must be inside double quotes.
- Never write

{{'email: string'}}

Instead write

{{
    "email":"string"
}}

Do not use comments.

Do not use trailing commas.
Do not use markdown.
Do not explain anything.

Do not wrap the JSON inside markdown.
"""

    response = llm.invoke(prompt)

    text = response.content.strip()

    text = (
        text.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        backend_design = json.loads(text)

    except json.JSONDecodeError as e:
        raise Exception(
            f"""
            Backend Engineer returned invalid JSON. Error:{e} Returned:{text}"""
        )

    return {
        "backend_design": backend_design
    }


# ==========================================================
# GRAPH
# ==========================================================

if __name__ == "__main__":
    graph = StateGraph(BackendState)
    graph.add_node("backend_engineer", backend_node)
    graph.set_entry_point("backend_engineer")
    graph.add_edge("backend_engineer", END)
    backend_graph = graph.compile()


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    state = {

        "user_request": """
Build an AI Resume Analyzer.

Features:

- Login
- Resume Upload
- ATS Score
- AI Suggestions
- Job Recommendation
- Dashboard
""",

        "business_plan": {
            "project_name": "AI Resume Analyzer",
            "priority": "High"
        },

        "product_requirements": {
            "prd": {
                "features": [
                    "Authentication",
                    "Resume Upload",
                    "ATS Score",
                    "Dashboard"
                ]
            }
        },

        "architecture": {
            "architecture": {
                "architecture_pattern": "Microservices",
                "tech_stack": {
                    "backend": "FastAPI",
                    "database": "PostgreSQL",
                    "cache": "Redis"
                }
            }
        },

        "backend_design": {}
    }

    result = backend_graph.invoke(state)

    print("\n========== BACKEND DESIGN ==========\n")

    print(json.dumps(result["backend_design"], indent=4))