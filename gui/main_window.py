import os
import asyncio
import cv2
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QImage, QPixmap

from database.async_database import AsyncDatabase
from recognition.face_detector import FaceRecognition
from recognition.system import FaceRecognitionSystem
from utils.video_thread import VideoThread


class AttendanceSystemGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition Attendance System")
        self.setFixedSize(1200, 800)

        # Create needed folders
        os.makedirs("data/Capture_Images", exist_ok=True)
        os.makedirs("resources", exist_ok=True)

        # Initialize variables
        self.video_thread = None
        self.face_recognition_system = None
        self.db = None
        self.timer = None
        self.is_running = False

        # Initialize UI
        self.init_ui()

        # Connect buttons
        self.start_button.clicked.connect(self.start_recognition)
        self.stop_button.clicked.connect(self.stop_recognition)

        # Disable stop button initially
        self.stop_button.setEnabled(False)

        # Reset UI
        self.reset_ui()

    def init_ui(self):
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)

        # Video feed
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 4px solid #6c5ce7;
                border-radius: 10px;
                background-color: #f5f6fa;
            }
        """)
        left_layout.addWidget(self.video_label)

        # Control buttons
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Recognition")
        self.stop_button = QPushButton("Stop")

        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border-radius: 15px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5b4cc7;
            }
        """)

        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #ff7675;
                color: white;
                border-radius: 15px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e56867;
            }
        """)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        left_layout.addLayout(control_layout)

        # Status label
        self.status_label_main = QLabel("System Status: Ready")
        self.status_label_main.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2d3436;
                padding: 5px;
                font-weight: bold;
            }
        """)
        left_layout.addWidget(self.status_label_main)

        # Right Panel
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #f5f6fa;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)

        # Employee photo
        self.employee_photo = QLabel()
        self.employee_photo.setFixedSize(216, 216)
        self.employee_photo.setStyleSheet("""
            QLabel {
                border: 2px solid #6c5ce7;
                border-radius: 10px;
                background-color: white;
            }
        """)
        self.employee_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.employee_photo)

        # Employee details
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        details_layout = QVBoxLayout(details_frame)

        # Create labels with consistent styling
        self.name_label = QLabel("Name: ")
        self.id_label = QLabel("ID: ")
        self.major_label = QLabel("Major: ")
        self.attendance_label = QLabel("Total Attendance: ")
        self.status_label = QLabel("Status: ")

        for label in [self.name_label, self.id_label, self.major_label,
                      self.attendance_label, self.status_label]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #2d3436;
                    padding: 5px;
                    font-weight: bold;
                }
            """)
            details_layout.addWidget(label)

        right_layout.addWidget(details_frame)

        # Status indicators
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(10)

        self.marked_indicator = QPushButton("MARKED")
        self.already_marked_indicator = QPushButton("ALREADY MARKED")
        self.active_indicator = QPushButton("ACTIVE")

        for button in [self.marked_indicator, self.already_marked_indicator, self.active_indicator]:
            button.setEnabled(False)
            button.setFixedHeight(40)
            button.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    font-weight: bold;
                    color: #2d3436;
                    background-color: #dfe6e9;
                }
            """)
            status_layout.addWidget(button)

        right_layout.addWidget(status_frame)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 60)
        main_layout.addWidget(right_panel, 40)

    def reset_ui(self):
        # Reset all UI elements
        self.name_label.setText("Name: ")
        self.id_label.setText("ID: ")
        self.major_label.setText("Major: ")
        self.attendance_label.setText("Total Attendance: ")
        self.status_label.setText("Status: ")

        # Reset employee photo
        placeholder = QPixmap(216, 216)
        placeholder.fill(Qt.GlobalColor.white)
        self.employee_photo.setPixmap(placeholder)

        # Reset indicators
        self.reset_indicators()

    def reset_indicators(self):
        for button in [self.marked_indicator, self.already_marked_indicator, self.active_indicator]:
            button.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    font-weight: bold;
                    color: #2d3436;
                    background-color: #dfe6e9;
                }
            """)

    async def start_recognition_async(self):
        self.status_label_main.setText("System Status: Initializing...")

        # Initialize database
        self.db = AsyncDatabase()
        db_success = await self.db.init_pool()

        if not db_success:
            self.status_label_main.setText("System Status: Database Connection Failed")
            self.start_button.setEnabled(True)
            return

        # Initialize face recognition system
        face_detector = FaceRecognition("EncodedImages.pickle")
        self.face_recognition_system = FaceRecognitionSystem(self.db, face_detector, "EncodedImages.pickle")
        self.face_recognition_system.face_detected_signal.connect(self.update_employee_info)
        self.face_recognition_system.status_signal.connect(self.update_status)
        self.face_recognition_system.processed_frame_signal.connect(self.update_processed_frame)

        # Start video thread
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_video_feed)
        self.video_thread.error_signal.connect(self.update_status)
        self.video_thread.start()

        # Start periodic processing
        self.timer = asyncio.create_task(self.process_frames_periodically())

        # Update UI
        self.status_label_main.setText("System Status: Running")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.is_running = True

        # Update active indicator
        self.active_indicator.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                font-weight: bold;
                color: white;
                background-color: #00b894;
            }
        """)

    def start_recognition(self):
        asyncio.create_task(self.start_recognition_async())

    async def process_frames_periodically(self):
        try:
            while self.is_running:
                if self.face_recognition_system:
                    await self.face_recognition_system.process_frame()
                await asyncio.sleep(0.1)  # Process at 10 FPS
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.update_status(f"Processing error: {str(e)}")

    async def stop_recognition_async(self):
        self.is_running = False

        # Cancel processing timer
        if self.timer:
            self.timer.cancel()
            self.timer = None

        # Stop video thread
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread = None

        # Close database connection
        if self.db:
            await self.db.close()
            self.db = None

        # Clean up face recognition system
        self.face_recognition_system = None

        # Update UI
        self.reset_ui()
        self.status_label_main.setText("System Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def stop_recognition(self):
        asyncio.create_task(self.stop_recognition_async())

    def update_video_feed(self, frame):
        if self.face_recognition_system:
            self.face_recognition_system.set_frame(frame)

    def update_processed_frame(self, frame):
        # Convert frame to QPixmap and display
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(convert_to_qt_format)
        self.video_label.setPixmap(pixmap)

    def update_employee_info(self, info):
        # Update employee information
        self.name_label.setText(f"Name: {info['name']}")
        self.id_label.setText(f"ID: {info['employee_id']}")
        self.major_label.setText(f"Major: {info['major']}")
        self.attendance_label.setText(f"Total Attendance: {info['total_attendance']}")
        self.status_label.setText(f"Status: {info['status']}")

        # Update employee photo
        if info['face_img'] is not None:
            face_img = cv2.cvtColor(info['face_img'], cv2.COLOR_BGR2RGB)
            h, w, ch = face_img.shape
            bytes_per_line = ch * w

            # Resize if needed
            if h > 0 and w > 0:  # Make sure dimensions are valid
                face_img = cv2.resize(face_img, (216, 216))
                h, w, ch = face_img.shape
                bytes_per_line = ch * w

                img = QImage(face_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                self.employee_photo.setPixmap(pixmap)

        # Update status indicators
        self.reset_indicators()

        if info['status'] == "MARKED":
            self.marked_indicator.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    font-weight: bold;
                    color: white;
                    background-color: #00b894;
                }
            """)
        elif info['status'] == "ALREADY MARKED":
            self.already_marked_indicator.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    font-weight: bold;
                    color: white;
                    background-color: #fdcb6e;
                }
            """)

    def update_status(self, status_text):
        self.status_label_main.setText(f"System Status: {status_text}")

    async def closeEvent_async(self, event):
        # Clean up when closing
        await self.stop_recognition_async()
        event.accept()

    def closeEvent(self, event):
        if self.is_running:
            # Create a task but we need to make sure it completes
            loop = asyncio.get_event_loop()
            loop.create_task(self.closeEvent_async(event))
            # Don't accept the event yet; let the async task do it
            event.ignore()
        else:
            event.accept()