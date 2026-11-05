#!/bin/bash
# usage: run_music.sh tag1 tag2 ...   (runs one at a time; never while a video script runs)
S="E:/esacpe-planner/escaperoom-design/.claude/skills/google-flow/scripts"
W="E:/Tikshuv Games/too-quiet/cutscene_work"
mkdir -p "$W/music"
for t in "$@"; do
  echo "=== $t $(date +%T)" >> "$W/music.log"
  python "$S/flow_music.py" --prompt-file "$W/music-prompts.md" --tag "$t" --out "$W/music" --prefix "$t" >> "$W/music.log" 2>&1
  echo "exit $? $(date +%T)" >> "$W/music.log"
done
echo MUSICDONE >> "$W/music.log"
