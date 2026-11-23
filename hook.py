#!/usr/bin/env python3
"""Claude Code hook: record this session's status for the sidebar."""
import json, os, sys, time

STATE_DIR = os.path.expanduser("~/.claude/session-sidebar/state")
STATUS = {
    "SessionStart": "idle",
    "UserPromptSubmit": "working",
    "PreToolUse": "working",
    "Notification": "waiting",
    "Stop": "idle",
}

def main():
    try:
        data = json.load(sys.stdin)
        sid = str(data.get("session_id", ""))
        event = data.get("hook_event_name", "")
        if not sid:
            return
        os.makedirs(STATE_DIR, exist_ok=True)
        path = os.path.join(STATE_DIR, sid + ".json")
        if event == "SessionEnd":
            if os.path.exists(path):
                os.remove(path)
            return
        if event not in STATUS:
            return
        old = {}
        try:
            with open(path) as f:
                old = json.load(f)
        except Exception:
            pass
        prompt = old.get("prompt", "")
        if event == "UserPromptSubmit":
            prompt = " ".join(str(data.get("prompt", "")).split())[:80]
        pane = os.environ.get("TMUX_PANE") or old.get("pane", "")
        state = {
            "status": STATUS[event],
            "cwd": data.get("cwd") or old.get("cwd", ""),
            "prompt": prompt,
            "pane": pane,
            "updated": time.time(),
        }
        if pane:  # drop older session files that belong to the same pane
            for f in os.listdir(STATE_DIR):
                fp = os.path.join(STATE_DIR, f)
                if f.endswith(".json") and fp != path:
                    try:
                        with open(fp) as fh:
                            if json.load(fh).get("pane") == pane:
                                os.remove(fp)
                    except Exception:
                        pass
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(state, f)
        os.replace(tmp, path)
    except Exception:
        pass

if __name__ == "__main__":
    main()
    sys.exit(0)
