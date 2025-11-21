#!/bin/bash

################################################################################
# AgentSwarm Tools - Autonomous Development Setup Script
#
# This script prepares your environment for fully autonomous development
# of all 61 Genspark tools with zero human intervention required.
#
# Usage: ./setup-autonomous-dev.sh
################################################################################

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  AgentSwarm Tools - Autonomous Development Setup"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

################################################################################
# STEP 1: Environment Detection
################################################################################

print_info "Detecting environment..."

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    print_success "Detected: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    print_success "Detected: Linux"
else
    print_error "Unsupported OS: $OSTYPE"
    exit 1
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
    print_success "Docker is installed: $(docker --version)"
else
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if docker info &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running. Please start Docker."
    exit 1
fi

################################################################################
# STEP 2: Create .env File with All Required Configuration
################################################################################

print_info "Creating .env configuration file..."

cat > .env << 'EOF'
################################################################################
# AgentSwarm Tools - Environment Configuration
# Generated: $(date)
################################################################################

# ============================================================================
# AUTONOMOUS MODE SETTINGS (Critical - Do Not Change)
# ============================================================================
AUTONOMOUS_MODE=true
AUTO_FIX=true
AUTO_MERGE=true
AUTO_TEST=true
AUTO_DOCUMENT=true
REQUIRE_HUMAN_APPROVAL=false
CONTINUE_ON_ERROR=true
USE_MOCK_APIS=true

# ============================================================================
# DEVELOPMENT SETTINGS
# ============================================================================
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

# ============================================================================
# TIMING & PERFORMANCE
# ============================================================================
CHECK_INTERVAL=60              # Check progress every 60 seconds
RETRY_ATTEMPTS=5               # Retry failed operations 5 times
AUTO_FIX_ATTEMPTS=3            # Attempt auto-fix 3 times before moving on
TIMEOUT_SECONDS=600            # 10 minute timeout per operation
PARALLEL_WORKERS=7             # 7 agent teams working in parallel

# ============================================================================
# QUALITY GATES
# ============================================================================
MIN_TEST_COVERAGE=80           # Minimum 80% code coverage
MAX_COMPLEXITY=10              # Maximum cyclomatic complexity
ENFORCE_TYPE_HINTS=true        # Require type hints
AUTO_FORMAT=true               # Auto-format code with black

# ============================================================================
# API KEYS (Optional - System uses mocks if not provided)
# ============================================================================

# Search APIs
SERPAPI_KEY=${SERPAPI_KEY:-}
SEMANTIC_SCHOLAR_KEY=${SEMANTIC_SCHOLAR_KEY:-}

# Media Generation APIs
OPENAI_API_KEY=${OPENAI_API_KEY:-}
STABILITY_API_KEY=${STABILITY_API_KEY:-}
ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY:-}
GOOGLE_CLOUD_API_KEY=${GOOGLE_CLOUD_API_KEY:-}

# Communication APIs
GMAIL_CLIENT_ID=${GMAIL_CLIENT_ID:-}
GMAIL_CLIENT_SECRET=${GMAIL_CLIENT_SECRET:-}
GOOGLE_CALENDAR_KEY=${GOOGLE_CALENDAR_KEY:-}

# Storage APIs
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}
AZURE_STORAGE_KEY=${AZURE_STORAGE_KEY:-}

# Workspace APIs
NOTION_API_KEY=${NOTION_API_KEY:-}
MICROSOFT_GRAPH_KEY=${MICROSOFT_GRAPH_KEY:-}

# ============================================================================
# ANALYTICS & MONITORING
# ============================================================================
ANALYTICS_ENABLED=true
ANALYTICS_BACKEND=file         # Options: file, memory, postgresql
ANALYTICS_LOG_DIR=/data/analytics

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL=postgresql://agentswarm:agentswarm@postgres:5432/agentswarm
REDIS_URL=redis://redis:6379/0

# ============================================================================
# GITHUB CONFIGURATION
# ============================================================================
GITHUB_REPO=https://github.com/fmogensen/agentswarm-tools.git
GITHUB_TOKEN=${GITHUB_TOKEN:-}
GIT_USER_NAME="AgentSwarm Bot"
GIT_USER_EMAIL="bot@agentswarm.ai"
AUTO_COMMIT=true
AUTO_PUSH=true

# ============================================================================
# AGENT CONFIGURATION
# ============================================================================
AGENT_MODEL=gpt-4o             # Model for agent reasoning
AGENT_TEMPERATURE=0.3          # Lower temperature for consistency
AGENT_MAX_TOKENS=4000
AGENT_TIMEOUT=300              # 5 minutes per agent task

