# ducas-agent-skills

A collection of reusable Claude agent skills for personal automation and tooling.
Each skill is a self-contained directory that teaches Claude how to handle a
specific task. Skills are loaded by Claude Code on the web via the Skills system.

## Repository layout

```
ducas-agent-skills/
├── CLAUDE.md                        # This file
├── README.md                        # Human-facing docs and skills table
├── .gitignore
├── .claude/
│   └── settings.json                # Pre-approved commands for Claude Code
├── _template/
│   └── SKILL.md                     # Template — copy this when adding a skill
├── scripts/
│   └── validate_skills.py           # Validates all skill directories
└── <skill-name>/                    # One directory per skill (kebab-case)
    ├── SKILL.md                     # Required — frontmatter + Claude instructions
    └── scripts/                     # Optional — helper scripts the skill uses
        └── *.py
```

## Naming conventions

- Skill directory names must be lowercase kebab-case: `ha-stats-export`, `gmail-search`
- The `name` field in `SKILL.md` frontmatter must match the directory name exactly
- Helper script directories inside a skill are always named `scripts/` (not `bin/`)

## How to add a new skill

1. Create a new directory at the repo root: `<skill-name>/`
2. Copy `_template/SKILL.md` into it as `<skill-name>/SKILL.md`
3. Fill in all frontmatter fields (`name`, `description`) — remove every `<PLACEHOLDER>` marker
4. Replace all placeholder sections in the body with real content
5. Add a `scripts/` subdirectory only if the skill requires helper scripts
6. Add the skill to the skills table in `README.md`
7. Run `python3 scripts/validate_skills.py` and fix any errors before committing

## SKILL.md contract

Every `SKILL.md` must have:

**Frontmatter** (between `---` delimiters at the top of the file):

| Field | Requirement |
|---|---|
| `name` | Must match the directory name exactly |
| `description` | One paragraph including explicit trigger phrases — when should Claude activate this skill? Be specific and include edge cases. |

**Body sections** (in this order, using `##` headings):

| Section | Required | Notes |
|---|---|---|
| `## What this skill produces` | Yes | Bullet list of outputs/artifacts |
| `## Running via Desktop Commander` | Only if applicable | How to invoke via `start_process`; omit if not relevant |
| `## Key API / tool details` | Yes | Auth, request format, response format, important options |
| `## Troubleshooting` | Yes | Common errors and their fixes |
| `## Dependencies` | Yes | Python version and pip packages |

## Validation

Always run before committing:

```bash
python3 scripts/validate_skills.py
```

Exit code 0 = all skills valid. Non-zero + printed errors = fix before committing.

## Invariants

- `_template/` is **not** a real skill — the validator skips it
- Never commit a `SKILL.md` that still contains `<PLACEHOLDER>` text
- The `scripts/` directory at the repo root is shared tooling, not a skill
