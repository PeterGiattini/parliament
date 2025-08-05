# Parliament

A multi-agent AI debate system that generates structured, multi-faceted analysis through intelligent agent interactions.

## Concept

Parliament creates AI agents with distinct perspectives (Economist, Ethicist, Technologist, Sociologist) who debate user questions in a structured three-round format:

1. **Opening Statements**: Each agent independently analyzes the topic
2. **Rebuttal**: Agents engage with each other's arguments sequentially  
3. **Synthesis**: A moderator summarizes key points, areas of agreement, and outstanding questions

## Architecture

- **Backend**: Python FastAPI with LangChain orchestration
- **Frontend**: React with streaming UI
- **AI**: Vertex AI (Gemini 1.5 Pro) for agent responses
- **Structure**: 3-round debate funnel with extensible agent system

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Cloud account with Vertex AI access
- Google Cloud service account key with Vertex AI permissions

### Quick Setup
For the easiest setup experience, use the provided setup script:
```bash
./setup.sh
```

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync  # Install dependencies using uv
```

#### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Variables
Create `.env` files in both `backend/` and `frontend/` directories by copying the example files:

```bash
# Backend
cd backend
cp env.example .env

# Frontend  
cd ../frontend
cp env.example .env
```

**Required backend/.env variables:**
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

**Required frontend/.env variables:**
```
VITE_API_BASE_URL=http://localhost:8000
```

See the `env.example` files for additional optional configuration options.

## Development

### Quick Start
Use the provided startup scripts for the easiest development experience:

```bash
# Simple startup
./start-simple.sh

# Full startup with real-time logs
./start.sh
```

### Manual Development

#### Backend
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

#### Frontend
```bash
cd frontend
npm run dev
```

### Development Tools
- **Dependency Management**: Uses `uv` for Python dependencies
- **Linting**: Uses `ruff` for Python code formatting and linting
- **Type Checking**: TypeScript for frontend type safety

## Services

Once started, you'll have access to:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Backend Health Check**: http://localhost:8000/health

## Additional Documentation

- **Startup Guide**: See `STARTUP.md` for detailed startup instructions and troubleshooting
- **Environment Configuration**: Check `env.example` files for all available configuration options

## Future Roadmap

- Dynamic agent generation
- Multi-model capability  
- Research tools integration
- MCP integration
- Service/API model 
