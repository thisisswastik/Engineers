# this file is used for self correction loops, parallel execution, HITL
import os 
import json 
import asyncio 
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.callbacks import AsyncCallbackHandler

# importing existing tools and agents from the repo
from mcps.combined_tools import get_combined_llm_with_tools

import logging
logging.getLogger("google.genai").setLevel(logging.ERROR)


# importing all agents 
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
import agents.devops as devops

load_dotenv()

# maximum number of automated self correction feedback
MAX_REVISIONS = 2

# Enhanced pipeline state
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
    coder_logs: List[str]
    security_report: dict
    devops_config: dict
    review_feedback: dict
    documentation_docs: dict
    # below variables are for feedback loop and HITL
    revision_count: int
    feedback_history: List[str]
    approved_by_human: bool

# Callback handler for real-time logging
class ToolLoggingHandler(AsyncCallbackHandler):
    async def on_tool_start(self, serialized: dict, input_str: str, **kwargs)-> None:
        name = serialized.get("name", "Unknown Tool")
        print(f"\n[Tool Run] Executing '{name}' with input: {input_str[:150]}...")
    async def on_tool_end(self, output:str, **kwargs)-> None:
        print(f"[Tool Result] {str(output)[:200]}...")

# conditional route: self-correction check

def should_revise_code(state: PipelineState)-> str:
    """
    Inspects reviewer feedback and determines whether to route back to the coder
    node for self-correction or finish the graph
    """
    review_feedback = state.get("review_feedback", {}).get("review_feedback",{})
    criticisms = review_feedback.get("criticisms",[])
    revision_count = state.get("revision_count",0)

    # check for high or critical severity issues
    has_critical_issues = any(c.get("severity","").lower() in ["high","critical"] for c in criticisms)
    print(f"\n--- [Router Evaluation] Revision Count: {revision_count}/{MAX_REVISIONS} ---")
    print(f"--- [Router Evaluation] Critical Issues Found: {has_critical_issues} ---")

    if has_critical_issues and revision_count < MAX_REVISIONS:
        print("--> [Decision] Self-correction triggered! Routing back to coder node")
        return "coder"
    print("--> [Decision] Quality threshold met or max revisions reached. Proceeding to documentation")
    return "documentation_agent"
    
# Helper node to increment revision counter before re-running coder

async def increment_revision_node(state: PipelineState)->dict:
    current_count = state.get("revision_count",0)
    criticisms=state.get("review_feedback",{}).get("review_feedback",{}).get("criticisms",[])
    history = state.get("feedback_history",[])
    
    feedback_summary = f"Revision #{current_count+1} Feedback: {json.dumps(criticisms)}"
    history.append(feedback_summary)

    return{
        "revision_count": current_count+1,
        "feedback_history": history,
    }
# Pipeline construction 

async def build_pipeline():
    llm_with_tools, tools = await get_combined_llm_with_tools()

    async def run_coder_node(state):
        return await coder.coder_node(state, llm_with_tools, tools)
        
    workflow = StateGraph(PipelineState)

    # Register Nodes 
    workflow.add_node("ceo", ceo.ceo_node)
    workflow.add_node("product_manager", pm.pm_node)
    workflow.add_node("architect", arch.architect_node)

    # design phase (parallel nodes)
    workflow.add_node("backend_engineer", backend.backend_node)
    workflow.add_node("database_engineer", db.database_node)
    workflow.add_node("frontend_engineer", frontend.frontend_node)

    # Join / QA phase
    workflow.add_node("qa_engineer", qa.qa_node)

    # execution and review phase
    workflow.add_node("coder", run_coder_node)
    workflow.add_node("devops", devops.devops_node)
    workflow.add_node("security_engineer", security.security_node)
    workflow.add_node("reviewer", reviewer.reviewer_node)
    workflow.add_node("increment_revision", increment_revision_node)
    workflow.add_node("documentation_agent", doc.doc_node)

    # ---------------------------------------------------------------
    # Graph Edges & Flow Control
    # ---------------------------------------------------------------
    workflow.set_entry_point("ceo")
    workflow.add_edge("ceo", "product_manager")
    workflow.add_edge("product_manager", "architect")
    # 1. PARALLEL FAN-OUT: Architect -> Backend, DB, Frontend simultaneously
    workflow.add_edge("architect", "backend_engineer")
    workflow.add_edge("architect", "database_engineer")
    workflow.add_edge("architect", "frontend_engineer")
    # 2. PARALLEL FAN-IN: Backend, DB, Frontend -> QA Engineer
    workflow.add_edge("backend_engineer", "qa_engineer")
    workflow.add_edge("database_engineer", "qa_engineer")
    workflow.add_edge("frontend_engineer", "qa_engineer")
    # QA -> Coder
    workflow.add_edge("qa_engineer", "coder")
    
    # Coder -> DevOps -> Security -> Reviewer
    workflow.add_edge("coder", "devops")
    workflow.add_edge("devops", "security_engineer")
    workflow.add_edge("security_engineer", "reviewer")
    # 3. CONDITIONAL SELF-CORRECTION EDGE
    # Evaluates reviewer feedback. If revision needed -> increment_revision -> coder. Else -> documentation.
    workflow.add_conditional_edges(
        "reviewer",
        should_revise_code,
        {
            "coder": "increment_revision",
            "documentation_agent": "documentation_agent"
        }
    )
    workflow.add_edge("increment_revision", "coder")
    workflow.add_edge("documentation_agent", END)
    # 4. HUMAN-IN-THE-LOOP CHECKPOINTING
    # Setting up in-memory checkpointer & breakpoint before Coder node
    memory = MemorySaver()
    compiled_graph = workflow.compile(
        checkpointer=memory,
        interrupt_before=["coder"]  # Pause pipeline here for human approval
    )
    
    return compiled_graph
