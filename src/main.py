import uuid
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.sentio_orchestrator import sentio_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable LangSmith Tracing for debugging
os.environ["LANGCHAIN_TRACING_V2"] = "true"

app = FastAPI(
    title="Sentio Vault API", 
    description="Multi-tenant Financial HCI Agent",
    version="2.0.0"
)

# --- 1. Request/Response Schemas ---

class QueryRequest(BaseModel):
    query: str
    user_id: str
    category: str

class QueryResponse(BaseModel):
    analysis: str
    is_cached: bool

# --- 2. API Endpoints ---

@app.get("/")
async def root():
    return {"status": "online", "message": "Sentio Vault is operational."}

@app.post("/ask", response_model=QueryResponse)
async def ask_sentio(request: QueryRequest):
    try:
        # Generate a unique thread ID for this specific user session
        # In a production app, you might use the user_id as the thread_id
        config = {"configurable": {"thread_id": f"session_{uuid.uuid4()}"}}
        
        # Initialize the graph state with the new required filters
        inputs = {
            "user_query": request.query,
            "user_id": request.user_id,
            "category": request.category
        }
        
        # Execute the LangGraph Agentic Loop
        result = sentio_app.invoke(inputs, config)
        
        return QueryResponse(
            analysis=result.get("analysis") or result.get("final_output"),
            is_cached=result.get("is_cached", False)
        )

    except Exception as e:
        # Catching and reporting errors for debugging
        print(f"❌ API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error occurred.")

# --- 3. Execution ---

if __name__ == "__main__":
    import uvicorn
    # Running on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)