#!/bin/bash
cd /e/yt-tikshuv/tools/flow
PROJ="$(cat /e/yt-tikshuv/flow-project.txt)"
W="E:/Tikshuv Games/too-quiet/cutscene_work"
for id in $(cat "$W/remaining_ids.txt" | tr -d '\r'); do
  [ -f "$W/$id.mp4" ] && continue
  echo "=== $id $(date +%T)" >> "$W/rest.log"
  python flow_video.py --project "$PROJ" --prompt-file "$W/$id.txt" --aspect 16:9 --seconds 8 --res 360p --out "$W/$id.mp4" --wait-min 8 >> "$W/rest.log" 2>&1
  echo "exit $? $(date +%T)" >> "$W/rest.log"
done
echo RESTDONE >> "$W/rest.log"
