#!/usr/bin/env python3
"""
export_ha_stats.py
------------------
Export Home Assistant long-term statistics to CSV via the WebSocket API.

Quick start:
  pip install websockets
  python export_ha_stats.py \
    --url wss://xxxxx.ui.nabu.casa \
    --token YOUR_TOKEN \
    --entity sensor.my_entity \
    --start 2026-04-01 --end 2026-05-27

Or use a rolling window:
  python export_ha_stats.py \
    --url wss://xxxxx.ui.nabu.casa \
    --token YOUR_TOKEN \
    --entity sensor.my_entity \
    --last 30d
"""

import argparse
import asyncio
import csv
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import websockets
except ImportError:
    sys.exit("Missing dependency: run  pip install websockets  then try again.")


def parse_date(value):
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(f"Cannot parse date '{value}'. Use YYYY-MM-DD.")


def parse_last(value):
    m = re.fullmatch(r"(\d+)(h|d|w|mo)", value.strip())
    if not m:
        raise argparse.ArgumentTypeError(f"Cannot parse '{value}'. Use e.g. 24h, 7d, 2w, 3mo.")
    n, unit = int(m.group(1)), m.group(2)
    return {"h": timedelta(hours=n), "d": timedelta(days=n),
            "w": timedelta(weeks=n), "mo": timedelta(days=n * 30)}[unit]


def ms_to_dt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


async def fetch_statistics(url, token, entity_ids, start, end, period):
    ws_url = url.rstrip("/") + "/api/websocket"
    print(f"Connecting to {ws_url} ...")
    async with websockets.connect(ws_url) as ws:
        msg = json.loads(await ws.recv())
        assert msg.get("type") == "auth_required", f"Unexpected: {msg}"
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        msg = json.loads(await ws.recv())
        if msg.get("type") == "auth_invalid":
            sys.exit("Authentication failed — check your access token.")
        assert msg.get("type") == "auth_ok", f"Unexpected: {msg}"
        print("Authenticated. Fetching statistics ...")
        await ws.send(json.dumps({
            "id": 1,
            "type": "recorder/statistics_during_period",
            "start_time": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "end_time":   end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "statistic_ids": entity_ids,
            "period": period,
            "types": ["mean", "min", "max", "sum", "state"],
        }))
        response = json.loads(await ws.recv())
    if not response.get("success"):
        err = response.get("error", {})
        sys.exit(f"API error {err.get('code','?')}: {err.get('message', response)}")
    return response.get("result", {})


FIELDNAMES = ["entity_id", "start", "end", "mean", "min", "max", "sum", "state"]


def write_csv(result, output_path):
    total = 0
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for entity_id, rows in sorted(result.items()):
            if not rows:
                print(f"  Warning: no data for {entity_id}")
                continue
            for row in rows:
                writer.writerow({
                    "entity_id": entity_id,
                    "start":  ms_to_dt(row["start"]),
                    "end":    ms_to_dt(row["end"]),
                    "mean":   row.get("mean",  ""),
                    "min":    row.get("min",   ""),
                    "max":    row.get("max",   ""),
                    "sum":    row.get("sum",   ""),
                    "state":  row.get("state", ""),
                })
                total += 1
    return total


def build_parser():
    p = argparse.ArgumentParser(description="Export Home Assistant statistics to CSV.")
    p.add_argument("--url",    required=True,
                   help="WebSocket URL, e.g. wss://xxxxx.ui.nabu.casa or ws://192.168.x.x:8123")
    p.add_argument("--token",  required=True, help="Long-lived access token.")
    p.add_argument("--entity", dest="entities", nargs="+", required=True, metavar="ENTITY_ID")
    p.add_argument("--period", default="hour",
                   choices=["5minute", "hour", "day", "week", "month"])
    p.add_argument("--output", default="ha_statistics.csv", metavar="FILE")
    tg = p.add_mutually_exclusive_group(required=True)
    tg.add_argument("--last",  metavar="DURATION", help="e.g. 24h, 7d, 2w, 3mo")
    tg.add_argument("--start", type=parse_date, metavar="DATE")
    p.add_argument("--end",    type=parse_date, metavar="DATE", default=None)
    return p


def main():
    args = build_parser().parse_args()
    now = datetime.now(tz=timezone.utc)
    if args.last:
        start, end = now - parse_last(args.last), now
    else:
        start, end = args.start, args.end or now
    if end <= start:
        sys.exit("--end must be after --start.")
    print(f"Range   : {start.date()} → {end.date()}")
    print(f"Period  : {args.period}")
    print(f"Entities: {', '.join(args.entities)}")
    result = asyncio.run(
        fetch_statistics(args.url, args.token, args.entities, start, end, args.period)
    )
    rows = write_csv(result, Path(args.output))
    print(f"\nWrote {rows} rows to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
