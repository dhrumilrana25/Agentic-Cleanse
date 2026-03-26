import streamlit as st
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver 
from agents import analyze_data_node, write_code_node, security_critic_node, execute_code_node 

# 1. THE STATE (The Factory Clipboard)
class DataCleanseState(TypedDict):
    dataset_path: str        
    user_instructions: str     
    cleaning_plan: str  
    python_code: str         
    errors: List[str]        
    is_cleaned: bool
    retry_count: int # Track attempts to fix bugs

# 2. THE ROUTER (The Circuit Breaker)
def route_after_execution(state):
    if state.get("is_cleaned"):
        return END
    
    # If we fail 3 times, stop so we don't waste API tokens
    if state.get("retry_count", 0) >= 3:
        return END
        
    return "engineer"

# 3. THE CACHED GRAPH
@st.cache_resource
def get_graph():
    workflow = StateGraph(DataCleanseState)

    # Add all 4 specialized worker nodes
    workflow.add_node("analyzer", analyze_data_node)
    workflow.add_node("engineer", write_code_node)
    workflow.add_node("security", security_critic_node)
    workflow.add_node("executor", execute_code_node)

    # Define the assembly line
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "engineer")
    workflow.add_edge("engineer", "security")
    
    # After security check, we PAUSE for human approval before executor
    workflow.add_edge("security", "executor")

    # Decision point after execution
    workflow.add_conditional_edges("executor", route_after_execution)

    memory = MemorySaver()
    
    # --- CRITICAL: Pause for Human review right before Agent 3 runs code ---
    return workflow.compile(checkpointer=memory, interrupt_before=["executor"])

# Create the globally accessible 'app'
app = get_graph()