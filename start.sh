#!/bin/bash

# Parliament Startup Script
# This script starts both the frontend and backend services with clear logging

set -e  # Exit on any error

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_frontend() {
    echo -e "${PURPLE}[FRONTEND]${NC} $1"
}

log_backend() {
    echo -e "${CYAN}[BACKEND]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            log_success "$service_name is ready!"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to cleanup background processes on exit
cleanup() {
    log_info "Shutting down services..."
    
    # Kill background processes
    if [ ! -z "$FRONTEND_PID" ]; then
        log_info "Stopping frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        log_info "Stopping backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Remove temporary files
    rm -f /tmp/parliament_frontend.log /tmp/parliament_backend.log
    
    log_success "Cleanup complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    log_error "This script must be run from the parliament project root directory"
    exit 1
fi

log_info "Starting Parliament development environment..."

# Check if ports are available
if check_port 5173; then
    log_warning "Port 5173 is already in use. Frontend may not start properly."
fi

if check_port 8000; then
    log_warning "Port 8000 is already in use. Backend may not start properly."
fi

# Check if virtual environment exists
if [ ! -d "backend/.venv" ]; then
    log_error "Backend virtual environment not found. Please run setup first."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    log_error "Frontend node_modules not found. Please run 'npm install' in frontend directory."
    exit 1
fi

# Start backend
log_info "Starting backend server..."
cd backend

# Activate virtual environment and start backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > /tmp/parliament_backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    log_error "Backend failed to start. Check /tmp/parliament_backend.log for details:"
    cat /tmp/parliament_backend.log
    exit 1
fi

log_success "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
if wait_for_service "http://localhost:8000/health" "Backend"; then
    log_success "Backend is ready at http://localhost:8000"
else
    log_error "Backend failed to become ready"
    cleanup
    exit 1
fi

cd ..

# Start frontend
log_info "Starting frontend development server..."
cd frontend

# Start frontend
npm run dev > /tmp/parliament_frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    log_error "Frontend failed to start. Check /tmp/parliament_frontend.log for details:"
    cat /tmp/parliament_frontend.log
    cleanup
    exit 1
fi

log_success "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to be ready
if wait_for_service "http://localhost:5173" "Frontend"; then
    log_success "Frontend is ready at http://localhost:5173"
else
    log_error "Frontend failed to become ready"
    cleanup
    exit 1
fi

cd ..

# Display status
echo ""
log_success "🎉 Parliament is now running!"
echo ""
echo -e "${GREEN}Services:${NC}"
echo -e "  ${CYAN}Backend:${NC}  http://localhost:8000"
echo -e "  ${PURPLE}Frontend:${NC} http://localhost:5173"
echo ""
echo -e "${GREEN}Logs:${NC}"
echo -e "  ${CYAN}Backend:${NC}  /tmp/parliament_backend.log"
echo -e "  ${PURPLE}Frontend:${NC} /tmp/parliament_frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Monitor logs in real-time
log_info "Monitoring logs (press Ctrl+C to stop)..."
echo ""

# Function to display logs with prefixes
tail_logs() {
    # Tail backend logs with prefix
    tail -f /tmp/parliament_backend.log | sed 's/^/[BACKEND] /' &
    BACKEND_LOG_PID=$!
    
    # Tail frontend logs with prefix
    tail -f /tmp/parliament_frontend.log | sed 's/^/[FRONTEND] /' &
    FRONTEND_LOG_PID=$!
    
    # Wait for either process to exit
    wait
}

# Start log monitoring
tail_logs &

# Wait for user interrupt
wait 
