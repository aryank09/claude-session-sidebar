# claude-session-sidebar

A tmux sidebar that lists running Claude Code sessions (project folder, status, last prompt) with Claude's spinner for sessions that are working. Pure Python 3 stdlib + bash. MIT licensed. Repo is private for now.

## How it works
Claude Code hooks run `hook.py` on events and write one JSON file per session to `~/.claude/session-sidebar/state/`. `sidebar.py` runs in a tmux pane, reads those files and tmux pane info, and redraws ~8x/sec. `ccs` starts tmux with the sidebar on the left.

## Files
- `hook.py` — hook script. Maps events to status (SessionStart/Stop → idle, UserPromptSubmit/PreToolUse → working, Notification → waiting unless it is an idle notice, SessionEnd → delete). Removes older state files for the same pane. Never prints or fails.
- `sidebar.py` — the UI. One row per pane, live folder from tmux `pane_current_path`, spinner `· ✢ ✳ ✶ ✻ ✽`. Keys: j/k/arrows, Enter or 1-9 jump, `n` new session in highlighted folder, `q` quit.
- `ccs` — launcher. `ccs` / `ccs start`, `ccs kill`, `ccs restart`. Sidebar width 28 (`CCS_WIDTH`), re-pinned on attach/resize, mouse on, `prefix h`/`prefix l` switch panes, hook adds a sidebar to every new window.
- `install.sh` / `uninstall.sh` — copy files to `~/.claude/session-sidebar/` and `~/.local/bin/ccs`, merge/remove the 6 hooks in `~/.claude/settings.json` (backup at `settings.json.bak`).
- `README.md`, `LICENSE`, `.gitignore` — docs, MIT, ignores.

## Working on it
- After editing, copy to the installed location (`./install.sh`) — the running copies are in `~/.claude/session-sidebar/` and `~/.local/bin/ccs`.
- Restart to pick up sidebar changes: `ccs kill` then `ccs` (ends Claude sessions inside tmux).
- Test on a separate tmux socket (`tmux -L test`) and a temp `$HOME`, not the user's live session.
- Syntax check: `python3 -m py_compile hook.py sidebar.py && bash -n ccs install.sh uninstall.sh`.

## Gotchas
- Ctrl+Arrow is taken by macOS Mission Control, so pane switching uses `prefix h/l`.
- Only sessions started inside tmux appear (state needs `$TMUX_PANE`).
- tmux scales panes proportionally on attach; `ccs` pins the width via client-attached/client-resized hooks.
- Claude's "waiting for your input" notification must not be treated as "needs you".
- Before commit/push, follow the privacy check in the user's global CLAUDE.md.
