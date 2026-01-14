#!/bin/bash

# 查找 uvicorn 进程
PID=$(ps aux | grep "[u]vicorn /Users/andy/Servers/checkin_server/app:app" | awk '{print $2}')

if [ -z "$PID" ]; then
  echo "服务未运行"
else
  echo "正在关闭服务，PID=$PID"
  kill -9 $PID
  echo "服务已关闭"
fi
