# Phase 6 Tasks

- [x] Task 1: Enhance CLI with new subcommands and YAML config support
  - What: Update cli.py to support all required subcommands (init, scan, organize, sync, rules, summary, dry-run) and YAML configuration via ~/.email_tool/config.yaml
  - Files: email_tool/cli.py, email_tool/config.py (extend), email_tool/logging_config.py (create)
  - Done when: CLI has all 7 subcommands, loads config from YAML, supports --verbose/--debug flags, and can be invoked via `python -m email_tool`

- [ ] Task 2: Create daemon module for periodic sync and background processing
  - What: Create daemon.py with support for running as a background service, configurable intervals, and systemd/cron integration support
  - Files: email_tool/daemon.py (create), examples/daemon_config.yaml (create)
  - Done when: Daemon can run in background, supports --interval flag, has systemd timer example, and can be started/stopped via CLI

- [x] Task 3: Create optional web dashboard with FastAPI
  - What: Build a simple web dashboard showing organization stats, recent activity, and system health metrics
  - Files: email_tool/dashboard/__init__.py (create), email_tool/dashboard/app.py (create), email_tool/dashboard/templates/index.html (create)
  - Done when: Dashboard runs on configurable port, shows email counts by category, recent processing activity, and rule match statistics

- [ ] Task 4: Create package configuration and installable setup
  - What: Create setup.py or pyproject.toml with proper metadata, entry points for CLI, and dependency specifications
  - Files: pyproject.toml (create), setup.cfg (optional)
  - Done when: Package can be installed via `pip install -e .`, CLI commands are available system-wide, dependencies are properly specified

- [ ] Task 5: Create comprehensive documentation
  - What: Write README.md, config reference, rule syntax guide, connector setup guide, and dashboard usage docs
  - Files: docs/README.md (create), docs/config_reference.md (create), docs/rule_syntax.md (create), docs/connectors.md (create), docs/dashboard.md (create)
  - Done when: All documentation files exist with clear instructions, examples, and configuration references

- [ ] Task 6: Create example configurations for common use cases
  - What: Create example YAML configs for inbox zero, finance tracking, and document archiving scenarios
  - Files: examples/basic.yaml (create), examples/finance.yaml (create), examples/inbox_zero.yaml (create), examples/document_archiving.yaml (create)
  - Done when: Each example config is valid YAML, includes comments explaining sections, and can be used as starting points

- [ ] Task 7: Create CLI and daemon test suite
  - What: Write comprehensive tests for CLI commands, daemon functionality, config loading, and dashboard endpoints
  - Files: tests/test_cli.py (create), tests/test_daemon.py (create), tests/test_dashboard.py (create)
  - Done when: All CLI subcommands have tests, daemon scheduling is tested, config loading is validated, and dashboard endpoints are tested

- [ ] Task 8: Create systemd timer and cron job integration examples
  - What: Provide ready-to-use systemd timer files and cron job examples for automated periodic sync
  - Files: examples/systemd/email-tool.timer (create), examples/systemd/email-tool.service (create), examples/cron/email-tool-cron (create)
  - Done when: Users can copy systemd files to /etc/systemd/system/, enable and start the timer, and cron example works with standard crontab syntax