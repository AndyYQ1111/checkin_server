#!/bin/bash

# 切换到项目目录
cd /Users/andy/Servers/checkin_server || exit 1

# 使用虚拟环境完整路径启动 uvicorn
exec /Users/andy/Servers/checkin_server/venv_checkin_server/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000
