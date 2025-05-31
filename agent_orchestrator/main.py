from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "agent_orchestrator is healthy"}

@app.get("/run-agent")
async def run_agent():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://agent_service:8000/health")
        return {"agent_response": response.json()}

