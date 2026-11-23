#!/usr/bin/env python3
"""Sidebar listing Claude Code sessions running in tmux."""
import glob, json, os, select, subprocess, sys, termios, time, tty

STATE_DIR = os.path.expanduser("~/.claude/session-sidebar/state")
FRAMES = ["·", "✢", "✳", "✶", "✻", "✽", "✻", "✶", "✳", "✢"]
ORANGE, YELLOW, DIM, BOLD, REV, RST = "\033[38;5;173m", "\033[33m", "\033[2m", "\033[1m", "\033[7m", "\033[0m"
MAX_AGE = 24 * 3600

def tmux(*args):
    try:
        return subprocess.run(["tmux", *args], capture_output=True, text=True).stdout
    except Exception:
        return ""

def load():
    panes = {}
    for line in tmux("list-panes", "-a", "-F", "#{pane_id}\t#{window_id}").splitlines():
        p, w = line.split("\t")
        panes[p] = w
    rows = []
    now = time.time()
    for f in glob.glob(os.path.join(STATE_DIR, "*.json")):
        try:
            s = json.load(open(f))
        except Exception:
            continue
        if s.get("pane") not in panes or now - s.get("updated", 0) > MAX_AGE:
            continue
        s["window"] = panes[s["pane"]]
        rows.append(s)
    rows.sort(key=lambda s: (s["window"], s["pane"]))
    return rows

def clip(t, n):
    return t if len(t) <= n else t[: max(n - 1, 0)] + "…"

def render(rows, sel, tick, cur_window, w, h):
    out = ["\033[H\033[2J", f"{BOLD}{ORANGE} ✻ Claude sessions{RST}\n\n"]
    if not rows:
        out.append(f"{DIM} No sessions yet.\n Run `claude` in\n another pane.{RST}\n")
    for i, s in enumerate(rows):
        st = s["status"]
        if st == "working":
            icon = f"{ORANGE}{FRAMES[tick % len(FRAMES)]}{RST}"
        elif st == "waiting":
            icon = f"{YELLOW}!{RST}"
        else:
            icon = f"{DIM}●{RST}"
        name = os.path.basename(s.get("cwd", "").rstrip("/")) or "?"
        mark = REV if i == sel else (BOLD if s["window"] == cur_window else "")
        out.append(f"{mark} {i+1} {icon}{mark} {clip(name, w-6)}{RST}\n")
        if s.get("prompt"):
            out.append(f"{DIM}     {clip(s['prompt'], w-6)}{RST}\n")
    out.append(f"\033[{h};1H{DIM} j/k move  ⏎ jump  q quit{RST}"[: 200])
    sys.stdout.write("".join(out))
    sys.stdout.flush()

def jump(s):
    tmux("select-window", "-t", s["window"])
    tmux("select-pane", "-t", s["pane"])

def main():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    sys.stdout.write("\033[?1049h\033[?25l")
    tty.setcbreak(fd)
    sel, tick = 0, 0
    try:
        while True:
            rows = load()
            sel = min(sel, max(len(rows) - 1, 0))
            cur = tmux("display-message", "-p", "#{window_id}").strip()
            w, h = os.get_terminal_size()
            render(rows, sel, tick, cur, w, h)
            tick += 1
            if select.select([fd], [], [], 0.12)[0]:
                k = os.read(fd, 8).decode(errors="ignore")
                if k in ("q", "\x03"):
                    break
                elif k in ("j", "\x1b[B"):
                    sel = min(sel + 1, len(rows) - 1)
                elif k in ("k", "\x1b[A"):
                    sel = max(sel - 1, 0)
                elif k in ("\r", "\n") and rows:
                    jump(rows[sel])
                elif k.isdigit() and 1 <= int(k) <= len(rows):
                    sel = int(k) - 1
                    jump(rows[sel])
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write("\033[?25h\033[?1049l")

if __name__ == "__main__":
    main()
