# main.py
import os 
import json
import asyncio
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.callbacks import AsyncCallbackHandler

# Importing tools 
from mcps.combined_tools import get_combined_llm_with_tools

# Importing all agents 
import agents.ceo as ceo
import agents.product_manager as pm 
import agents.architect as arch
import agents.backend as backend 
import agents.frontend as frontend
import agents.qa as qa 
import agents.security as security 
import agents.coder as coder
import agents.reviewer as reviewer
import agents.documentation as doc 
import agents.database as db

load_dotenv()

# 1. Real-time Tool Execution Callback Handler
class ToolLoggingHandler(AsyncCallbackHandler):
    async def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        name = serialized.get("name", "Unknown Tool")
        print(f"\n[Tool Run] Executing tool '{name}' with input: {input_str}")

    async def on_tool_end(self, output: str, **kwargs) -> None:
        # Prints first 300 characters of the tool output to avoid stdout flooding
        print(f"[Tool Result] Output: {str(output)[:300]}...")

class PipelineState(TypedDict):
    user_request: str
    business_plan: dict
    agents_required: List[str]
    product_requirements: dict
    architecture: dict
    backend_design: dict
    database_design: dict
    frontend_design: dict
    qa_plan: dict
    coder_logs: List[str]      # Track logs from the Coder ReAct loop
    security_report: dict
    devops_config: dict
    review_feedback: dict
    documentation_docs: dict

async def run_pipeline():
    llm_with_tools, tools = await get_combined_llm_with_tools()
    
    # The planning agents use their own default LLM, we only pass tools to the coder agent.

    # Helper function to invoke the Coder ReAct loop with the tools list
    async def run_coder_node(state):
        return await coder.coder_node(state, llm_with_tools, tools)

    # Initialize graph
    workflow = StateGraph(PipelineState)

    # Adding nodes
    workflow.add_node("ceo", ceo.ceo_node)
    workflow.add_node("product_manager", pm.pm_node)
    workflow.add_node("architect", arch.architect_node)
    workflow.add_node("backend_engineer", backend.backend_node)
    workflow.add_node("database_engineer", db.database_node)
    workflow.add_node("frontend_engineer", frontend.frontend_node)
    workflow.add_node("qa_engineer", qa.qa_node)
    workflow.add_node("coder", run_coder_node)  # Register coder node
    workflow.add_node("security_engineer", security.security_node)
    workflow.add_node("reviewer", reviewer.reviewer_node)
    workflow.add_node("documentation_agent", doc.doc_node)

    # Defining edges (sequential flow)
    workflow.set_entry_point("ceo")
    workflow.add_edge("ceo", "product_manager")
    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "backend_engineer")
    workflow.add_edge("backend_engineer", "database_engineer")
    workflow.add_edge("database_engineer", "frontend_engineer")
    workflow.add_edge("frontend_engineer", "qa_engineer")
    workflow.add_edge("qa_engineer", "coder")              # Route to Coder
    workflow.add_edge("coder", "security_engineer")        # Route from Coder to Security
    workflow.add_edge("security_engineer", "reviewer")
    workflow.add_edge("reviewer", "documentation_agent")
    workflow.add_edge("documentation_agent", END)

    pipeline_graph = workflow.compile()
    
    initial_state = {
        "user_request": """
        Build me a food delivery application.
        The application should support:
        - Customer login and browse restaurants
        - Cart management and order checkout
        - Restaurant dashboard to accept/reject orders
        - Delivery driver app with live status updates
        """,
        "business_plan": {},
        "agents_required": [],
        "product_requirements": {},
        "architecture": {},
        "backend_design": {},
        "database_design": {},
        "frontend_design": {},
        "qa_plan": {},
        "coder_logs": [],
        "security_report": {},
        "devops_config": {},
        "review_feedback": {},
        "documentation_docs": {}
    }
    
    print("\n" + "="*50)
    print("Launching AI Software Engineering Organization Pipeline...")
    print("="*50)
    
    # Register callbacks and stream updates
    config = {"callbacks": [ToolLoggingHandler()]}
    
    async for chunk in pipeline_graph.astream(initial_state, config=config, stream_mode="updates"):
        for node_name, state_update in chunk.items():
            print(f"\n* [Finished Node] {node_name.upper()} has completed execution.")
            
            # Print a quick preview of what key this node generated:
            for key, val in state_update.items():
                if val:
                    print(f"   -> Key populated: '{key}'")

    print("\n" + "="*50)
    print("PIPELINE EXECUTION COMPLETE - ALL DELIVERABLES GENERATED")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_pipeline())
