"""FastAPI application for the Parliament multi-agent debate system."""

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents import get_default_agents
from debate_orchestrator import DebateOrchestrator

load_dotenv()

app = FastAPI(title="Parliament", description="Multi-agent AI debate system")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebateRequest(BaseModel):
    """Request model for starting a new debate."""

    topic: str


@app.get("/")
async def root() -> dict[str, str]:
    """Return basic API information."""
    return {"message": "Parliament API - Multi-agent debate system"}


@app.post("/debate")
async def start_debate(request: DebateRequest) -> StreamingResponse:
    """Start a new debate with the given topic.

    Returns a streaming response with the debate progress.
    """
    try:
        orchestrator = DebateOrchestrator(get_default_agents())
        return StreamingResponse(
            orchestrator.run_debate(request.topic),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return health status of the API."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
