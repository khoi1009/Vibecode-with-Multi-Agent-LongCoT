# Deployment Guide

## Local Development

```bash
# Clone and setup
git clone <repo>
cd vibecode-studio
pip install -e ".[test]"

# Configure
export GEMINI_API_KEY="your-key"

# Run
python vibecode_studio.py
```

## Docker Deployment

```bash
# Build image
docker build -t vibecode .

# Run with API key
docker run -e GEMINI_API_KEY="your-key" -v $(pwd)/workspace:/app/workspace vibecode
```

## CI/CD Pipeline

```yaml
# .github/workflows/vibecode.yml
name: Vibecode CI

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install
        run: pip install -e ".[test]"

      - name: Test
        run: pytest tests/ -v --cov=core

      - name: Quality Gate
        run: |
          coverage=$(pytest --cov=core --cov-report=term | grep TOTAL | awk '{print $4}' | tr -d '%')
          if [ "$coverage" -lt 80 ]; then
            echo "Coverage $coverage% < 80% required"
            exit 1
          fi
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key for Gemini | - |
| `VIBECODE_AUTO` | Enable auto mode | `0` |
| `VIBECODE_CONFIDENCE_THRESHOLD` | Confidence threshold | `0.8` |
| `VIBECODE_AUDIT_LOG` | Audit log path | `.vibecode/autonomy_audit.log` |
| `VIBECODE_MAX_STEPS` | ReAct max iterations | `30` |

## Production Checklist

- [ ] API key configured as secret
- [ ] Confidence threshold appropriate for use case
- [ ] Audit logging enabled
- [ ] Test gate at 95% pass rate
- [ ] Memory limits configured
- [ ] Rollback procedure documented
