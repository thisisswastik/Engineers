# agents/coder.py
import os
import json
from typing import TypedDict, List
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage


class CoderState(TypedDict):
    user_request: str
    architecture: str
    database_design: str
    backend_design: str
    frontend_design: str
    coder_logs: List[str]


async def frontend_coder_node(state: CoderState, pro_llm, tools):
    """Generates a production React + TypeScript + Vite frontend application."""
    print("\n[Frontend Coder Agent (Gemini 2.5 Pro)] Generating React UI...")
    agent = create_react_agent(pro_llm, tools)

    prompt = f"""
You are a Senior Frontend Engineer Agent.
Your task is to build a complete, interactive, production-grade Frontend Web Application in React + TypeScript + Vite.

FRONTEND ARCHITECTURE SPECIFICATION:
{json.dumps(state.get('frontend_design', {}), indent=2)}

INSTRUCTIONS:
1. Use your terminal and filesystem tools (`write_file`, `create_directory`, `exec`).
2. Scaffold the project under `test_project/generated-app/frontend/`.
3. Create production components in `src/App.tsx` and `src/components/` with complete state hooks, event handlers, and styling.
4. DO NOT use placeholders like `// TODO: implement later`. Write full working logic.
5. When completely finished, output a summary of frontend components created.
"""
    result = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
    final_response = result["messages"][-1].content
    return {"coder_logs": state.get("coder_logs", []) + [f"[Frontend Coder]: {final_response}"]}


async def backend_coder_node(state: CoderState, pro_llm, tools):
    """Generates a production Node.js / Express REST API backend."""
    print("\n[Backend Coder Agent (Gemini 2.5 Pro)] Generating Node.js REST API...")
    agent = create_react_agent(pro_llm, tools)

    prompt = f"""
You are a Senior Backend & API Engineer Agent.
Your task is to implement the backend REST API microservices according to the backend design spec.

BACKEND DESIGN SPECIFICATION:
{json.dumps(state.get('backend_design', {}), indent=2)}

DATABASE SPECIFICATION:
{json.dumps(state.get('database_design', {}), indent=2)}

INSTRUCTIONS:
1. Use your tools (`write_file`, `create_directory`) to create backend controllers, models, and routes under `test_project/generated-app/services/`.
2. Write production server code with input validation, route handlers, and database connections.
3. Include a `package.json` with all necessary dependencies.
4. DO NOT use placeholders. Write full working logic.
5. When finished, output a summary of backend files created.
"""
    result = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
    final_response = result["messages"][-1].content
    return {"coder_logs": state.get("coder_logs", []) + [f"[Backend Coder]: {final_response}"]}


async def full_stack_coder_node(state: CoderState, pro_llm, tools):
    """
    Runs both frontend and backend coder agents sequentially.
    This is the node wired into the main pipeline graph.
    """
    print("\n[Full-Stack Coder] Running Backend Coder first, then Frontend Coder...")

    # Phase 2a: Backend
    backend_result = await backend_coder_node(state, pro_llm, tools)
    # Merge logs back into state so frontend coder sees the accumulated logs
    state_with_backend = {**state, "coder_logs": backend_result["coder_logs"]}

    # Phase 2b: Frontend
    frontend_result = await frontend_coder_node(state_with_backend, pro_llm, tools)

    return {"coder_logs": frontend_result["coder_logs"]}