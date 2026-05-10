import os
import weaviate
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_aws import ChatBedrock
from dotenv import load_dotenv

load_dotenv()

# --- 1. State Definition ---
class SentioState(TypedDict):
    user_query: str
    context: str
    analysis: str
    reflection_count: int
    is_cached: bool

# --- 2. AWS Bedrock Setup ---
llm = ChatBedrock(
    model_id="amazon.nova-micro-v1:0", 
    model_kwargs={"temperature": 0},
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# --- 3. Nodes ---
def researcher_node(state: SentioState):
    client = weaviate.connect_to_local(port=int(os.getenv("WEAVIATE_PORT", 8081)))
    vault = client.collections.get("SentioTransaction")
    
    # Semantic search in local Weaviate
    response = vault.query.near_text(query=state["user_query"], limit=15)
    context = "\n".join([str(o.properties) for o in response.objects])
    client.close()
    return {"context": context, "reflection_count": 0}

def analyzer_node(state: SentioState):
    prompt = f"Analyze these transactions: {state['context']}. Query: {state['user_query']}"
    res = llm.invoke(prompt)
    return {"analysis": res.content}

def reflection_node(state: SentioState):
    prompt = (
        f"Critique this analysis: '{state['analysis']}' using this data: {state['context']}. "
        "Rules: 1. No code. 2. Verify math. 3. Be concise."
    )
    res = llm.invoke(prompt)
    return {"analysis": res.content, "reflection_count": state["reflection_count"] + 1}

# --- 4. Routing Logic ---
def should_reflect(state: SentioState):
    return "reflect" if state["reflection_count"] < 1 else "end"

# --- 5. Graph Construction ---
builder = StateGraph(SentioState)
builder.add_node("research", researcher_node)
builder.add_node("analyze", analyzer_node)
builder.add_node("reflect", reflection_node)

builder.set_entry_point("research")
builder.add_edge("research", "analyze")
builder.add_conditional_edges("analyze", should_reflect, {"reflect": "reflect", "end": END})
builder.add_edge("reflect", END)

memory = MemorySaver()
sentio_app = builder.compile(checkpointer=memory)