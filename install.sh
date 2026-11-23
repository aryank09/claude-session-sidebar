#!/usr/bin/env bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/session-sidebar"
SETTINGS="$HOME/.claude/settings.json"
command -v tmux >/dev/null || { echo "tmux is required"; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }
mkdir -p "$DEST/state" "$HOME/.local/bin" "$HOME/.claude"
cp "$SRC/hook.py" "$SRC/sidebar.py" "$SRC/pin.sh" "$DEST/"
chmod +x "$DEST/pin.sh"
cp "$SRC/ccs" "$HOME/.local/bin/ccs"
chmod +x "$HOME/.local/bin/ccs"
[ -f "$SETTINGS" ] && cp "$SETTINGS" "$SETTINGS.bak"
python3 - "$SETTINGS" <<'PY'
import json, os, sys
p = sys.argv[1]
s = json.load(open(p)) if os.path.exists(p) else {}
cmd = "python3 ~/.claude/session-sidebar/hook.py"
hooks = s.setdefault("hooks", {})
for ev in ["SessionStart", "UserPromptSubmit", "PreToolUse", "Notification", "Stop", "SessionEnd"]:
    groups = hooks.setdefault(ev, [])
    if not any(h.get("command") == cmd for g in groups for h in g.get("hooks", [])):
        groups.append({"hooks": [{"type": "command", "command": cmd}]})
json.dump(s, open(p, "w"), indent=2)
PY
echo "Installed. Make sure ~/.local/bin is on your PATH, then run: ccs"
