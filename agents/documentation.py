# agents/documentation.py
import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class DocState(TypedDict):
    user_request: str
    business_plan: dict
    architecture: dict
    documentation_docs: dict

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
)

def doc_node(state: DocState):
    prompt = f"""
You are a Lead Documentation Specialist.

Your task is to write detailed developer setup guides, deployment commands, and architectural documentation.

Given:
- USER REQUEST: {state["user_request"]}
- BUSINESS PLAN: {json.dumps(state.get("business_plan", {}), indent=2)}
- ARCHITECTURE: {json.dumps(state.get("architecture", {}), indent=2)}

Return ONLY valid JSON matching this schema:

{{{{
    "documentation_docs": {{{{
        "api_docs_url": "e.g., /api/docs (Swagger-UI)",
        "setup_guide": [
            "1. Clone repository and run npm install / pip install",
            "2. Copy .env.example to .env and configure environment variables",
            "3. Run docker-compose up to start database and services"
        ],
        "deployment_steps": [
            "docker build -t app-image .",
            "kubectl apply -f k8s/deployment.yaml"
        ],
        "architecture_summary": "Description of the system architecture flow"
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
        documentation_docs = json.loads(text)
    except json.JSONDecodeError as e:
        raise Exception(f"Documentation Agent returned invalid JSON. Error: {e} Text: {text}")

    return {"documentation_docs": documentation_docs}

graph = StateGraph(DocState)
graph.add_node("documentation_agent", doc_node)
graph.set_entry_point("documentation_agent")
graph.add_edge("documentation_agent", END)
documentation_graph = graph.compile()
