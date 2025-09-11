#!/bin/bash
export PYTHONPATH=${PWD}  # Thêm root repo vào sys.path, để Python tìm thấy 'backend' như module
uvicorn backend.main:app --host 0.0.0.0 --port $PORT