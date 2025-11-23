#!/bin/bash

# Pre-Push Cleanup Script
# Ensures root directory is clean before pushing to GitHub

set -e

echo "🧹 Running pre-push cleanup checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: Temporary files in root
echo ""
echo "📂 Checking for temporary files..."
TEMP_FILES=$(find . -maxdepth 1 -type f \( -name "*.tmp" -o -name "*.temp" -o -name "*.log" -o -name "coverage.xml" -o -name "test_results.txt" -o -name "tool_readme_audit.json" -o -name ".coverage.*" \) 2>/dev/null || true)

if [ -n "$TEMP_FILES" ]; then
    echo -e "${RED}❌ Found temporary files in root:${NC}"
    echo "$TEMP_FILES"
    echo ""
    echo "Run: rm -f coverage.xml test_results.txt tool_readme_audit.json .coverage.* *.tmp *.temp *.log"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No temporary files in root${NC}"
fi

# Check 2: Misplaced report files
echo ""
echo "📄 Checking for misplaced report files..."
# Exclude TEST_REPORT.md and other current status docs
REPORT_FILES=$(find . -maxdepth 1 -type f \( -name "*IMPLEMENTATION*REPORT*.md" -o -name "*SUMMARY*.md" -o -name "*DELIVERABLES*.md" -o -name "CLEANUP_REPORT*.md" \) 2>/dev/null || true)

if [ -n "$REPORT_FILES" ]; then
    echo -e "${RED}❌ Found report files in root (should be in reports/):${NC}"
    echo "$REPORT_FILES"
    echo ""
    echo "Move these to reports/ directory"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No misplaced report files${NC}"
fi

# Check 3: Utility scripts in root
echo ""
echo "🔧 Checking for utility scripts in root..."
SCRIPT_FILES=$(find . -maxdepth 1 -type f \( -name "audit_*.py" -o -name "generate_*.py" -o -name "test_*.py" \) ! -name "conftest.py" 2>/dev/null || true)

if [ -n "$SCRIPT_FILES" ]; then
    echo -e "${RED}❌ Found utility scripts in root (should be in scripts/):${NC}"
    echo "$SCRIPT_FILES"
    echo ""
    echo "Move these to scripts/ directory"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No misplaced utility scripts${NC}"
fi

# Check 4: Git status clean
echo ""
echo "🔍 Checking git status..."
UNTRACKED=$(git status --porcelain | grep "^??" | grep -v ".venv\|__pycache__\|.pytest_cache\|htmlcov\|test-results\|.analytics\|.coverage\|benchmarks" || true)

if [ -n "$UNTRACKED" ]; then
    echo -e "${YELLOW}⚠️  Warning: Untracked files found:${NC}"
    echo "$UNTRACKED"
    echo ""
    echo "Review these files and either:"
    echo "  - Add to .gitignore if generated"
    echo "  - Move to appropriate directory"
    echo "  - Delete if temporary"
    echo ""
    echo -e "${YELLOW}This is a warning, not blocking push.${NC}"
fi

# Check 5: Sensitive data
echo ""
echo "🔒 Checking for sensitive data..."
SENSITIVE=$(git diff --cached --name-only | xargs grep -l "sk_live_\|ghp_\|lin_api_\|PRIVATE.*KEY" 2>/dev/null || true)

if [ -n "$SENSITIVE" ]; then
    echo -e "${RED}❌ CRITICAL: Potential sensitive data found in staged files:${NC}"
    echo "$SENSITIVE"
    echo ""
    echo "DO NOT PUSH! Review and remove sensitive data."
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No sensitive data detected${NC}"
fi

# Summary
echo ""
echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All pre-push checks passed!${NC}"
    echo "Safe to push to GitHub."
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS issue(s) that must be fixed before pushing${NC}"
    echo ""
    echo "Fix the issues above and try again."
    exit 1
fi
