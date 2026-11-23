#!/usr/bin/env bash
# Keep every sidebar pane at a fixed width (tmux scales panes on attach/resize).
W="${CCS_WIDTH:-28}"
tmux list-panes -a -F '#{pane_id} #{pane_title}' | while read -r id title; do
  [ "$title" = "claude-sidebar" ] && tmux resize-pane -t "$id" -x "$W"
done
exit 0
