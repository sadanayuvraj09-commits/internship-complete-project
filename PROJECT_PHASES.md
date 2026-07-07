# Unbilled Revenue Detective Phase Map

This file documents which project phase each source, script, and test file serves.
It is intentionally a documentation tag map, not a file move, so existing imports
and commands keep working.

## Phase Tags

- P1: Data Collection
- P2: Digital Footprint Building
- P3: Timesheet Comparison
- P4: AI Analysis and Alerts
- SUPPORT: Configuration, database, utilities, local scripts, and manual tests

## Source Files

| File | Tags | Purpose |
| --- | --- | --- |
| `src/main.py` | P1, P2, P3, P4 | FastAPI route layer for ingestion, gap detection, summary generation, and alerting. |
| `src/github_service.py` | P1 | Fetches GitHub commits (with pagination) and stores them in `activity_logs`. |
| `src/slack_service.py` | P1 | Fetches Slack messages and stores them in `activity_logs`. |
| `src/jira_service.py` | P1 | Fetches Jira issue activity and stores it in `activity_logs`. |
| `src/footprint_service.py` | P2 | Aggregates GitHub, Slack, and Jira activity into a developer/day footprint. |
| `src/ai_service.py` | P4 | Generates natural language summaries, priority classification, timesheet suggestions, and Q&A with Gemini. |
| `src/alert_service.py` | P4 | Generates and stores alerts from detected gaps; sends Slack and email notifications. |
| `src/activity_utils.py` | SUPPORT | Shared date and developer normalization helpers. |
| `src/config.py` | SUPPORT | Environment variable configuration. |
| `src/database.py` | SUPPORT | Shared MongoDB client and database handle. |
| `src/__init__.py` | SUPPORT | Marks `src` as an importable package. |

## Scripts

| File | Tags | Purpose |
| --- | --- | --- |
| `scripts/insert_developers.py` | SUPPORT, P3 | Seeds developer records used for matching activity to timesheets. |
| `scripts/check_gaps.py` | SUPPORT, P3, P4 | Inspects persisted detected gaps. |
| `scripts/reset_gaps.py` | SUPPORT, P3 | Clears gap detection output for reruns. |
| `scripts/fix_dates.py` | SUPPORT, P3 | One-time repair script for missing dates in early gap records; not part of runtime. |
| `scripts/fix_summaries.py` | SUPPORT, P4 | One-time repair script for malformed AI summary text; not part of runtime. |
| `scripts/summarize_gaps.py` | SUPPORT, P4 | Local summary generation helper. |
| `scripts/cleanup_commits.py` | SUPPORT, P1 | One-time repair script that removed old malformed activity records; not part of runtime. |
| `scripts/check_git_path.py` | SUPPORT |