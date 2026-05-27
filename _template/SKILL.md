<!--
  Copy this file to <skill-name>/SKILL.md and replace every <PLACEHOLDER> marker.
  Run `python3 scripts/validate_skills.py` before committing.
-->
---
name: <PLACEHOLDER>
description: >
  <PLACEHOLDER: One paragraph. Include the specific trigger phrases that should
  activate this skill — e.g. "Use this skill when the user wants to ..., or
  mentions ..., or asks about ...". Be explicit about edge cases and loose
  phrasings that should still trigger this skill.>
---

# <PLACEHOLDER: Human-Readable Skill Title>

<PLACEHOLDER: One-sentence summary of what this skill does.>

## What this skill produces

- <PLACEHOLDER: bullet describing the primary output or artifact>
- <PLACEHOLDER: additional outputs if any>

## Running via Desktop Commander

<PLACEHOLDER: If this skill can be run via Desktop Commander, describe how here
(use `start_process`, set `timeout_ms`, show the inline template). If it cannot,
delete this section entirely.>

## Key API / tool details

<PLACEHOLDER: Cover authentication, request/command format, response format, and
any important options or caveats. Use fenced code blocks for JSON schemas,
command templates, and example responses.>

## Troubleshooting

- **<PLACEHOLDER: error name>** — <PLACEHOLDER: cause and fix>
- **<PLACEHOLDER: error name>** — <PLACEHOLDER: cause and fix>

## Dependencies

- <PLACEHOLDER: e.g. Python 3.9+>
- <PLACEHOLDER: e.g. `websockets` library (`pip install websockets`)>
