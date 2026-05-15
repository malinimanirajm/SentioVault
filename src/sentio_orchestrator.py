import os
import weaviate
from weaviate.classes.query import Filter
from typing import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_aws import ChatBedrock

load_dotenv()

# --- 1. State Definition ---
class SentioState(TypedDict):
    user_query: str
    user_id: str      # Tracks which user is asking
    category: str     # Tracks the specific filter
    context: str
    analysis: str
    reflection_count: int
    is_cached: bool
    final_output: str

# --- 2. AWS Bedrock Setup ---
llm = ChatBedrock(
    model_id="amazon.nova-micro-v1:0",
    model_kwargs={"temperature": 0},
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# --- 3. Nodes ---

def cache_check_node(state: SentioState):
    client = weaviate.connect_to_local(port=int(os.getenv("WEAVIATE_PORT", 8081)))
    try:
        cache = client.collections.get("SentioCache")
        
        # STEP 1 IMPLEMENTED: Strict multi-tenant isolation for the cache layer
        result = cache.query.near_text(
            query=state["user_query"], 
            limit=1,
            filters=Filter.by_property("user_id").equal(state["user_id"])
        )
        
        if result.objects:
            return {"final_output": result.objects[0].properties["response"], "is_cached": True}
        return {"is_cached": False}
    finally:
        client.close()

def researcher_node(state: SentioState):
    client = weaviate.connect_to_local(port=int(os.getenv("WEAVIATE_PORT", 8081)))
    try:
        vault = client.collections.get("SentioTransaction")

        # CRITICAL: Pre-filter by User_ID and Category
        response = vault.query.near_text(
            query=state["user_query"],
            limit=15,
            filters=Filter.all_of([
                Filter.by_property("user_id").equal(state["user_id"]),
                Filter.by_property("category").equal(state["category"])
            ])
        )

        context = "\n".join([str(o.properties) for o in response.objects])
        return {"context": context, "reflection_count": 0}
    finally:
        client.close()

def analyzer_node(state: SentioState):
    prompt = (
        f"You are Sentio, analyzing data for User: {state['user_id']}.\n"
        f"Context (Transactions & HCI Metrics):\n{state['context']}\n\n"
        f"User Query: {state['user_query']}\n"
        "Instructions: Summarize spending. If 'cognitive_load_score' is high (>0.7), "
        "suggest a simpler financial view or automated budgeting to reduce stress."
    )
    res = llm.invoke(prompt)
    return {"analysis": res.content}

def reflection_node(state: SentioState):
    prompt = (
        f"Critique this analysis: '{state['analysis']}'\n"
        f"Based ONLY on this data: {state['context']}\n\n"
        "Rules:\n1. Verify math.\n2. Ensure the advice matches the category requested.\n"
        "3. Keep it concise."
    )
    res = llm.invoke(prompt)
    return {"analysis": res.content, "reflection_count": state["reflection_count"] + 1}

# --- 4. Routing & Graph Construction ---

def should_reflect(state: SentioState):
    return "reflect" if state["reflection_count"] < 1 else "end"

def cache_router(state: SentioState):
    return END if state["is_cached"] else "research"

builder = StateGraph(SentioState)
builder.add_node("cache", cache_check_node)
builder.add_node("research", researcher_node)
builder.add_node("analyze", analyzer_node)
builder.add_node("reflect", reflection_node)

builder.set_entry_point("cache")
builder.add_conditional_edges("cache", cache_router, {"research": "research", END: END})
builder.add_edge("research", "analyze")
builder.add_conditional_edges("analyze", should_reflect, {"reflect": "reflect", "end": END})
builder.add_edge("reflect", END)

memory = MemorySaver()
sentio_app = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    # Local Test Case
    test_inputs = {
        "user_query": "How is my grocery spending looking?",
        "user_id": "user_123", # Make sure this exists in your CSV
        "category": "Groceries"
    }
    config = {"configurable": {"thread_id": "test_run"}}
    for event in sentio_app.stream(test_inputs, config):
        print(event)