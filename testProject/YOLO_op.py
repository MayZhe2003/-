import cv2
import face_recognition

# 加载用户输入的图片
sticker_image = cv2.imread('your_sticker_image.png', -1)

# 打开系统摄像头
cap = cv2.VideoCapture(0)

while True:
    # 读取一帧摄像头画面
    ret, frame = cap.read()

    if not ret:
        break

    # 转换为 RGB 格式，因为 face_recognition 库使用 RGB 格式
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 检测人脸位置
    face_locations = face_recognition.face_locations(rgb_frame)

    for (top, right, bottom, left) in face_locations:
        # 获取人脸的宽度和高度
        face_width = right - left
        face_height = bottom - top

        # 调整贴纸图片的大小以适应人脸
        resized_sticker = cv2.resize(sticker_image, (face_width, face_height))

        # 提取贴纸的透明度通道
        alpha_sticker = resized_sticker[:, :, 3] / 255.0
        alpha_frame = 1.0 - alpha_sticker

        # 遍历贴纸的每个像素
        for c in range(0, 3):
            frame[top:bottom, left:right, c] = (
                alpha_sticker * resized_sticker[:, :, c] +
                alpha_frame * frame[top:bottom, left:right, c]
            )

    # 显示处理后的画面
    cv2.imshow('Face Sticker', frame)

    # 按 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头并关闭所有窗口
cap.release()
cv2.destroyAllWindows()