# ============================================================================
# TOOL DEVELOPMENT CONFIGURATION
# ============================================================================
TOOLS_TO_DEVELOP=61            # Total number of tools
SKIP_EXISTING=true             # Skip already completed tools
VERIFY_COMPATIBILITY=true      # Verify Agency Swarm compatibility

# ============================================================================
# SECURITY SETTINGS
# ============================================================================
SECURITY_SCAN_ENABLED=true
VULNERABILITY_SCAN=true
SECRET_DETECTION=true
CODE_SIGNING=false

# ============================================================================
# NOTIFICATION SETTINGS (Optional)
# ============================================================================
NOTIFY_ON_COMPLETION=false
NOTIFY_ON_ERROR=false
SLACK_WEBHOOK=${SLACK_WEBHOOK:-}
DISCORD_WEBHOOK=${DISCORD_WEBHOOK:-}
EMAIL_NOTIFICATIONS=${EMAIL_NOTIFICATIONS:-}

# ============================================================================
# DOCKER SETTINGS
# ============================================================================
DOCKER_COMPOSE_PROJECT=agentswarm-tools
DOCKER_NETWORK=agentswarm-net
DOCKER_RESTART_POLICY=unless-stopped

# ============================================================================
# DASHBOARD SETTINGS
# ============================================================================
DASHBOARD_PORT=8080
DASHBOARD_ENABLED=true
DASHBOARD_AUTO_REFRESH=30      # Auto-refresh every 30 seconds

EOF

print_success "Created .env file with autonomous development configuration"

################################################################################
# STEP 3: Export All Environment Variables
################################################################################

print_info "Exporting environment variables..."

# Source the .env file
set -a  # Automatically export all variables
source .env
set +a

print_success "Exported all environment variables from .env"

################################################################################
# STEP 4: Create Data Directories
################################################################################

print_info "Creating data directories..."

mkdir -p data/analytics
mkdir -p data/logs
mkdir -p data/progress
mkdir -p data/metrics
mkdir -p data/cache

print_success "Created data directories"

################################################################################
# STEP 5: Create Docker Configuration Files
################################################################################

print_info "Creating Docker configuration files..."

# Create .dockerignore
cat > .dockerignore << 'EOF'
.git
.github
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.env
.venv
venv/
data/
.DS_Store
*.log
.pytest_cache
.mypy_cache
.coverage
htmlcov/
EOF

print_success "Created .dockerignore"

################################################################################
# STEP 6: Create requirements.txt
################################################################################

print_info "Creating requirements.txt..."

cat > requirements.txt << 'EOF'
# Core Framework
agency-swarm>=1.0.0
pydantic>=2.5.0
python-dotenv>=1.0.0

# Web & HTTP
requests>=2.31.0
aiohttp>=3.9.0
httpx>=0.25.0

# Data Processing
pandas>=2.1.0
numpy>=1.26.0

# Database
redis>=5.0.0
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# Code Quality
black>=23.12.0
pylint>=3.0.0
mypy>=1.7.0
flake8>=6.1.0
bandit>=1.7.5
safety>=2.3.5

# Documentation
sphinx>=7.2.0
sphinx-rtd-theme>=2.0.0
markdown>=3.5.0

# OpenAI & AI
openai>=1.6.0

# Utilities
click>=8.1.7
rich>=13.7.0
tqdm>=4.66.0
python-dateutil>=2.8.2

# Security
cryptography>=41.0.7
pyjwt>=2.8.0

# Monitoring
opentelemetry-api>=1.22.0
opentelemetry-sdk>=1.22.0

# Async
asyncio>=3.4.3
uvloop>=0.19.0
EOF

print_success "Created requirements.txt"

################################################################################
# STEP 7: Create Makefile for Common Commands
################################################################################

print_info "Creating Makefile for common commands..."

cat > Makefile << 'EOF'
.PHONY: help setup start stop restart logs status clean test

help:
	@echo "AgentSwarm Tools - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Initial setup (run once)"
	@echo "  make start          - Start autonomous development"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs           - View all logs"
	@echo "  make status         - Check current status"
	@echo "  make dashboard      - Open progress dashboard"
	@echo ""
	@echo "Control:"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean up containers and data"
	@echo "  make test           - Run tests manually"

setup:
	@echo "Setting up autonomous development environment..."
	./setup-autonomous-dev.sh

