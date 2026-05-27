# ducas-agent-skills

A collection of Claude agent skills for personal automation and tooling.

## What are skills?

Skills are reusable instructions and scripts that teach Claude how to handle
specific tasks — connecting to APIs, exporting data, automating workflows, etc.
Each skill lives in its own folder with a `SKILL.md` file and optional scripts
or reference files.

## Skills

| Skill | Description |
|---|---|
| [ha-stats-export](./ha-stats-export/) | Export long-term statistics from Home Assistant to CSV via the WebSocket API |

## Installing a skill

1. Download the `.skill` file from the [Releases](../../releases) page
2. Drop it into your Claude skills folder

## Structure

```
ducas-agent-skills/
└── ha-stats-export/
    ├── SKILL.md                  # Skill instructions for Claude
    └── scripts/
        └── export_ha_stats.py   # Standalone Python script
```
