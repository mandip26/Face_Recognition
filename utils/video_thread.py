import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.width = 640
        self.height = 480

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.error_signal.emit("Error: Unable to open camera")
                return

            cap.set(3, self.width)
            cap.set(4, self.height)

            while self.running:
                ret, frame = cap.read()
                if ret:
                    self.change_pixmap_signal.emit(frame)
                else:
                    self.error_signal.emit("Error: Failed to capture frame")
                    break

                self.msleep(30)  # Limit to about 30 FPS

            cap.release()
        except Exception as e:
            self.error_signal.emit(f"Camera error: {str(e)}")

    def stop(self):
        self.running = False
        self.wait()