start:
	@echo "Starting autonomous development..."
	docker-compose up -d
	@echo ""
	@echo "✓ Autonomous development started!"
	@echo "  - View dashboard: http://localhost:8080"
	@echo "  - View logs: make logs"
	@echo "  - Check status: make status"

stop:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting services..."
	docker-compose restart

logs:
	docker-compose logs -f

status:
	@docker-compose ps
	@echo ""
	@echo "Progress:"
	@docker-compose exec -T redis redis-cli get "metrics:completed" 2>/dev/null || echo "0"
	@echo "/61 tools completed"

dashboard:
	@open http://localhost:8080 || xdg-open http://localhost:8080

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf data/*

test:
	docker-compose exec orchestrator pytest -v
EOF

chmod +x Makefile

print_success "Created Makefile"

################################################################################
# STEP 8: Create Git Configuration
################################################################################

print_info "Configuring Git for autonomous commits..."

git config user.name "AgentSwarm Bot" 2>/dev/null || true
git config user.email "bot@agentswarm.ai" 2>/dev/null || true

print_success "Configured Git"

################################################################################
# STEP 9: Verify Docker Compose
################################################################################

print_info "Verifying Docker Compose installation..."

if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose is available: $(docker-compose --version)"
elif docker compose version &> /dev/null; then
    print_success "Docker Compose V2 is available: $(docker compose version)"
else
    print_error "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

################################################################################
# STEP 10: Create Quick Start Script
################################################################################

print_info "Creating quick start script..."

cat > start.sh << 'EOF'
#!/bin/bash
# Quick start for autonomous development

echo "🚀 Starting AgentSwarm Tools Autonomous Development..."
echo ""

# Source environment
source .env

# Start with Docker Compose
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo ""
echo "✅ Autonomous development is now running!"
echo ""
echo "📊 Dashboard: http://localhost:8080"
echo "📝 View logs: docker-compose logs -f orchestrator"
echo "📈 Status: docker-compose logs -f | grep '✅'"
echo ""
echo "The system will run continuously until all 61 tools are complete."
echo "No human intervention required!"
echo ""
EOF

chmod +x start.sh

print_success "Created start.sh quick start script"

################################################################################
# STEP 11: Create Stop Script
################################################################################

cat > stop.sh << 'EOF'
#!/bin/bash
# Stop autonomous development

echo "🛑 Stopping autonomous development..."

if command -v docker-compose &> /dev/null; then
    docker-compose down
else
    docker compose down
fi

echo "✅ All services stopped"
EOF

chmod +x stop.sh

print_success "Created stop.sh script"

################################################################################
# STEP 12: Summary and Next Steps
################################################################################

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Environment is ready for autonomous development of 61 tools."
echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo "  • Autonomous Mode: ${GREEN}ENABLED${NC}"
echo "  • Auto-Fix: ${GREEN}ENABLED${NC}"
echo "  • Auto-Merge: ${GREEN}ENABLED${NC}"
echo "  • Mock APIs: ${GREEN}ENABLED${NC} (real APIs optional)"
echo "  • Agent Teams: ${GREEN}7 teams${NC} working in parallel"
echo "  • Total Tools: ${GREEN}61 tools${NC} to develop"
echo ""
echo -e "${BLUE}Files Created:${NC}"
echo "  ✓ .env (environment configuration)"
echo "  ✓ requirements.txt (Python dependencies)"
echo "  ✓ Makefile (common commands)"
echo "  ✓ start.sh (quick start script)"
echo "  ✓ stop.sh (stop script)"
echo "  ✓ data/ directories"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "  1. ${YELLOW}Review .env file${NC} and add real API keys (optional)"
echo "     ${BLUE}→${NC} nano .env"
echo ""
echo "  2. ${YELLOW}Build Docker images${NC}"
echo "     ${BLUE}→${NC} docker-compose build"
echo ""
echo "  3. ${YELLOW}Start autonomous development${NC}"
echo "     ${BLUE}→${NC} ./start.sh"
echo "     ${BLUE}OR${NC}"
echo "     ${BLUE}→${NC} make start"
echo ""
echo "  4. ${YELLOW}Monitor progress${NC}"
echo "     ${BLUE}→${NC} Open http://localhost:8080 in browser"
echo "     ${BLUE}→${NC} docker-compose logs -f orchestrator"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  • System runs continuously until all 61 tools complete"
echo "  • No human intervention required"
echo "  • Progress is saved - can restart anytime"
echo "  • Real API keys are optional (uses mocks by default)"
echo ""
echo -e "${GREEN}Ready to launch autonomous development!${NC}"
echo ""
echo "════════════════════════════════════════════════════════════════"
