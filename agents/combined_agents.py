from typing import TypedDict, List
import json 
from langgraph.graph import StateGraph, END 
# pyrefly: ignore [missing-import]
from ceo import ceo_node    
# pyrefly: ignore [missing-import]
from product_manager import pm_node
# pyrefly: ignore [missing-import]
from architect import architect_node
# pyrefly: ignore [missing-import]
from backend import backend_node 

class OverallState(TypedDict):
    user_request:str
    business_plan:dict
    agents_required: List[str]
    product_requirements: dict
    architecture:dict
    backend_design: dict

workflow = StateGraph(OverallState)

workflow.add_node("ceo",ceo_node)
workflow.add_node("product_manager",pm_node)
workflow.add_node("architect",architect_node)
workflow.add_node("backend",backend_node)

workflow.set_entry_point("ceo")
workflow.add_edge("ceo","product_manager")
workflow.add_edge("product_manager","architect")
workflow.add_edge("architect","backend")
workflow.add_edge("backend",END)

combined_agents_graph= workflow.compile()

if __name__ == "__main__":
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
        "backend_design": {}
    }
    print("Starting AI Software Engineering Team Pipeline...")
    result = combined_agents_graph.invoke(initial_state)
    print("\n" + "="*40 + "\nFINAL OUTPUTS GENERATED\n" + "="*40)
    print("\n--- 1. CEO Business Plan ---")
    print(json.dumps(result["business_plan"], indent=2))
    print("\n--- 2. Product Requirements (PRD) ---")
    print(json.dumps(result["product_requirements"], indent=2))
    print("\n--- 3. System Architecture ---")
    print(json.dumps(result["architecture"], indent=2))
    print("\n--- 4. Backend Design Document ---")
    print(json.dumps(result["backend_design"], indent=2))