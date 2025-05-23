#!/bin/bash

# 创建虚拟环境（推荐）
python -m venv yolo_env
source yolo_env/bin/activate

# 安装依赖
pip install ultralytics opencv-python pygame numpy

# 下载警报声音文件（如果没有）
curl -o alarm.mp3 https://example.com/alarm.mp3  # 请替换为实际的警报声音文件URL