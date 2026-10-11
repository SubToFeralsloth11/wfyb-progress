#!/usr/bin/env python3
"""Update progress.json and push.

  mark.py <status> <id> [<id> ...] [-m "log message"] [-n "current focus"] [-d "detail for the ids"]
  status: done | active | pending
"""
import argparse, datetime, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "progress.json")

ap = argparse.ArgumentParser()
ap.add_argument("status", choices=["done", "active", "pending"])
ap.add_argument("ids", nargs="*")
ap.add_argument("-m", "--message")
ap.add_argument("-n", "--now")
ap.add_argument("-d", "--detail")
a = ap.parse_args()

data = json.load(open(PATH))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
steps = {s["id"]: s for p in data["phases"] for s in p["steps"]}
unknown = [i for i in a.ids if i not in steps]
if unknown:
    sys.exit(f"unknown step ids: {unknown}")
for i in a.ids:
    steps[i]["status"] = a.status
    steps[i]["updated"] = now
    if a.detail is not None:
        steps[i]["detail"] = a.detail
if a.now:
    data["current"] = a.now
if a.message:
    data["log"].append({"t": now, "msg": a.message})
    data["log"] = data["log"][-50:]
data["updated"] = now
json.dump(data, open(PATH, "w"), indent=1)

msg = a.message or f"Mark {', '.join(a.ids)} {a.status}"
subprocess.run(["git", "add", "progress.json"], cwd=HERE, check=True)
subprocess.run(["git", "commit", "-qm", msg], cwd=HERE, check=True)
subprocess.run(["git", "push", "-q"], cwd=HERE, check=True)
done = sum(s["status"] == "done" for s in steps.values())
print(f"{done}/{len(steps)} done")
