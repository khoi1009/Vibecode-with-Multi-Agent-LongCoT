# Changelog

## [2.0.0] - 2026-01-07

### Added
- **Autonomous Mode**: Full headless operation with `--prompt --auto`
- **Confidence-Based Approval**: Auto-approve/reject based on Long CoT confidence
- **Agent Executors**: Real execution logic for agents 00, 01, 02, 09
- **Message Queue**: Structured agent-to-agent communication
- **Artifact Registry**: Track and rollback generated files
- **Extended Tools**: 15+ ReAct tools (git, npm, test, search)
- **Test Infrastructure**: pytest with 133 tests, 95%+ coverage
- **Performance Optimizations**: Caching, async I/O, bounded history
- **CI/CD Pipeline**: GitHub Actions with quality gates
- **Audit Logging**: All autonomous decisions tracked

### Changed
- Orchestrator approval flow now confidence-gated
- ReasoningEngine history now bounded
- Agent context includes compaction

### Fixed
- Windows path handling in ReasoningEngine
- Memory leaks in long sessions
- Context pollution between agents

### Security
- Tool permissions per agent
- Sensitive env var blocking
- Command injection prevention
