import weaviate
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama

# --- 1. State Definition ---
class SentioState(TypedDict):
    user_query: str
    context: str
    analysis: str
    reflection_count: int
    cognitive_load: float
    is_cached: bool
    final_output: str

# --- 2. Local LLM Setup ---
llm = ChatOllama(
    model="llama3.2", 
    temperature=0,
    system="You are Sentio, a precise financial analyst. You double-check your math and never output code unless explicitly asked."
)

# --- 3. Nodes ---

def cache_check_node(state: SentioState):
    client = weaviate.connect_to_local(port=8081)
    cache = client.collections.get("SentioCache")
    
    # Search for similar query (Semantic Match)
    result = cache.query.near_text(query=state["user_query"], limit=1)
    client.close()

    if result.objects:
        return {"final_output": result.objects[0].properties["response"], "is_cached": True}
    return {"is_cached": False}

def researcher_node(state: SentioState):
    client = weaviate.connect_to_local(port=8081)
    vault = client.collections.get("SentioTransaction")
    
    # Retrieve top relevant transactions
    response = vault.query.near_text(query=state["user_query"], limit=15)
    context = "\n".join([str(o.properties) for o in response.objects])
    client.close()
    
    return {"context": context, "reflection_count": 0}

def analyzer_node(state: SentioState):
    prompt = f"Analyze these transactions: {state['context']}. Query: {state['user_query']}"
    res = llm.invoke(prompt)
    return {"analysis": res.content}

def reflection_node(state: SentioState):
    # Refining the prompt to keep the agent focused on data, not code.
    prompt = (
        f"Critique the following financial analysis: '{state['analysis']}' "
        f"based ONLY on this retrieved data: {state['context']}. "
        "Rules: \n"
        "1. Do not provide Python code or script suggestions.\n"
        "2. Check if the math is correct (summing the amounts).\n"
        "3. Ensure the summary is concise and addresses the user's specific query.\n"
        "4. If 'Groceries' were found, list the specific transactions and total."
    )
    res = llm.invoke(prompt)
    return {"analysis": res.content, "reflection_count": state["reflection_count"] + 1}

# --- 4. Routing Logic ---

def should_reflect(state: SentioState):
    if state["reflection_count"] < 1: # Reflect once for accuracy
        return "reflect"
    return "end"

def cache_router(state: SentioState):
    return "research" if not state["is_cached"] else END

# --- 5. Graph Construction ---

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

# Memory for thread-safe persistence
memory = MemorySaver()
sentio_app = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "user_123"}}
    query = "Summarize my spending in groceries for 2024."
    
    for event in sentio_app.stream({"user_query": query}, config):
        print(event)