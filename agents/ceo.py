import os
import json
from typing import TypedDict, List

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


# -----------------------------
# State
# -----------------------------
class CEOState(TypedDict):
    user_request: str
    business_plan: dict
    agents_required: List[str]


# -----------------------------
# LLM
# -----------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)


# -----------------------------
# CEO Node
# -----------------------------
def ceo_node(state: CEOState):

    prompt = f"""
You are the CEO of an elite software company.

A client has requested:

{state["user_request"]}

Your responsibilities:

1. Understand the client's vision.
2. Infer missing requirements.
3. Decide the required engineering teams.
4. Create a high-level roadmap.
5. Return ONLY valid JSON.

Available Agents:

- Product Manager
- Architect
- Backend Engineer
- Frontend Engineer
- QA Engineer
- Security Engineer
- DevOps Agent
- Reviewer Agent
- Documentation Agent

Return ONLY this JSON structure.

{{
    "project_name": "",
    "summary": "",
    "goals": [],
    "required_agents": [],
    "priority": "",
    "estimated_complexity": "",
    "roadmap": [
        {{
            "phase": 1,
            "title": ""
        }}
    ]
}}

DO NOT add markdown.
DO NOT add explanation.
DO NOT wrap in ```json.
"""

    response = llm.invoke(prompt)

    text = response.content.strip()

    # Remove markdown if Gemini still returns it
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        plan = json.loads(text)

    except Exception:
        raise Exception(f"Gemini did not return valid JSON:\n\n{text}")

    return {
        "business_plan": plan,
        "agents_required": plan["required_agents"],
    }


# -----------------------------
# Graph
# -----------------------------
graph = StateGraph(CEOState)

graph.add_node("CEO", ceo_node)

graph.set_entry_point("CEO")

graph.add_edge("CEO", END)

ceo_graph = graph.compile()


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":

    state = {
        "user_request": """
Build an AI Resume Analyzer.

The application should:

- Analyze resumes
- Score ATS compatibility
- Recommend improvements
- Suggest jobs
- Generate cover letters
- Allow login and dashboard
""",
        "business_plan": {},
        "agents_required": [],
    }

    result = ceo_graph.invoke(state)

    print("\n========== CEO PLAN ==========\n")

    print(json.dumps(result["business_plan"], indent=4))

    print("\n========== AGENTS ==========\n")

    for agent in result["agents_required"]:
        print("-", agent)