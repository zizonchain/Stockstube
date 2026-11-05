#!/bin/bash
# Every 30 minutes: restart the Reddit collector if it is not running and has not finished.
cd "$(dirname "$0")/.."
while true; do
  if ! pgrep -f run_reddit3.sh >/dev/null && ! grep -q 'DONE comments stocks' data/reddit3.log; then
    echo "$(date -u +%FT%H:%MZ) watchdog: collector down, restarting" >> data/watchdog.log
    nohup bash scripts/run_reddit3.sh >> data/reddit3.log 2>&1 &
  else
    echo "$(date -u +%FT%H:%MZ) watchdog: ok" >> data/watchdog.log
  fi
  sleep 1800
done
