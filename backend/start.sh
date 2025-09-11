#!/bin/bash
export PYTHONPATH=/opt/render/project/src  # Path chuẩn của Render
uvicorn backend.main:app --host 0.0.0.0 --port $PORT