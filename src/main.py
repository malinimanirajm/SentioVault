from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.sentio_orchestrator import sentio_app
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"

app = FastAPI(title="Sentio Vault API", version="1.0.0")

# Define the request structure
class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"

# Define the response structure
class QueryResponse(BaseModel):
    analysis: str
    is_cached: bool

@app.post("/ask", response_model=QueryResponse)
async def ask_sentio(request: QueryRequest):
    try:
        # Generate a thread ID for LangGraph persistence
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        
        # Run the agentic loop
        inputs = {"user_query": request.query}
        result = sentio_app.invoke(inputs, config)
        
        return QueryResponse(
            analysis=result["analysis"],
            is_cached=result.get("is_cached", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)