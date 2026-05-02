import weaviate
import os
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

class SentioState(TypedDict):
    query: str
    context: Optional[str]
    cognitive_load: float
    final_insight: Optional[str]
    is_relevant: bool

# --- NODES ---

def researcher_node(state: SentioState):
    client = weaviate.connect_to_local()
    collection = client.collections.get("SentioTransaction")
    
    print(f"--- VAULT SEARCH: {state['query']} ---")
    response = collection.query.near_text(query=state['query'], limit=3)
    
    if not response.objects:
        client.close()
        return {"context": "No data found.", "cognitive_load": 0.0, "is_relevant": False}

    context_str = "\n".join([f"{o.properties['category']}: ${o.properties['amount']}" for o in response.objects])
    max_load = max([o.properties['cognitive_load_score'] for o in response.objects])
    
    client.close()
    return {"context": context_str, "cognitive_load": max_load, "is_relevant": True}

def grader_node(state: SentioState) -> Literal["relevant", "not_relevant"]:
    """Reflective check: Did the search yield actual value?"""
    if state["is_relevant"] and state["context"] != "No data found.":
        print("--- GRADE: RELEVANT ---")
        return "relevant"
    print("--- GRADE: IRRELEVANT ---")
    return "not_relevant"

def compliance_node(state: SentioState):
    print("--- COMPLIANCE ALERT ---")
    return {"final_insight": "⚠️ HIGH STRESS DETECTED. Transaction review paused for safety."}

def analyzer_node(state: SentioState):
    print("--- ANALYZING ---")
    insight = f"Analysis based on Vault data:\n{state['context']}\nStatus: System cleared for advice."
    return {"final_insight": insight}

# --- ROUTING LOGIC ---

def route_based_on_load(state: SentioState):
    return "compliance" if state["cognitive_load"] > 0.8 else "analyze"

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(SentioState)

workflow.add_node("research", researcher_node)
workflow.add_node("analyze", analyzer_node)
workflow.add_node("compliance", compliance_node)

workflow.set_entry_point("research")

# Add the reflective jump
workflow.add_conditional_edges(
    "research", 
    grader_node, 
    {"relevant": "analyze", "not_relevant": END}
)

# Add the safety gate
workflow.add_conditional_edges(
    "analyze", 
    route_based_on_load, 
    {"compliance": "compliance", "analyze": "analyze"}
)

workflow.add_edge("compliance", END)
workflow.add_edge("analyze", END)

# Add Persistence (Memory)
memory = MemorySaver()
sentio_app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # thread_id allows the agent to remember the user across multiple calls
    config = {"configurable": {"thread_id": "user_session_001"}}
    user_query = "Check my spending during high-stress moments."
    
    for event in sentio_app.stream({"query": user_query}, config):
        print(event)