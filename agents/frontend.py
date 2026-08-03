import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class FrontendState(TypedDict):
    user_request: str
    business_plan: dict
    product_requirements: dict
    architecture: dict
    frontend_design: dict


def _get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2
    )


def frontend_node(state: FrontendState):
    llm = _get_llm()
    prompt = f"""
You are a Principal Frontend Engineer.
Your task is to produce a Frontend Engineering Design Document.
Given:
- USER REQUEST: {state["user_request"]}
- PRODUCT REQUIREMENTS: {json.dumps(state.get("product_requirements", {}), indent=2)}
- ARCHITECTURE: {json.dumps(state.get("architecture", {}), indent=2)}
Return ONLY valid JSON matching this schema:
{{{{
    "frontend_design": {{{{
        "framework": "React / Next.js / Vue / Angular etc.",
        "ui_library": "TailwindCSS, Material UI, Shadcn/ui etc.",
        "state_management": "Redux, Zustand, Context API etc.",
        "routes": [
            {{{{
                "path": "/dashboard",
                "page_name": "DashboardPage",
                "components": ["OverviewCard", "StatsChart", "ActivityList"],
                "functionality": "Displays ATS metrics and recommended jobs."
            }}}}
        ],
        "folder_structure": ["src/", "src/components/", "src/pages/"],
        "styling_system": {{{{
            "theme": "Dark/Light mode support",
            "responsive_strategy": "Mobile-first layout grid"
        }}}},
        "performance_optimization": [
            "Code splitting via dynamic imports",
            "Lazy loading images",
            "Caching API responses client-side"
        ]
    }}}}
}}}}
IMPORTANT:
- Return ONLY valid JSON.
- DO NOT wrap the JSON inside markdown code blocks (```json).
- Every key/string must be in double quotes. No trailing commas.
"""
    response = llm.invoke(prompt)
    text = response.content.strip().replace("```json", "").replace("```", "").strip()
    try:
        frontend_design = json.loads(text)
    except json.JSONDecodeError as e:
        raise Exception(f"Frontend Agent returned invalid JSON. Error: {e} Text: {text}")
    return {"frontend_design": frontend_design}


if __name__ == "__main__":
    graph = StateGraph(FrontendState)
    graph.add_node("frontend_engineer", frontend_node)
    graph.set_entry_point("frontend_engineer")
    graph.add_edge("frontend_engineer", END)
    frontend_graph = graph.compile()