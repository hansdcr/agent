#!/bin/bash
# AI Agent 启动脚本

# 使用 uv 运行 uvicorn，排除虚拟环境目录的监控
uv run uvicorn main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --reload \
  --reload-exclude '.venv/*' \
  --reload-exclude '__pycache__/*' \
  --reload-exclude '*.pyc'
