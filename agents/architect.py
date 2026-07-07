"""
architect.py

Architect Agent

Responsibilities
----------------
1. Design the overall system architecture.
2. Select the technology stack.
3. Design the database.
4. Define APIs.
5. Decide whether microservices are required.
6. Design deployment & infrastructure.
7. Specify security considerations.
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

class ArchitectState(TypedDict):
    user_request: str
    business_plan: dict
    product_requirements: dict
    architecture: dict


# ==========================================================
# MODEL
# ==========================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)


# ==========================================================
# ARCHITECT NODE
# ==========================================================

def architect_node(state: ArchitectState):

    prompt = f"""
You are a Principal Software Architect.

Your responsibility is NOT to write code.

Your responsibility is to design a complete technical architecture
for the engineering teams.

--------------------------------------------------
USER REQUEST
--------------------------------------------------

{state["user_request"]}

--------------------------------------------------
CEO BUSINESS PLAN
--------------------------------------------------

{json.dumps(state["business_plan"], indent=2)}

--------------------------------------------------
PRODUCT REQUIREMENTS
--------------------------------------------------

{json.dumps(state["product_requirements"], indent=2)}

--------------------------------------------------

Design a production-ready architecture.

Return ONLY valid JSON.

Do NOT explain anything.

Do NOT wrap the JSON inside markdown.

Return EXACTLY this schema.

{{
  "architecture": {{
    "architecture_pattern": "",
    "tech_stack": {{
      "frontend": "",
      "backend": "",
      "database": "",
      "ai_framework": "",
      "cache": "",
      "message_queue": "",
      "cloud": ""
    }},
    "database_schema": [
      {{
        "table": "",
        "columns": []
      }}
    ],
    "api_endpoints": [
      {{
        "method": "",
        "endpoint": "",
        "description": ""
      }}
    ],
    "microservices": [
      {{
        "name": "",
        "responsibility": ""
      }}
    ],
    "folder_structure": [],
    "deployment": {{
      "containerization": "",
      "orchestration": "",
      "ci_cd": ""
    }},
    "security": {{
      "authentication": "",
      "authorization": "",
      "encryption": ""
    }},
    "scalability": {{
      "load_balancer": "",
      "horizontal_scaling": "",
      "caching": ""
    }}
  }}
}}
"""

    response = llm.invoke(prompt)

    text = response.content.strip()

    text = (
        text.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:
        architecture = json.loads(text)

    except json.JSONDecodeError as e:
        raise Exception(
            f"""

Architect Agent returned invalid JSON.

JSON Error:
{e}

Returned Text:

{text}

"""
        )

    return {
        "architecture": architecture
    }


# ==========================================================
# GRAPH
# ==========================================================

graph = StateGraph(ArchitectState)

graph.add_node("architect", architect_node)

graph.set_entry_point("architect")

graph.add_edge("architect", END)

architect_graph = graph.compile()


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    state = {

        "user_request": """
Build an AI Resume Analyzer.

The application should

- Analyze resumes
- Calculate ATS score
- Suggest improvements
- Recommend jobs
- Generate cover letters
- Login / Signup
- Dashboard
""",

        "business_plan": {
            "project_name": "AI Resume Analyzer",
            "summary": "AI-powered resume analysis platform",
            "goals": [
                "Analyze resumes",
                "Improve ATS score",
                "Generate cover letters"
            ],
            "priority": "High",
            "estimated_complexity": "High"
        },

        "product_requirements": {
            "prd": {
                "features": [
                    "Resume Parsing",
                    "ATS Scoring",
                    "Job Recommendation",
                    "Cover Letter Generation",
                    "Dashboard"
                ],
                "constraints": [
                    "Support PDF",
                    "Secure",
                    "Scalable"
                ]
            }
        },

        "architecture": {}
    }

    result = architect_graph.invoke(state)

    print("\n========== ARCHITECTURE ==========\n")

    print(json.dumps(result["architecture"], indent=4))