# -------------------------------------------------------------------
# 5. Execution Routine with Human Interruption Handling
# -------------------------------------------------------------------
async def run_pipeline():
    pipeline_graph = await build_pipeline()
    
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
        "documentation_docs": {},
        "revision_count": 0,
        "feedback_history": [],
        "approved_by_human": False
    }
    config = {
        "configurable": {"thread_id": "session-run-001"},
        "callbacks": [ToolLoggingHandler()]
    }
    print("\n" + "="*60)
    print("Launching AI Engineering Organization (Part 1 Architecture)...")
    print("="*60)

    # -------------------------------------------------------------------
    # PHASE 1: Run graph until hit breakpoint (before 'coder')
    # -------------------------------------------------------------------
    async for event in pipeline_graph.astream(initial_state, config, stream_mode="updates"):
        for node_name, state_update in event.items():
            print(f"[Finished Node] {node_name.upper()}")

    # Inspect current state at breakpoint
    state_snapshot = await pipeline_graph.aget_state(config)
    next_nodes = state_snapshot.next

    if "coder" in next_nodes:
        # Extract planning deliverables from graph state snapshot
        values = state_snapshot.values
        
        print("\n" + "="*70)
        print("  HUMAN-IN-THE-LOOP INTERRUPT: PLANNING PHASE COMPLETE  ")
        print("="*70)
        
        print("\n--- 1. PRODUCT REQUIREMENTS ---")
        print(json.dumps(values.get("product_requirements", {}), indent=2))

        print("\n--- 2. SYSTEM ARCHITECTURE ---")
        print(json.dumps(values.get("architecture", {}), indent=2))

        print("\n--- 3. DATABASE DESIGN ---")
        print(json.dumps(values.get("database_design", {}), indent=2))

        print("\n--- 4. BACKEND & FRONTEND DESIGN ---")
        print(json.dumps(values.get("backend_design", {}), indent=2))
        print(json.dumps(values.get("frontend_design", {}), indent=2))

        print("\n--- 5. QA STRATEGY ---")
        print(json.dumps(values.get("qa_plan", {}), indent=2))

        print("\n" + "!"*70)
        print("Review the planning specification above.")
        print("!"*70)

        user_approval = input("\nDo you approve the planning specs to start coding? (y/n): ")
        
        if user_approval.lower().strip() == 'y':
            print("\n[Human Approved] Resuming pipeline to start file generation...\n")
            # PHASE 2: Resume execution passing None as state to continue from checkpoint
            async for event in pipeline_graph.astream(None, config, stream_mode="updates"):
                for node_name, state_update in event.items():
                    print(f"[Finished Node] {node_name.upper()}")
        else:
            print("\n[Pipeline Aborted] Human rejected planning specs.")
            return

    print("\n" + "="*60)
    print("PIPELINE EXECUTION COMPLETE - ALL DELIVERABLES GENERATED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_pipeline())

