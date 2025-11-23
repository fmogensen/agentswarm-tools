# Development Scripts

This directory contains utility scripts for development, maintenance, and quality assurance.

## Pre-Push Cleanup

### pre_push_cleanup.sh

**Purpose**: Automated pre-push checks to ensure repository cleanliness

**Usage**:
```bash
# Run before pushing to GitHub
./scripts/pre_push_cleanup.sh
```

**Checks**:
- ✅ No temporary files in root (*.tmp, *.log, coverage.xml, etc.)
- ✅ No misplaced report files (should be in reports/)
- ✅ No misplaced utility scripts (should be in scripts/)
- ✅ No sensitive data in staged commits
- ⚠️  Warns about untracked files

**Exit Codes**:
- `0` - All checks passed, safe to push
- `1` - Issues found, must fix before pushing

## Utility Scripts

### audit_tools.py

Audits all tools for documentation completeness and standards compliance.

**Usage**:
```bash
python scripts/audit_tools.py
```

### generate_readmes.py

Generates README files for tools missing documentation.

**Usage**:
```bash
python scripts/generate_readmes.py
```

### test_performance_monitoring.py

Tests the performance monitoring system.

**Usage**:
```bash
python scripts/test_performance_monitoring.py
```

### test_sdk_demo.py

Demonstrates and tests the SDK tool generation capabilities.

**Usage**:
```bash
python scripts/test_sdk_demo.py
```

## Git Hooks Integration

To automatically run cleanup checks before each push, install as a Git hook:

```bash
# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
./scripts/pre_push_cleanup.sh
EOF

# Make executable
chmod +x .git/hooks/pre-push
```

Now the cleanup script will run automatically before every `git push`, preventing messy commits.

## Best Practices

1. **Always run cleanup before pushing**:
   ```bash
   ./scripts/pre_push_cleanup.sh && git push
   ```

2. **Fix issues immediately** - Don't ignore warnings

3. **Keep root clean** - Move files to appropriate directories:
   - Reports → `reports/`
   - Scripts → `scripts/`
   - Docs → `docs/`

4. **Update .gitignore** if new generated file types appear

5. **Never commit sensitive data** - API keys, credentials, tokens
