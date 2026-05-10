import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentio_orchestrator import sentio_app
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Sentio Vault AWS API")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    analysis: str

@app.post("/ask", response_model=QueryResponse)
async def ask_sentio(request: QueryRequest):
    try:
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = sentio_app.invoke({"user_query": request.query}, config)
        return QueryResponse(analysis=result["analysis"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)