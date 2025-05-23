import cv2
import numpy as np
import time
from ultralytics import YOLO
import pygame
import argparse

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='YOLOv8实时人车检测应用')
    parser.add_argument('--camera', type=int, default=0, help='摄像头索引，默认为0')
    parser.add_argument('--threshold', type=float, default=0.5, help='检测置信度阈值，默认为0.5')
    parser.add_argument('--person_count', type=int, default=3, help='触发警报的人数阈值，默认为3')
    args = parser.parse_args()

    # 初始化YOLOv8模型
    model = YOLO("yolov8n.pt")  # 使用yolov8n.pt，这是一个较小的模型，适合实时应用
    
    # 初始化摄像头
    cap = cv2.VideoCapture(args.camera)
    
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return
    
    # 设置摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # 初始化pygame用于播放警报声音
    pygame.mixer.init()
    pygame.mixer.music.load("alarm.mp3")  # 请确保在同一目录下有alarm.mp3文件
    
    # 警报状态和冷却时间
    alarm_active = False
    last_alarm_time = 0
    alarm_cooldown = 5  # 警报冷却时间（秒）
    
    # 显示FPS的变量
    prev_time = 0
    
    print("按'q'键退出程序")
    
    while True:
        # 读取一帧
        ret, frame = cap.read()
        if not ret:
            print("无法获取画面")
            break
        
        # 计算FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time > 0 else 0
        prev_time = current_time
        
        # 使用YOLOv8进行检测
        results = model(frame, classes=[0, 2], conf=args.threshold)  # 只检测人(0)和汽车(2)
        
        # 处理检测结果
        person_count = 0
        car_count = 0
        
        # 在图像上绘制检测结果
        annotated_frame = results[0].plot()
        
        # 统计人和车的数量
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # 人
                    person_count += 1
                elif cls == 2:  # 汽车
                    car_count += 1
        
        # 显示人和车的数量
        cv2.putText(annotated_frame, f"number of persons: {person_count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"number of cars: {car_count}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"FPS: {int(fps)}", (10, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 检查是否需要触发警报
        if person_count >= args.person_count:
            # 在画面上显示警报
            cv2.putText(annotated_frame, "警报：检测到过多人员！", (10, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # 如果警报未激活或已经过了冷却时间，则触发警报
            if not alarm_active or (current_time - last_alarm_time) > alarm_cooldown:
                pygame.mixer.music.play()
                alarm_active = True
                last_alarm_time = current_time
        else:
            alarm_active = False
        
        # 显示结果
        cv2.imshow("YOLOv8实时检测", annotated_frame)
        
        # 按'q'键退出
        if cv2.waitKey(1) == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 