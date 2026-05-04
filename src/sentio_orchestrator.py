# ... (imports and SentioState remains the same)

def analyzer_node(state: SentioState):
    print("--- ANALYZING ---")
    # We move the logic: Analyzer now just prepares the data
    insight = f"Analysis based on Vault data:\n{state['context']}\nStatus: System cleared for advice."
    return {"final_insight": insight}

# --- ROUTING LOGIC ---

def route_based_on_load(state: SentioState):
    # Logic: If load is high, go to compliance. If not, we are done.
    if state["cognitive_load"] > 0.8:
        return "compliance"
    return END # End here so we don't loop back to analyze

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(SentioState)

workflow.add_node("research", researcher_node)
workflow.add_node("analyze", analyzer_node)
workflow.add_node("compliance", compliance_node)

workflow.set_entry_point("research")

workflow.add_conditional_edges(
    "research", 
    grader_node, 
    {"relevant": "analyze", "not_relevant": END}
)

workflow.add_conditional_edges(
    "analyze", 
    route_based_on_load, 
    {
        "compliance": "compliance", 
        "end": END # Explicitly map END
    }
)

workflow.add_edge("compliance", END)