from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
import os

# 1. Define the SentioVault State
# This dictionary is passed between every node in the graph.
class SentioState(TypedDict):
    query: str                   # The user's financial question
    context: Optional[str]        # Data retrieved from Weaviate
    cognitive_load: float         # Current user stress level from dataset
    decision_quality: float       # Quality of the current financial path
    final_insight: Optional[str]  # The final answer for the user

# 2. Define the Nodes (The 'Skills')

def researcher_node(state: SentioState):
    """
    Skill: Queries Weaviate to find the relevant 2024-2025 transaction data.
    """
    print("--- SEARCHING THE VAULT ---")
    # Here you would call your Weaviate query logic
    # Mocking the retrieval for now:
    retrieved_data = "Transaction ID 123: $500 Investment. Load: 0.85"
    return {"context": retrieved_data, "cognitive_load": 0.85}

def analyzer_node(state: SentioState):
    """
    Skill: Evaluates the retrieved data against financial best practices.
    """
    print("--- ANALYZING FINANCIAL LOGIC ---")
    insight = f"Based on your high load ({state['cognitive_load']}), I recommend a simplified auto-save plan."
    return {"final_insight": insight}

def compliance_node(state: SentioState):
    """
    Skill: A high-security node triggered only for high-risk/high-load scenarios.
    """
    print("--- SECURITY & COMPLIANCE CHECK ---")
    return {"final_insight": "SECURITY ALERT: High stress detected. Pausing complex trades."}

# 3. Define the Router (Conditional Logic)

def should_check_compliance(state: SentioState):
    """
    If cognitive load is > 0.8, route to compliance for safety.
    """
    if state["cognitive_load"] > 0.8:
        return "compliance"
    return "analyze"

# 4. Build the Graph

workflow = StateGraph(SentioState)

# Add our nodes
workflow.add_node("research", researcher_node)
workflow.add_node("analyze", analyzer_node)
workflow.add_node("compliance", compliance_node)

# Set the entry point
workflow.set_entry_point("research")

# Define the path with a Conditional Edge
workflow.add_conditional_edges(
    "research",
    should_check_compliance,
    {
        "compliance": "compliance",
        "analyze": "analyze"
    }
)

# Connect everything to the end
workflow.add_edge("analyze", END)
workflow.add_edge("compliance", END)

# Compile the SentioVault Orchestrator
sentio_app = workflow.compile()