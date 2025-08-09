# Parliament

A multi-agent AI debate system that generates structured, multi-faceted analysis through intelligent agent interactions.

## Concept

Parliament creates AI agents with distinct perspectives who debate user questions in a structured format. The system supports both built-in expert agents (Economist, Ethicist, Technologist, Sociologist) and custom user-generated agents.

### Debate Structure
Currently implements a 4-round debate format:
1. **Opening Statements**: Each agent independently analyzes the topic
2. **Rebuttal**: Agents engage with each other's arguments sequentially  
3. **Surrebuttal**: Agents defend their positions against critiques
4. **Synthesis**: A moderator summarizes key points, areas of agreement, and outstanding questions

### Key Features
- **Agent Management**: Create, save, and manage custom agents with simple prompts
- **Panel System**: Assemble and save debate panels for reuse
- **Export/Import**: Share agents and panels via JSON export/import
- **Stateful Orchestration**: LangGraph-based, robust, state-driven debate management

## Architecture

- **Backend**: Python FastAPI with LangGraph orchestration
- **Frontend**: React with streaming UI
- **AI**: Vertex AI (Gemini 2.0 Flash) for agent responses
- **Persistence**: In-memory with JSON export/import

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
Use the provided startup script for the easiest development experience:

```bash
# Default mode (with real-time logs)
./start.sh

# Simple mode (no real-time logs)
./start.sh --simple
```

The script includes auto-reload for both frontend and backend services.

### Manual Development

#### Backend
```bash
cd backend
uv run main.py
```

#### Frontend
```bash
cd frontend
npm run dev
```

### Testing
The backend includes a lean, deterministic test suite using `pytest`.
Tests use a fake LLM for fast, reliable execution without external dependencies.

#### Running Tests
```bash
cd backend
uv run pytest -q                    # Run all tests quietly
uv run pytest -v                    # Run all tests with verbose output
uv run pytest tests/                # Run all tests (default behavior)
uv run pytest tests/test_file.py    # Run specific test file
uv run pytest -k "test_name"        # Run tests matching pattern
uv run pytest --cov=. --cov-report=html  # Run with coverage report
```

#### Test Strategy
The test suite focuses on critical architectural invariants rather than brittle content assertions:
- **DebateSpec validation**: Ensures YAML configs load and validate correctly
- **Router flow**: Verifies the debate progresses through rounds and reaches completion
- **Transcript shape**: Confirms output structure remains stable across runs
- **Budget guards**: Tests recursion limits and error handling

Tests are designed to be fast and require no external services or credentials.

For detailed testing documentation, see `backend/tests/README.md`.

### Development Tools
- **Dependency Management**: Uses `uv` for Python dependencies
- **Testing**: `pytest` for backend unit tests
- **Linting**: Uses `ruff` for Python code formatting and linting
- **Type Checking**: TypeScript for frontend type safety
- **Auto-reload**: Both frontend and backend auto-reload on file changes

## Services

Once started, you'll have access to:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Backend Health Check**: http://localhost:8000/api/health

## User Experience

### Creating Debates
1. **Select Agents**: Choose from built-in experts or create custom agents
2. **Assemble Panel**: Build debate panels with 2 or more agents
3. **Start Debate**: Enter your topic and watch the structured debate unfold
4. **Save Panels**: Reuse successful panel combinations

### Custom Agents
Create agents with simple prompts like:
- "A Keynesian economist"
- "Abraham Lincoln oration style"
- "A libertarian policy analyst"

### Panel Management
- Save custom panels (e.g., "Economic Policy Panel", "Climate Debate Panel")
- Export/import panels as JSON strings
- Modify existing panels

## Additional Documentation

- **Startup Guide**: See `STARTUP.md` for detailed startup instructions and troubleshooting
- **Environment Configuration**: Check `env.example` files for all available configuration options

## Known Issues

- Single-agent "debates" are unstable, and agents are more likely to hallucinate. For best results, use at least two agents.

## Future Roadmap

- **Customizable Debate Structure**: Configurable debate layer system
- **Research Tools**: Google Search integration for factual debates
- **Advanced Agent Features**: LLM-based agent generation and enhanced capabilities
- **Multi-model Capability**: Support for different AI models
- **MCP Integration**: Model Context Protocol integration
