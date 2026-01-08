# Tool Reference

## Core Tools

| Tool | Description | Args |
|------|-------------|------|
| `list_dir` | List directory contents | `path` |
| `read_file` | Read file content | `path` |
| `write_file` | Write file content | `path`, `content` |
| `run_command` | Execute shell command | `command` |
| `finish_task` | Mark task complete | `summary` |

## Git Tools

| Tool | Description | Args |
|------|-------------|------|
| `git_status` | Repository status | - |
| `git_commit` | Create commit | `message` |
| `git_diff` | Show changes | `staged` (optional) |
| `git_branch` | Create/switch branch | `name`, `create` |

## Package Tools

| Tool | Description | Args |
|------|-------------|------|
| `npm_install` | Install npm package | `package` |
| `pip_install` | Install Python package | `package` |
| `npm_run` | Run npm script | `script` |

## Test Tools

| Tool | Description | Args |
|------|-------------|------|
| `run_tests` | Execute test suite | `pattern`, `framework` |
| `get_test_coverage` | Coverage report | - |

## Utility Tools

| Tool | Description | Args |
|------|-------------|------|
| `search_codebase` | Grep-like search | `pattern`, `file_type` |
| `get_env_var` | Read env variable | `name` |
| `create_directory` | Create directory | `path` |

## Agent Permissions

| Agent | Allowed Categories |
|-------|--------------------|
| 00 (Forensic) | core, utility |
| 01 (Architect) | core, utility |
| 02 (Builder) | ALL |
| 04 (Reviewer) | core, utility |
| 09 (QA) | core, test, utility |

## Security

- Commands with `rm -rf`, `format`, `del /s` are blocked
- File paths must be under workspace
- Sensitive env vars (containing SECRET, TOKEN, etc.) blocked
- Rate limits per tool per session
