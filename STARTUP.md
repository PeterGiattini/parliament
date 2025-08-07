# Parliament Startup Script

This directory contains a script to easily start both the frontend and backend services for the Parliament debate system.

## Quick Start

### Default Mode (with real-time logs)
```bash
./start.sh
```

### Simple Mode (no real-time logs)
```bash
./start.sh --simple
# or
./start.sh -s
```

### Show Help
```bash
./start.sh --help
```

## What the Script Does

The startup script will:

1. **Check Prerequisites**
   - Verify you're in the project root directory
   - Check if `uv` is available
   - Check if frontend node_modules exists
   - Warn if ports 5173 or 8000 are already in use

2. **Start Backend**
   - Start the FastAPI server using `uv run main.py` on port 8000
   - Wait for the health endpoint to be ready
   - Log to `/tmp/parliament_backend.log`

3. **Start Frontend**
   - Start the Vite development server on port 5173
   - Wait for the frontend to be ready
   - Log to `/tmp/parliament_frontend.log`

4. **Provide Status**
   - Display service URLs
   - Show log file locations
   - Provide useful commands for debugging

## Services

Once started, you'll have access to:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Backend Health Check**: http://localhost:8000/health

## Logging and Debugging

### Log Files
- Backend logs: `/tmp/parliament_backend.log`
- Frontend logs: `/tmp/parliament_frontend.log`

### Viewing Logs
```bash
# View backend logs in real-time
tail -f /tmp/parliament_backend.log

# View frontend logs in real-time
tail -f /tmp/parliament_frontend.log

# View last 50 lines of backend logs
tail -50 /tmp/parliament_backend.log
```

### Common Issues

#### Backend Won't Start
1. Check if `uv` is installed: `which uv`
2. Check backend logs: `cat /tmp/parliament_backend.log`
3. Verify environment variables: `cat backend/env.example`

#### Frontend Won't Start
1. Check if node_modules exists: `ls frontend/node_modules`
2. Check frontend logs: `cat /tmp/parliament_frontend.log`
3. Try reinstalling dependencies: `cd frontend && npm install`

#### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Check what's using port 5173
lsof -i :5173

# Kill process using port 8000 (replace PID with actual process ID)
kill -9 <PID>
```

## Stopping Services

Press `Ctrl+C` in the terminal where you ran the startup script. The script will automatically:

1. Stop the frontend process
2. Stop the backend process
3. Clean up temporary files
4. Exit cleanly

## Manual Startup (Alternative)

If you prefer to start services manually:

### Backend
```bash
cd backend
uv run main.py
```

### Frontend
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Script Permissions
If you get "Permission denied" errors:
```bash
chmod +x start.sh
```

### Missing Dependencies
If the script fails due to missing dependencies:

1. **Backend**: Run the setup script or ensure `uv` is installed
2. **Frontend**: Run `npm install` in the frontend directory

### Environment Variables
Make sure you have the required environment variables set up:
```bash
cp backend/env.example backend/.env
# Edit backend/.env with your actual values
```

## Script Modes

- **Default mode**: Includes real-time log monitoring with colored prefixes for easier debugging
- **Simple mode** (`--simple`): Starts services and keeps running without real-time log monitoring 
