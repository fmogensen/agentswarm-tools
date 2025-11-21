# AgentSwarm Tools - Quick Start Guide

## 🚀 Launch Autonomous Development in 3 Commands

### Step 1: Run Setup
```bash
cd /Users/frank/Documents/Code/Genspark/agentswarm-tools
./setup-autonomous-dev.sh
```

This creates:
- ✅ `.env` with all autonomous configuration
- ✅ `requirements.txt` with dependencies
- ✅ `Makefile` with helper commands
- ✅ `start.sh` / `stop.sh` scripts
- ✅ Data directories

### Step 2: Build Docker Containers
```bash
docker-compose build
```

This builds:
- 1 Orchestrator agent (master coordinator)
- 7 Development teams (parallel workers)
- 1 Tester agent
- 1 Documentation agent
- 1 Dashboard (web UI)
- Supporting services (Redis, PostgreSQL)

### Step 3: Start Autonomous Development
```bash
./start.sh
```

**That's it!** The system now runs autonomously until all 61 tools are complete.

---

## 📊 Monitor Progress

### View Dashboard (Recommended)
```bash
open http://localhost:8080
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Orchestrator only
docker-compose logs -f orchestrator

# Specific team
docker-compose logs -f team1

# Just completions
docker-compose logs -f | grep "✅"
```

### Check Status
```bash
make status
```

---

## 🎮 Control Commands

```bash
# Stop everything
./stop.sh
# OR
make stop

# Restart
make restart

# View help
make help
```

---

## ⚙️ Configuration

### Add Real API Keys (Optional)

Edit `.env` and add your keys:
```bash
nano .env
```

Then restart:
```bash
make restart
```

**Note:** Real API keys are optional. System uses mocks by default.

### Adjust Settings

In `.env` you can configure:
- `CHECK_INTERVAL` - How often to check progress (default: 60s)
- `RETRY_ATTEMPTS` - Retry count for failures (default: 5)
- `MIN_TEST_COVERAGE` - Required coverage % (default: 80)
- `PARALLEL_WORKERS` - Number of teams (default: 7)

---

## 📈 What Happens Autonomously

1. **Orchestrator starts** ✅
2. **Loads 61 tools into queue** ✅
3. **Assigns tools to 7 teams** ✅
4. **Each team develops in parallel:**
   - Reads Genspark docs
   - Generates code
   - Writes tests
   - Auto-fixes issues
   - Creates documentation
5. **Orchestrator reviews & merges** ✅
6. **Continues until all 61 done** ✅
7. **Deploys automatically** ✅

**NO HUMAN INTERVENTION NEEDED!**

---

## 🔍 Troubleshooting

### Docker not running?
```bash
# macOS
open -a Docker

# Check status
docker info
```

### Containers won't start?
```bash
# Clean and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### View specific container logs
```bash
docker-compose logs orchestrator
docker-compose logs team1
docker-compose logs redis
```

### Check if containers are running
```bash
docker-compose ps
```

---

## ⏱️ Timeline

**Estimated completion:** 2-3 weeks of continuous operation

Progress is saved, so you can stop/restart anytime without losing work.

---

## 🎯 Success Indicators

Watch for these in logs:

```
✅ web_search complete
✅ scholar_search complete
✅ image_generation complete
...
🎉 ALL 61 TOOLS COMPLETE!
```

Dashboard shows:
- Tools completed: X/61
- Current progress: Y%
- Estimated time remaining

---

## 📞 Need Help?

1. Check logs: `make logs`
2. Check status: `make status`
3. View dashboard: `open http://localhost:8080`
4. Check this guide: `cat QUICKSTART.md`

---

## 🛑 Stopping Development

```bash
./stop.sh
```

**Note:** Progress is saved. You can restart anytime and it will continue from where it left off.

---

**Built for AgentSwarm.ai platform** 🚀
