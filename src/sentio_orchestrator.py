import weaviate
import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

client = weaviate.Client(url=os.getenv("WEAVIATE_URL"))

class SentioState(TypedDict):
    query: str
    context: Optional[str]
    cognitive_load: float
    final_insight: Optional[str]

# --- NODES ---

def researcher_node(state: SentioState):
    """Queries Weaviate for semantic matches."""
    print(f"--- VAULT SEARCH: {state['query']} ---")
    
    response = (
        client.query
        .get("SentioTransaction", ["category", "amount", "cognitive_load_score"])
        .with_near_text({"concepts": [state["query"]]})
        .with_limit(3)
        .do()
    )
    
    results = response.get("data", {}).get("Get", {}).get("SentioTransaction", [])
    if not results:
        return {"context": "No data found.", "cognitive_load": 0.0}

    context_str = "\n".join([f"{r['category']}: ${r['amount']}" for r in results])
    max_load = max([r['cognitive_load_score'] for r in results])
    
    return {"context": context_str, "cognitive_load": max_load}

def analyzer_node(state: SentioState):
    """Standard analysis logic."""
    print("--- ANALYZING ---")
    insight = f"Results:\n{state['context']}\nSuggestion: Your load is stable. Proceed with budget."
    return {"final_insight": insight}

def compliance_node(state: SentioState):
    """High-risk safety logic."""
    print("--- COMPLIANCE ALERT ---")
    return {"final_insight": "ALERT: High stress detected. Complex actions paused for safety."}

# --- ROUTING ---

def should_check_compliance(state: SentioState):
    return "compliance" if state["cognitive_load"] > 0.8 else "analyze"

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(SentioState)
workflow.add_node("research", researcher_node)
workflow.add_node("analyze", analyzer_node)
workflow.add_node("compliance", compliance_node)

workflow.set_entry_point("research")
workflow.add_conditional_edges("research", should_check_compliance, {
    "compliance": "compliance", 
    "analyze": "analyze"
})
workflow.add_edge("analyze", END)
workflow.add_edge("compliance", END)

sentio_app = workflow.compile()

if __name__ == "__main__":
    user_query = "Review my high-stress transactions from last month"
    for output in sentio_app.stream({"query": user_query, "cognitive_load": 0.0}):
        print(output)