import sys
import cv2
import numpy as np
import time
from ultralytics import YOLO
import pygame
import threading
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                            QPushButton, QVBoxLayout, QHBoxLayout, QSpinBox, 
                            QDoubleSpinBox, QGroupBox, QComboBox, QCheckBox,
                            QFileDialog, QTabWidget, QRadioButton, QButtonGroup,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                            QDateTimeEdit, QPushButton, QLineEdit, QFrame)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
import mysql.connector
from db_config import DB_CONFIG
from datetime import datetime

class StyleSheet:
    @staticmethod
    def get_main_style():
        return """
            QMainWindow {
                background-color: #f0f2f5;
            }
            
            QTabWidget::pane {
                border: none;
                background: #f0f2f5;
            }
            
            QTabBar::tab {
                padding: 8px 20px;
                margin: 0px 2px;
                border: none;
                background: #e4e6e9;
                color: #666;
            }
            
            QTabBar::tab:selected {
                background: #1890ff;
                color: white;
            }
            
            QGroupBox {
                border: 2px solid #e4e6e9;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 24px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #666;
            }
            
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #40a9ff;
            }
            
            QPushButton:pressed {
                background-color: #096dd9;
            }
            
            QPushButton:disabled {
                background-color: #d9d9d9;
            }
            
            QLabel {
                color: #333;
            }
            
            QSpinBox, QDoubleSpinBox {
                padding: 4px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
            }
            
            QComboBox {
                padding: 4px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
            }
            
            QCheckBox {
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #e6f7ff;
                color: #333;
            }
            
            QHeaderView::section {
                background-color: #fafafa;
                padding: 8px;
                border: none;
                border-right: 1px solid #f0f0f0;
                border-bottom: 1px solid #f0f0f0;
                color: #666;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #d9d9d9;
                min-height: 30px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
    
    @staticmethod
    def get_start_page_style():
        return """
            QWidget#startPage {
                background-color: white;
            }
            
            QLabel#titleLabel {
                font-size: 32px;
                font-weight: bold;
                color: #1890ff;
                margin: 20px;
            }
            
            QPushButton#startButton {
                font-size: 16px;
                padding: 12px 24px;
                margin: 20px;
                min-width: 200px;
            }
            
            QRadioButton {
                font-size: 14px;
                color: #333;
                padding: 8px;
            }
        """

    @staticmethod
    def get_history_page_style():
        return """
            QWidget#historyPage {
                background-color: white;
                padding: 20px;
            }
            
            QGroupBox {
                margin-bottom: 20px;
            }
            
            QDateTimeEdit {
                padding: 6px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                min-width: 180px;
            }
            
            QPushButton#searchButton {
                min-width: 100px;
            }
            
            QTableWidget {
                margin: 10px 0;
            }
            
            QPushButton#deleteButton {
                background-color: #ff4d4f;
            }
            
            QPushButton#deleteButton:hover {
                background-color: #ff7875;
            }
            
            QPushButton#previewButton {
                background-color: #52c41a;
            }
            
            QPushButton#previewButton:hover {
                background-color: #73d13d;
            }
            
            QLabel#previewLabel {
                border: 2px solid #e4e6e9;
                border-radius: 4px;
                padding: 2px;
                background-color: #fafafa;
            }
        """
    
    @staticmethod
    def get_detection_page_style():
        return """
            QWidget#detectionPage {
                background-color: white;
                padding: 20px;
            }
            
            QLabel#videoLabel {
                border: 2px solid #1890ff;
                border-radius: 8px;
                padding: 2px;
                background-color: black;
            }
            
            QGroupBox {
                margin-bottom: 15px;
            }
            
            QPushButton#backButton {
                background-color: #faad14;
            }
            
            QPushButton#backButton:hover {
                background-color: #ffc53d;
            }
            
            QLabel[status="normal"] {
                color: #52c41a;
                font-weight: bold;
            }
            
            QLabel[status="warning"] {
                color: #ff4d4f;
                font-weight: bold;
            }
            
            QLabel#fpsLabel {
                font-family: monospace;
                font-size: 14px;
            }
        """

class StartPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("startPage")
        self.init_ui()
        self.setStyleSheet(StyleSheet.get_start_page_style())
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # 添加标题
        title_label = QLabel("人车检测系统")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建一个居中的容器
        center_container = QFrame()
        center_container.setMaximumWidth(600)
        center_layout = QVBoxLayout(center_container)
        
        # 选择检测源
        source_group = QGroupBox("选择检测源")
        source_layout = QVBoxLayout()
        
        self.camera_radio = QRadioButton("使用摄像头")
        self.camera_radio.setChecked(True)
        self.video_radio = QRadioButton("导入视频文件")
        
        self.camera_settings = QWidget()
        camera_layout = QHBoxLayout(self.camera_settings)
        camera_layout.addWidget(QLabel("摄像头索引:"))
        self.camera_spinbox = QSpinBox()
        self.camera_spinbox.setValue(0)
        camera_layout.addWidget(self.camera_spinbox)
        camera_layout.addStretch()
        
        self.video_settings = QWidget()
        video_layout = QHBoxLayout(self.video_settings)
        self.video_path_label = QLabel("未选择视频文件")
        video_layout.addWidget(self.video_path_label)
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_video)
        video_layout.addWidget(self.browse_button)
        self.video_settings.setVisible(False)
        
        source_layout.addWidget(self.camera_radio)
        source_layout.addWidget(self.camera_settings)
        source_layout.addWidget(self.video_radio)
        source_layout.addWidget(self.video_settings)
        source_group.setLayout(source_layout)
        center_layout.addWidget(source_group)
        
        # 连接单选按钮切换事件
        self.camera_radio.toggled.connect(self.toggle_source_settings)
        
        # 开始按钮
        self.start_button = QPushButton("开始检测")
        self.start_button.setObjectName("startButton")
        center_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(center_container, alignment=Qt.AlignCenter)
        
    def toggle_source_settings(self, checked):
        self.camera_settings.setVisible(checked)
        self.video_settings.setVisible(not checked)
        
    def browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov);;所有文件 (*)")
        if file_path:
            self.video_path_label.setText(os.path.basename(file_path))
            self.video_path_label.setToolTip(file_path)
            
    def get_selected_source(self):
        if self.camera_radio.isChecked():
            return {"type": "camera", "index": self.camera_spinbox.value()}
        else:
            video_path = self.video_path_label.toolTip()
            if not video_path or video_path == "未选择视频文件":
                return None
            return {"type": "video", "path": video_path}

class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyPage")
        self.db_conn = mysql.connector.connect(**DB_CONFIG)
        self.db_cursor = self.db_conn.cursor()
        self.init_ui()
        self.load_sessions()
        self.setStyleSheet(StyleSheet.get_history_page_style())
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 搜索区域
        search_group = QGroupBox("搜索条件")
        search_layout = QHBoxLayout()
        
        # 时间范围选择
        self.start_time = QDateTimeEdit()
        self.start_time.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.end_time = QDateTimeEdit()
        self.end_time.setDateTime(QDateTime.currentDateTime())
        
        search_layout.addWidget(QLabel("开始时间:"))
        search_layout.addWidget(self.start_time)
        search_layout.addWidget(QLabel("结束时间:"))
        search_layout.addWidget(self.end_time)
        
        # 搜索按钮
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_sessions)
        search_layout.addWidget(self.search_button)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # 会话列表
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels([
            "会话ID", "开始时间", "结束时间", "来源类型", "总帧数", "操作"
        ])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sessions_table.itemClicked.connect(self.on_session_clicked)
        main_layout.addWidget(self.sessions_table)
        
        # 记录详情区域
        details_group = QGroupBox("检测记录详情")
        details_layout = QVBoxLayout()
        
        # 记录列表
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels([
            "记录ID", "帧号", "检测人数", "检测车辆", "警报状态", "预览"
        ])
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        details_layout.addWidget(self.records_table)
        
        # 图片预览区域
        preview_layout = QHBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setObjectName("previewLabel")
        preview_layout.addWidget(self.preview_label)
        details_layout.addLayout(preview_layout)
        
        details_group.setLayout(details_layout)
        main_layout.addWidget(details_group)
        
        # 设置搜索按钮样式
        self.search_button.setObjectName("searchButton")
        
    def load_sessions(self):
        try:
            query = """
                SELECT session_id, start_time, end_time, source_type, 
                       total_frames, save_dir
                FROM detection_sessions
                ORDER BY start_time DESC
            """
            self.db_cursor.execute(query)
            sessions = self.db_cursor.fetchall()
            
            self.sessions_table.setRowCount(len(sessions))
            for i, session in enumerate(sessions):
                for j, value in enumerate(session[:-1]):  # 不显示save_dir
                    self.sessions_table.setItem(i, j, QTableWidgetItem(str(value)))
                
                # 添加操作按钮
                delete_btn = QPushButton("删除")
                delete_btn.clicked.connect(lambda checked, sid=session[0]: self.delete_session(sid))
                delete_btn.setObjectName("deleteButton")
                self.sessions_table.setCellWidget(i, 5, delete_btn)
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "错误", f"加载会话记录失败: {err}")
            
    def search_sessions(self):
        try:
            query = """
                SELECT session_id, start_time, end_time, source_type, 
                       total_frames, save_dir
                FROM detection_sessions
                WHERE start_time BETWEEN %s AND %s
                ORDER BY start_time DESC
            """
            self.db_cursor.execute(query, (
                self.start_time.dateTime().toPyDateTime(),
                self.end_time.dateTime().toPyDateTime()
            ))
            sessions = self.db_cursor.fetchall()
            
            self.sessions_table.setRowCount(len(sessions))
            for i, session in enumerate(sessions):
                for j, value in enumerate(session[:-1]):
                    self.sessions_table.setItem(i, j, QTableWidgetItem(str(value)))
                
                delete_btn = QPushButton("删除")
                delete_btn.clicked.connect(lambda checked, sid=session[0]: self.delete_session(sid))
                self.sessions_table.setCellWidget(i, 5, delete_btn)
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "错误", f"搜索会话记录失败: {err}")
            
    def delete_session(self, session_id):
        reply = QMessageBox.question(self, "确认删除", 
                                   "确定要删除这个会话记录吗？这将同时删除所有相关的检测记录和图片。",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # 获取会话目录
                self.db_cursor.execute(
                    "SELECT save_dir FROM detection_sessions WHERE session_id = %s",
                    (session_id,)
                )
                save_dir = self.db_cursor.fetchone()[0]
                
                # 删除数据库记录
                self.db_cursor.execute("""
                    DELETE FROM person_detections 
                    WHERE record_id IN (
                        SELECT record_id FROM detection_records 
                        WHERE session_id = %s
                    )
                """, (session_id,))
                
                self.db_cursor.execute("""
                    DELETE FROM car_detections 
                    WHERE record_id IN (
                        SELECT record_id FROM detection_records 
                        WHERE session_id = %s
                    )
                """, (session_id,))
                
                self.db_cursor.execute(
                    "DELETE FROM detection_records WHERE session_id = %s",
                    (session_id,)
                )
                
                self.db_cursor.execute(
                    "DELETE FROM detection_sessions WHERE session_id = %s",
                    (session_id,)
                )
                
                self.db_conn.commit()
                
                # 删除图片文件夹
                if os.path.exists(save_dir):
                    import shutil
                    shutil.rmtree(save_dir)
                
                # 刷新会话列表
                self.load_sessions()
                
                QMessageBox.information(self, "成功", "会话记录已删除")
                
            except (mysql.connector.Error, OSError) as err:
                QMessageBox.critical(self, "错误", f"删除会话记录失败: {err}")
                
    def on_session_clicked(self, item):
        if item.column() != 0:  # 只在点击会话ID列时响应
            return
            
        session_id = int(item.text())
        try:
            # 加载该会话的所有检测记录
            query = """
                SELECT record_id, frame_number, person_count, car_count,
                       alarm_triggered, frame_image_path
                FROM detection_records
                WHERE session_id = %s
                ORDER BY frame_number
            """
            self.db_cursor.execute(query, (session_id,))
            records = self.db_cursor.fetchall()
            
            self.records_table.setRowCount(len(records))
            for i, record in enumerate(records):
                for j, value in enumerate(record[:-1]):  # 不显示图片路径
                    if j == 4:  # alarm_triggered 列
                        value = "已触发" if value else "正常"
                    self.records_table.setItem(i, j, QTableWidgetItem(str(value)))
                
                # 添加预览按钮
                if record[5]:  # 如果有图片路径
                    preview_btn = QPushButton("预览")
                    preview_btn.setObjectName("previewButton")
                    preview_btn.clicked.connect(
                        lambda checked, path=record[5], rid=record[0]: 
                        self.preview_record(path, rid)
                    )
                    self.records_table.setCellWidget(i, 5, preview_btn)
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "错误", f"加载检测记录失败: {err}")
            
    def preview_record(self, frame_path, record_id):
        try:
            # 显示帧图片
            if os.path.exists(frame_path):
                frame = cv2.imread(frame_path)
                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                        self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
            
            # 创建预览窗口显示该记录中检测到的所有人
            preview_window = QWidget()
            preview_window.setWindowTitle("检测目标预览")
            preview_layout = QVBoxLayout(preview_window)
            
            # 获取该记录的所有人物检测
            query = """
                SELECT image_path, confidence
                FROM person_detections
                WHERE record_id = %s
            """
            self.db_cursor.execute(query, (record_id,))
            person_detections = self.db_cursor.fetchall()
            
            for path, conf in person_detections:
                if os.path.exists(path):
                    img = cv2.imread(path)
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        h, w, ch = img.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qt_image)
                        
                        # 创建图片标签和置信度标签
                        img_label = QLabel()
                        img_label.setPixmap(pixmap.scaled(
                            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        conf_label = QLabel(f"置信度: {conf:.2f}")
                        
                        # 添加到布局
                        item_layout = QHBoxLayout()
                        item_layout.addWidget(img_label)
                        item_layout.addWidget(conf_label)
                        preview_layout.addLayout(item_layout)
            
            preview_window.show()
            
        except (mysql.connector.Error, cv2.error) as err:
            QMessageBox.critical(self, "错误", f"预览图片失败: {err}")

class PersonCarDetectorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('人车检测系统')
        self.setMinimumSize(1200, 800)  # 增加最小尺寸
        
        # 设置应用样式
        self.setStyleSheet(StyleSheet.get_main_style())
        
        # 初始化堆栈式页面
        self.stacked_widget = QTabWidget()
        self.stacked_widget.setTabPosition(QTabWidget.South)
        self.stacked_widget.setTabBarAutoHide(False)  # 显示标签栏
        self.setCentralWidget(self.stacked_widget)
        
        # 创建启动页面
        self.start_page = StartPage()
        self.stacked_widget.addTab(self.start_page, "选择")
        self.start_page.start_button.clicked.connect(self.start_detection)
        
        # 创建检测页面
        self.detection_widget = QWidget()
        self.stacked_widget.addTab(self.detection_widget, "检测")
        
        # 创建历史记录页面
        self.history_page = HistoryPage()
        self.stacked_widget.addTab(self.history_page, "历史记录")
        
        # 初始化变量
        self.model = None
        self.cap = None
        self.video_source = None
        self.is_detecting = False
        self.alarm_active = False
        self.last_alarm_time = 0
        self.alarm_cooldown = 5
        self.skip_frames = 0
        self.process_every_n_frames = 2
        self.frame_buffer = None
        
        # 启用GPU加速（如果可用）
        self.use_gpu = True
        
        # 初始化pygame
        pygame.mixer.init()
        pygame.mixer.music.load("alarm.mp3")

        # 添加IoU阈值设置
        self.iou_threshold = 0.5
        
        # 创建检测页面布局
        self.create_detection_layout()
        
        # 创建定时器用于更新画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # 数据库相关变量
        self.db_conn = None
        self.db_cursor = None
        self.current_session_id = None
        self.frame_count = 0
        self.connect_database()
        
        # 图片存储相关
        self.base_save_dir = "detection_images"
        self.session_dir = None
        
    def connect_database(self):
        try:
            self.db_conn = mysql.connector.connect(**DB_CONFIG)
            self.db_cursor = self.db_conn.cursor()
            print("数据库连接成功！")
        except mysql.connector.Error as err:
            print(f"数据库连接失败: {err}")
            
    def start_detection_session(self):
        if not self.db_conn or not self.db_cursor:
            return
            
        try:
            # 创建会话目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_dir = os.path.join(self.base_save_dir, f"session_{timestamp}")
            os.makedirs(self.session_dir)
            os.makedirs(os.path.join(self.session_dir, "frames"))
            os.makedirs(os.path.join(self.session_dir, "persons"))
            os.makedirs(os.path.join(self.session_dir, "cars"))
            
            source_type = self.video_source["type"]
            source_info = str(self.video_source["index"] if source_type == "camera" else self.video_source["path"])
            
            query = """
                INSERT INTO detection_sessions 
                (source_type, source_info, save_dir)
                VALUES (%s, %s, %s)
            """
            self.db_cursor.execute(query, (source_type, source_info, self.session_dir))
            self.db_conn.commit()
            self.current_session_id = self.db_cursor.lastrowid
            self.frame_count = 0
            
        except (mysql.connector.Error, OSError) as err:
            print(f"创建检测会话失败: {err}")
            
    def end_detection_session(self):
        if not self.db_conn or not self.db_cursor or not self.current_session_id:
            return
            
        try:
            query = """
                UPDATE detection_sessions 
                SET end_time = NOW(),
                    total_frames = %s
                WHERE session_id = %s
            """
            self.db_cursor.execute(query, (self.frame_count, self.current_session_id))
            self.db_conn.commit()
            self.current_session_id = None
            
        except mysql.connector.Error as err:
            print(f"结束检测会话失败: {err}")
            
    def save_detection_record(self, frame, results, person_count, car_count, alarm_triggered):
        if not self.db_conn or not self.db_cursor or not self.current_session_id:
            return
            
        try:
            # 保存当前帧
            frame_path = None
            if self.save_frames_checkbox.isChecked():
                frame_filename = f"frame_{self.frame_count}.jpg"
                frame_path = os.path.join(self.session_dir, "frames", frame_filename)
                cv2.imwrite(frame_path, frame)
            
            # 插入检测记录
            record_query = """
                INSERT INTO detection_records 
                (session_id, frame_number, person_count, car_count, alarm_triggered, frame_image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            record_values = (self.current_session_id, self.frame_count, 
                           person_count, car_count, alarm_triggered, frame_path)
            self.db_cursor.execute(record_query, record_values)
            record_id = self.db_cursor.lastrowid
            
            # 保存检测目标
            save_conf_threshold = self.save_conf_spinbox.value()
            
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # 检查置信度是否达到保存阈值
                    if conf < save_conf_threshold:
                        continue
                        
                    xyxy = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = map(int, xyxy)
                    
                    # 裁剪目标图像
                    target_img = frame[y1:y2, x1:x2]
                    if target_img.size == 0:
                        continue
                    
                    target_path = None
                    if cls == 0 and self.save_persons_checkbox.isChecked():  # 人
                        target_dir = "persons"
                        query = """
                            INSERT INTO person_detections 
                            (record_id, confidence, x_min, y_min, x_max, y_max, image_path)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        # 保存目标图像
                        target_filename = f"person_{self.frame_count}_{int(conf*100)}.jpg"
                        target_path = os.path.join(self.session_dir, target_dir, target_filename)
                        cv2.imwrite(target_path, target_img)
                        
                    elif cls == 2 and self.save_cars_checkbox.isChecked():  # 车
                        target_dir = "cars"
                        query = """
                            INSERT INTO car_detections 
                            (record_id, confidence, x_min, y_min, x_max, y_max, image_path)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        # 保存目标图像
                        target_filename = f"car_{self.frame_count}_{int(conf*100)}.jpg"
                        target_path = os.path.join(self.session_dir, target_dir, target_filename)
                        cv2.imwrite(target_path, target_img)
                    else:
                        continue
                    
                    if target_path:
                        values = (record_id, conf, x1, y1, x2, y2, target_path)
                        self.db_cursor.execute(query, values)
            
            self.db_conn.commit()
            
        except (mysql.connector.Error, cv2.error, OSError) as err:
            print(f"保存检测记录失败: {err}")
        
    def start_detection(self):
        source = self.start_page.get_selected_source()
        if not source:
            return
        
        # 初始化模型
        if not self.model:
            self.model = YOLO("yolov8n.pt")
        
        self.video_source = source
        self.stacked_widget.setCurrentIndex(1)
        
        # 适当处理返回按钮状态
        self.back_button.setEnabled(True)
        
        # 准备开始检测
        if self.is_detecting:
            self.stop_detection()
        
        # 显示准备就绪状态
        self.alarm_status_label.setText("状态: 准备就绪")
        
    def create_detection_layout(self):
        # 主布局
        self.detection_widget.setObjectName("detectionPage")
        main_layout = QHBoxLayout(self.detection_widget)
        
        # 左侧视频显示区域
        self.video_label = QLabel()
        self.video_label.setObjectName("videoLabel")
        self.video_label.setMinimumSize(800, 600)
        main_layout.addWidget(self.video_label)
        
        # 右侧控制面板
        control_panel = QVBoxLayout()
        
        # 返回按钮
        self.back_button = QPushButton("返回选择页")
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.go_back)
        control_panel.addWidget(self.back_button)
        
        # 参数设置组
        params_group = QGroupBox("参数设置")
        params_layout = QVBoxLayout()
        
        # 置信度阈值
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("置信度阈值:"))
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.1, 1.0)
        self.threshold_spinbox.setValue(0.5)
        self.threshold_spinbox.setSingleStep(0.1)
        threshold_layout.addWidget(self.threshold_spinbox)
        params_layout.addLayout(threshold_layout)
        
        # 人数阈值
        person_count_layout = QHBoxLayout()
        person_count_layout.addWidget(QLabel("警报人数阈值:"))
        self.person_count_spinbox = QSpinBox()
        self.person_count_spinbox.setRange(1, 10)
        self.person_count_spinbox.setValue(3)
        person_count_layout.addWidget(self.person_count_spinbox)
        params_layout.addLayout(person_count_layout)
        
        # 在参数设置组中添加IoU阈值设置
        iou_threshold_layout = QHBoxLayout()
        iou_threshold_layout.addWidget(QLabel("IoU阈值:"))
        self.iou_threshold_spinbox = QDoubleSpinBox()
        self.iou_threshold_spinbox.setRange(0.1, 1.0)
        self.iou_threshold_spinbox.setValue(0.5)
        self.iou_threshold_spinbox.setSingleStep(0.1)
        self.iou_threshold_spinbox.valueChanged.connect(self.update_iou_threshold)
        iou_threshold_layout.addWidget(self.iou_threshold_spinbox)
        params_layout.addLayout(iou_threshold_layout)
        
        params_group.setLayout(params_layout)
        control_panel.addWidget(params_group)
        
        # 性能设置组
        performance_group = QGroupBox("性能设置")
        performance_layout = QVBoxLayout()
        
        # 处理帧率
        process_rate_layout = QHBoxLayout()
        process_rate_layout.addWidget(QLabel("处理频率:"))
        self.process_rate_spinbox = QSpinBox()
        self.process_rate_spinbox.setRange(1, 10)
        self.process_rate_spinbox.setValue(2)
        self.process_rate_spinbox.setToolTip("每隔多少帧进行一次检测")
        process_rate_layout.addWidget(self.process_rate_spinbox)
        performance_layout.addLayout(process_rate_layout)
        
        # 分辨率选择
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("分辨率:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1980x1080","1280x720", "640x480", "320x240"])
        resolution_layout.addWidget(self.resolution_combo)
        performance_layout.addLayout(resolution_layout)
        
        # GPU加速选项
        gpu_layout = QHBoxLayout()
        self.gpu_checkbox = QCheckBox("启用GPU加速")
        self.gpu_checkbox.setChecked(self.use_gpu)
        self.gpu_checkbox.toggled.connect(self.toggle_gpu)
        gpu_layout.addWidget(self.gpu_checkbox)
        performance_layout.addLayout(gpu_layout)
        
        performance_group.setLayout(performance_layout)
        control_panel.addWidget(performance_group)
        
        # 添加图片保存设置组
        save_group = QGroupBox("图片保存设置")
        save_layout = QVBoxLayout()
        
        # 保存原始帧选项
        self.save_frames_checkbox = QCheckBox("保存原始视频帧")
        self.save_frames_checkbox.setChecked(True)
        save_layout.addWidget(self.save_frames_checkbox)
        
        # 保存检测目标选项
        self.save_persons_checkbox = QCheckBox("保存检测到的人")
        self.save_persons_checkbox.setChecked(True)
        save_layout.addWidget(self.save_persons_checkbox)
        
        self.save_cars_checkbox = QCheckBox("保存检测到的车辆")
        self.save_cars_checkbox.setChecked(True)
        save_layout.addWidget(self.save_cars_checkbox)
        
        # 保存置信度阈值
        save_conf_layout = QHBoxLayout()
        save_conf_layout.addWidget(QLabel("保存置信度阈值:"))
        self.save_conf_spinbox = QDoubleSpinBox()
        self.save_conf_spinbox.setRange(0.1, 1.0)
        self.save_conf_spinbox.setValue(0.5)
        self.save_conf_spinbox.setSingleStep(0.1)
        save_conf_layout.addWidget(self.save_conf_spinbox)
        save_layout.addLayout(save_conf_layout)
        
        save_group.setLayout(save_layout)
        control_panel.addWidget(save_group)
        
        # 状态显示组
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout()
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setObjectName("fpsLabel")
        self.person_count_label = QLabel("当前人数: 0")
        self.car_count_label = QLabel("当前车辆: 0")
        self.alarm_status_label = QLabel("警报状态: 未触发")
        self.alarm_status_label.setProperty("status", "normal")
        
        status_layout.addWidget(self.fps_label)
        status_layout.addWidget(self.person_count_label)
        status_layout.addWidget(self.car_count_label)
        status_layout.addWidget(self.alarm_status_label)
        
        status_group.setLayout(status_layout)
        control_panel.addWidget(status_group)
        
        # 控制按钮
        self.start_button = QPushButton("开始检测")
        self.start_button.clicked.connect(self.toggle_detection)
        control_panel.addWidget(self.start_button)
        
        main_layout.addLayout(control_panel)
        
        # 状态标签样式
        self.fps_label.setObjectName("fpsLabel")
        self.alarm_status_label.setProperty("status", "normal")
        
    def go_back(self):
        if self.is_detecting:
            self.stop_detection()
        self.stacked_widget.setCurrentIndex(0)
        
    def toggle_gpu(self, checked):
        self.use_gpu = checked
        # 重新加载模型以应用GPU设置
        if self.is_detecting:
            self.toggle_detection()  # 停止检测
            self.toggle_detection()  # 重新开始检测
    
    def toggle_detection(self):
        if not self.is_detecting:
            # 开始检测
            if self.video_source["type"] == "camera":
                self.cap = cv2.VideoCapture(self.video_source["index"])
            else:
                self.cap = cv2.VideoCapture(self.video_source["path"])
                
            if not self.cap.isOpened():
                self.alarm_status_label.setText("警报状态: 视频源打开失败")
                return
            
            # 只对摄像头设置分辨率
            if self.video_source["type"] == "camera":
                resolution = self.resolution_combo.currentText().split("x")
                width, height = int(resolution[0]), int(resolution[1])
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
                # 设置缓冲区大小为1，减少延迟
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # 更新处理频率
            self.process_every_n_frames = self.process_rate_spinbox.value()
            
            # 开始新的检测会话
            self.start_detection_session()
            
            self.is_detecting = True
            self.start_button.setText("停止检测")
            self.timer.start(10)  # 更高的刷新率，约100FPS
        else:
            # 结束检测会话
            self.end_detection_session()
            self.stop_detection()
    
    def stop_detection(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.is_detecting = False
        self.start_button.setText("开始检测")
        self.video_label.clear()
        self.session_dir = None
            
    def calculate_iou(self, box1, box2):
        """计算两个边界框的IoU"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # 计算交集区域
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
            
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        
        # 计算两个框的面积
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        # 计算并集面积
        union_area = box1_area + box2_area - intersection_area
        
        # 计算IoU
        iou = intersection_area / union_area if union_area > 0 else 0
        return iou
        
    def filter_duplicates(self, boxes, classes):
        """过滤重复的检测框"""
        filtered_boxes = []
        filtered_classes = []
        
        for i, (box, cls) in enumerate(zip(boxes, classes)):
            is_duplicate = False
            for prev_box in filtered_boxes:
                if self.calculate_iou(box, prev_box) > self.iou_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_boxes.append(box)
                filtered_classes.append(cls)
                
        return filtered_boxes, filtered_classes
        
    def update_frame(self):
        if not self.cap:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            if self.video_source["type"] == "video":
                self.end_detection_session()
                self.alarm_status_label.setText("警报状态: 视频播放完毕")
                self.stop_detection()
            return
        
        self.frame_count += 1
        
        # 存储最新帧
        self.frame_buffer = frame.copy()
        
        # 计算FPS
        current_time = time.time()
        if hasattr(self, 'prev_time'):
            fps = 1 / (current_time - self.prev_time)
            self.fps_label.setText(f"FPS: {int(fps)}")
        self.prev_time = current_time
        
        # 跳帧处理，提高性能
        self.skip_frames += 1
        if self.skip_frames < self.process_every_n_frames:
            if hasattr(self, 'last_annotated_frame'):
                self.display_frame(self.last_annotated_frame)
            return
        
        self.skip_frames = 0
        
        # 使用YOLOv8进行检测
        results = self.model(frame, classes=[0, 2], conf=self.threshold_spinbox.value())
        
        # 收集所有检测框和类别
        all_boxes = []
        all_classes = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                xyxy = box.xyxy[0].tolist()
                all_boxes.append(xyxy)
                all_classes.append(cls)
        
        # 过滤重复检测
        filtered_boxes, filtered_classes = self.filter_duplicates(all_boxes, all_classes)
        
        # 统计人和车的数量
        person_count = sum(1 for cls in filtered_classes if cls == 0)
        car_count = sum(1 for cls in filtered_classes if cls == 2)
        
        # 更新状态显示
        self.person_count_label.setText(f"当前人数: {person_count}")
        self.car_count_label.setText(f"当前车辆: {car_count}")
        
        # 检查是否需要触发警报
        alarm_triggered = False
        if person_count >= self.person_count_spinbox.value():
            if not self.alarm_active or (current_time - self.last_alarm_time) > self.alarm_cooldown:
                pygame.mixer.music.play()
                self.alarm_active = True
                self.last_alarm_time = current_time
                self.alarm_status_label.setProperty("status", "warning")
                self.alarm_status_label.setText("警报状态: ⚠️警报触发！")
                alarm_triggered = True
        else:
            self.alarm_active = False
            self.alarm_status_label.setProperty("status", "normal")
            self.alarm_status_label.setText("警报状态: 正常")
            
        # 保存检测记录到数据库
        self.save_detection_record(frame, results, person_count, car_count, alarm_triggered)
        
        # 显示检测结果
        annotated_frame = results[0].plot()
        self.last_annotated_frame = annotated_frame
        
        self.display_frame(annotated_frame)
    
    def display_frame(self, frame):
        # 转换图像格式并显示
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
        
    def closeEvent(self, event):
        # 程序关闭时清理资源
        if self.cap:
            self.cap.release()
        event.accept()

    def update_iou_threshold(self, value):
        self.iou_threshold = value

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PersonCarDetectorGUI()
    window.show()
    sys.exit(app.exec_()) 