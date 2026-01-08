# Autonomous Mode Guide

## Overview

Vibecode Studio's autonomous mode enables fully unattended operation, ideal for CI/CD pipelines, batch processing, and automated workflows.

## Prerequisites

- Gemini API key configured (for AI-powered execution)
- Project scanned at least once (for Long CoT confidence)

## Usage

### Basic Autonomous Execution

```bash
python vibecode_studio.py --prompt "<command>" --auto
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/scan` | Analyze project | `--prompt "/scan --deep"` |
| `/build <desc>` | Build feature | `--prompt "/build user auth"` |
| `/fix <bug>` | Fix bug | `--prompt "/fix null pointer in login"` |
| `/test` | Run tests | `--prompt "/test --coverage"` |
| `/refactor <desc>` | Refactor code | `--prompt "/refactor extract services"` |

### Configuration

```bash
# Environment variables
export GEMINI_API_KEY="your-key"
export VIBECODE_AUTO=1                    # Enable auto mode by default
export VIBECODE_CONFIDENCE_THRESHOLD=0.8  # Default: 0.8

# CLI flags
--auto                    # Enable auto-approval
--confidence-threshold X  # Override default (0.0-1.0)
--audit-log <path>        # Custom audit log location
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Build Feature
  run: |
    python vibecode_studio.py \
      --prompt "/build ${{ github.event.inputs.feature }}" \
      --auto \
      --confidence-threshold 0.9
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Safety Mechanisms

### Confidence Gating

Long CoT analysis provides confidence scores (0.0-1.0):
- High confidence (>=0.8): Proceed automatically
- Medium (0.5-0.8): Require explicit --auto flag
- Low (<0.5): Auto-reject destructive operations

### Audit Trail

All autonomous decisions logged:
```json
{
  "timestamp": "2026-01-07T12:34:56",
  "task_type": "BUILD_FEATURE",
  "confidence": 0.85,
  "approved": true,
  "reason": "High confidence (85%)"
}
```

### Rollback Support

Artifacts tracked in `.vibecode/artifacts/<run_id>/`:
- Manifest of all created files
- Checksums for verification
- Rollback command: `python vibecode_studio.py --rollback <run_id>`

## Best Practices

1. **Always scan first**: Run `/scan --deep` before autonomous builds
2. **Set appropriate threshold**: Lower for safe ops, higher for destructive
3. **Review audit logs**: Periodically check `.vibecode/autonomy_audit.log`
4. **Use CI gates**: Require 95% test pass rate before merge
5. **Monitor token usage**: Check `.vibecode/metrics.jsonl` for cost control

## Troubleshooting

### "Auto-rejected due to low confidence"

1. Run `/scan --deep` to improve Long CoT analysis
2. Lower confidence threshold if appropriate
3. Check project has analyzable code structure

### "No API key configured"

1. Set `GEMINI_API_KEY` environment variable
2. Or run `python vibecode_studio.py` and use Settings menu

### "Max steps reached"

1. Increase ReasoningEngine max_steps
2. Simplify the prompt/task
3. Break into smaller sub-tasks
