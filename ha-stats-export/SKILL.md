---
name: ha-stats-export
description: >
  Export long-term statistics from Home Assistant to CSV using the WebSocket API
  and a Python script. Use this skill whenever the user wants to pull, download,
  extract, or export historical statistics or sensor data from Home Assistant —
  especially when they mention entity IDs, date ranges, periods (hourly, daily,
  etc.), energy data, temperature logs, or any time-series data stored in HA's
  long-term statistics. Also trigger when the user wants a Python script that
  connects to Home Assistant via WebSocket to retrieve or save statistics. Use
  this skill even if the user just says "export my HA data" or "get stats from
  Home Assistant" without specifying a format.
---

# Home Assistant Long-Term Statistics Exporter

Generates and runs a Python script that connects to a Home Assistant instance
via the WebSocket API and exports long-term statistics for one or more entities
to CSV.

## What this skill produces

A Python script (inline or saved to disk) that:
- Connects to HA via WebSocket (`ws://` for local, `wss://` for Nabu Casa cloud)
- Authenticates using a long-lived access token
- Calls `recorder/statistics_during_period` to fetch aggregates
- Accepts either a **date range** (`--start` / `--end`) or a **rolling period** (`--last 30d`)
- Accepts one or more `--entity` IDs
- Writes to CSV with columns: `entity_id, start, end, mean, min, max, sum, state`
- Requires only stdlib + `websockets` (`pip install websockets`)

## Running via Desktop Commander

When Desktop Commander is available, **run the script directly** rather than
just generating it for the user. Use `start_process` with an inline python3 -c
command (see template below). Set `timeout_ms` to 30000.

### Inline script template (Desktop Commander)

```python
import asyncio, json, websockets, csv
from datetime import datetime, timezone
from pathlib import Path

TOKEN  = '<TOKEN>'
URL    = '<WS_URL>/api/websocket'   # e.g. wss://xxx.ui.nabu.casa/api/websocket
ENTITY = '<ENTITY_ID>'
START  = '<YYYY-MM-DDT00:00:00.000Z>'
END    = '<YYYY-MM-DDT00:00:00.000Z>'

def ms_to_dt(ms):
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc).isoformat()

async def main():
    print('Connecting...')
    async with websockets.connect(URL) as ws:
        msg = json.loads(await ws.recv())
        await ws.send(json.dumps({'type': 'auth', 'access_token': TOKEN}))
        msg = json.loads(await ws.recv())
        print('Auth:', msg.get('type'))
        if msg.get('type') != 'auth_ok':
            print('FAILED:', msg); return
        await ws.send(json.dumps({
            'id': 1, 'type': 'recorder/statistics_during_period',
            'start_time': START, 'end_time': END,
            'statistic_ids': [ENTITY], 'period': 'hour',
            'types': ['mean','min','max','sum','state'],
        }))
        response = json.loads(await ws.recv())
    if not response.get('success'):
        print('Error:', response); return
    rows = response['result'].get(ENTITY, [])
    print(f'Got {len(rows)} rows')
    out = Path.home() / 'ha_statistics.csv'
    with out.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['entity_id','start','end','mean','min','max','sum','state'])
        w.writeheader()
        for row in rows:
            w.writerow({'entity_id': ENTITY,
                'start': ms_to_dt(row['start']), 'end': ms_to_dt(row['end']),
                'mean': row.get('mean',''), 'min': row.get('min',''),
                'max': row.get('max',''), 'sum': row.get('sum',''),
                'state': row.get('state','')})
    print(f'Done! Written to {out}')

asyncio.run(main())
```

## Key API details

### Authentication handshake
```
connect → ws(s)://<host>/api/websocket
← {"type": "auth_required"}
→ {"type": "auth", "access_token": "<TOKEN>"}
← {"type": "auth_ok"}  |  {"type": "auth_invalid"}
```

### statistics_during_period command
```json
{
  "id": 1,
  "type": "recorder/statistics_during_period",
  "start_time": "2026-04-01T00:00:00.000Z",
  "end_time":   "2026-05-27T00:00:00.000Z",
  "statistic_ids": ["sensor.my_entity"],
  "period": "hour",
  "types": ["mean", "min", "max", "sum", "state"]
}
```

**period** values: `"5minute"`, `"hour"`, `"day"`, `"week"`, `"month"`

**Response** — timestamps are Unix milliseconds:
```json
{
  "result": {
    "sensor.my_entity": [
      {"start": 1743465600000, "end": 1743469200000,
       "mean": 21.4, "min": 20.1, "max": 22.9}
    ]
  }
}
```

Columns present depend on entity's `state_class`:
- `measurement` → `mean`, `min`, `max`
- `total` / `total_increasing` → `sum`, `state`

### URL format
| Setup | URL format |
|---|---|
| Local network | `ws://192.168.x.x:8123` |
| Nabu Casa cloud | `wss://xxxxx.ui.nabu.casa` |

### Period shorthand → date range
| Input | Meaning |
|---|---|
| `--last 24h` | last 24 hours |
| `--last 7d` | last 7 days |
| `--last 2w` | last 14 days |
| `--last 3mo` | last ~90 days |

## Troubleshooting

- **auth_invalid** — Token is wrong or expired. Ask user to create a new
  long-lived access token at **Profile → Security → Long-lived access tokens**.
- **HTTP 403** — Nabu Casa cloud may reject connections from certain IPs
  (e.g. cloud sandboxes). If running via Desktop Commander this should work
  fine. If running from a cloud CI/server, use the local IP instead.
- **Empty result** — Entity ID may be wrong, or no statistics recorded for
  that period. Confirm the entity ID in HA's Developer Tools → Statistics.

## Dependencies
- Python 3.9+
- `websockets` library (`pip install websockets`)
