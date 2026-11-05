#!/bin/bash
cd /e/yt-tikshuv/tools/flow
PROJ="$(cat /e/yt-tikshuv/flow-project.txt)"
W="E:/Tikshuv Games/too-quiet/cutscene_work"
for id in cs_bakery_chaos cs_valley_arrival lesson_start_01 cs_thread_storm; do
  echo "=== $id $(date +%T)" >> "$W/trial.log"
  python flow_video.py --project "$PROJ" --prompt-file "$W/$id.txt" --aspect 16:9 --seconds 8 --res 360p --out "$W/$id.mp4" --wait-min 8 >> "$W/trial.log" 2>&1
  echo "exit $? $(date +%T)" >> "$W/trial.log"
done
echo ALLDONE >> "$W/trial.log"
