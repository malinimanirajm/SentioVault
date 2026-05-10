import os
import weaviate

from typing import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_aws import ChatBedrock

load_dotenv()


# --- 1. State Definition ---

class SentioState(TypedDict):
    user_query: str
    context: str
    analysis: str
    reflection_count: int
    cognitive_load: float
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

    client = weaviate.connect_to_local(
        port=int(os.getenv("WEAVIATE_PORT", 8081))
    )

    try:
        cache = client.collections.get("SentioCache")

        result = cache.query.near_text(
            query=state["user_query"],
            limit=1
        )

        if result.objects:
            return {
                "final_output": result.objects[0].properties["response"],
                "is_cached": True
            }

        return {"is_cached": False}

    finally:
        client.close()


def researcher_node(state: SentioState):

    client = weaviate.connect_to_local(
        port=int(os.getenv("WEAVIATE_PORT", 8081))
    )

    try:
        vault = client.collections.get("SentioTransaction")

        response = vault.query.near_text(
            query=state["user_query"],
            limit=15
        )

        context = "\n".join(
            [str(o.properties) for o in response.objects]
        )

        return {
            "context": context,
            "reflection_count": 0
        }

    finally:
        client.close()


def analyzer_node(state: SentioState):

    prompt = (
        f"Analyze these financial transactions:\n"
        f"{state['context']}\n\n"
        f"User Query: {state['user_query']}"
    )

    res = llm.invoke(prompt)

    return {"analysis": res.content}


def reflection_node(state: SentioState):

    prompt = (
        f"Critique the following financial analysis:\n"
        f"{state['analysis']}\n\n"
        f"Based ONLY on this retrieved data:\n"
        f"{state['context']}\n\n"
        "Rules:\n"
        "1. Do not provide code.\n"
        "2. Verify calculations carefully.\n"
        "3. Keep the answer concise.\n"
        "4. Ensure the response answers the user's question."
    )

    res = llm.invoke(prompt)

    return {
        "analysis": res.content,
        "reflection_count": state["reflection_count"] + 1
    }


# --- 4. Routing Logic ---

def should_reflect(state: SentioState):

    if state["reflection_count"] < 1:
        return "reflect"

    return "end"


def cache_router(state: SentioState):

    if state["is_cached"]:
        return END

    return "research"


# --- 5. Graph Construction ---

builder = StateGraph(SentioState)

builder.add_node("cache", cache_check_node)
builder.add_node("research", researcher_node)
builder.add_node("analyze", analyzer_node)
builder.add_node("reflect", reflection_node)

builder.set_entry_point("cache")

builder.add_conditional_edges(
    "cache",
    cache_router,
    {
        "research": "research",
        END: END
    }
)

builder.add_edge("research", "analyze")

builder.add_conditional_edges(
    "analyze",
    should_reflect,
    {
        "reflect": "reflect",
        "end": END
    }
)

builder.add_edge("reflect", END)


# --- 6. Compile Graph ---

memory = MemorySaver()

sentio_app = builder.compile(
    checkpointer=memory
)


# --- 7. Local Testing ---

if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "user_123"
        }
    }

    query = "Summarize my spending in groceries for 2024."

    for event in sentio_app.stream(
        {"user_query": query},
        config
    ):
        print(event)