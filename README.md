# claude-session-sidebar

A sidebar for the terminal that lists your running Claude Code sessions, like the desktop app does. Sessions that are working show Claude's spinner (· ✢ ✳ ✶ ✻ ✽).

```
 ✻ Claude sessions

 1 ✻ my-app
     fix the login bug
 2 ● website
     add a pricing page
 3 ! api
     update the schema
```

`✻` working, `●` idle, `!` waiting for you.

## Requirements
- tmux
- Python 3
- Claude Code

## Install
```bash
git clone <this repo>
cd claude-session-sidebar
./install.sh
```
Make sure `~/.local/bin` is on your PATH.

## Use
Run `ccs`. It opens tmux with the sidebar on the left. Start `claude` in the right pane. Each new tmux window (`prefix c`) gets its own sidebar.

`ccs kill` stops everything (ends the Claude sessions inside it). `ccs restart` stops and starts fresh; run it from a normal terminal, not inside tmux.

Keys in the sidebar: `j`/`k` or arrows to move, `Enter` or `1-9` to jump, `n` for a new Claude session in a new window, `q` to quit.

Only sessions started inside tmux show up.

## How it works
Claude Code hooks (SessionStart, UserPromptSubmit, PreToolUse, Notification, Stop, SessionEnd) run `hook.py`, which writes one small file per session in `~/.claude/session-sidebar/state/`. `sidebar.py` reads those files and redraws.

## Uninstall
```bash
./uninstall.sh
```
Your old settings are also saved at `~/.claude/settings.json.bak`.

## License
MIT
