#!/usr/bin/env bash
set -e
SETTINGS="$HOME/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
python3 - "$SETTINGS" <<'PY'
import json, sys
p = sys.argv[1]
s = json.load(open(p))
cmd = "python3 ~/.claude/session-sidebar/hook.py"
h = s.get("hooks", {})
for ev in list(h):
    h[ev] = [g for g in h[ev] if not any(x.get("command") == cmd for x in g.get("hooks", []))]
    if not h[ev]: del h[ev]
if not h: s.pop("hooks", None)
json.dump(s, open(p, "w"), indent=2)
PY
fi
rm -rf "$HOME/.claude/session-sidebar" "$HOME/.local/bin/ccs"
echo "Uninstalled."
