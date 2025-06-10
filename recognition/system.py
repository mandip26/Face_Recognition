import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal


class FaceRecognitionSystem(QObject):
    face_detected_signal = pyqtSignal(dict)
    status_signal = pyqtSignal(str)
    processed_frame_signal = pyqtSignal(np.ndarray)

    def __init__(self, db, face_recognition, encoded_image_path):
        super().__init__()
        self.db = db
        self.face_recognition = face_recognition
        self.current_frame = None
        self.processing = False
        self.counter = 0
        self.id = -1
        self.last_detection_time = datetime.now()
        self.last_processed_id = None
        # Create needed folder for captured images
        os.makedirs("data/Capture_Images", exist_ok=True)
        self.image_saved = False

    def set_frame(self, frame):
        self.current_frame = frame.copy()

    async def process_frame(self):
        if self.current_frame is None or self.processing:
            return

        self.processing = True

        try:
            frame = self.current_frame.copy()
            frame_with_rect = frame.copy()

            # Detect faces
            faceCurFrame, encodeCurFace = self.face_recognition.recognize_faces(frame)

            if faceCurFrame:
                for encodeFace, facLoc in zip(encodeCurFace, faceCurFrame):
                    if len(self.face_recognition.encodeListKnown) == 0:
                        self.status_signal.emit("No encoded faces available")
                        continue

                    matches, matchIndex = self.face_recognition.match_faces(encodeFace)

                    if matches and matches[matchIndex]:
                        # Draw rectangle around face
                        y1, x2, y2, x1 = facLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(frame_with_rect, (x1, y1), (x2, y2), (0, 255, 0), 2)

                        # Process matched face
                        employee_id = self.face_recognition.employeeIds[matchIndex]

                        # Check time since last detection to avoid processing too frequently
                        time_diff = (datetime.now() - self.last_detection_time).total_seconds()

                        if employee_id != self.last_processed_id or time_diff > 3:
                            self.id = employee_id
                            self.last_processed_id = employee_id
                            self.last_detection_time = datetime.now()

                            face_img = await self.save_and_display_face(frame, employee_id)

                            # Process employee info
                            await self.process_employee(self.id, face_img)

            # Emit processed frame
            self.processed_frame_signal.emit(frame_with_rect)

        except Exception as e:
            self.status_signal.emit(f"Processing error: {str(e)}")

        finally:
            self.processing = False

    async def save_and_display_face(self, frame, employee_id):
        folderPath = 'data/Capture_Images'
        face_filename = os.path.join(folderPath, f'{employee_id}.jpg')

        # Save the image if it hasn't been saved yet
        if not self.image_saved:
            cv2.imwrite(face_filename, frame)
            self.image_saved = True
            self.status_signal.emit(f"Face image saved for employee {employee_id}")

        # Read the saved image
        captured_face = cv2.imread(face_filename)

        if captured_face is not None:
            # Resize to match the employee photo size in the UI
            captured_face_resized = cv2.resize(captured_face, (216, 216))
            return captured_face_resized
        else:
            self.status_signal.emit(f"Error: Could not read saved face image for employee {employee_id}")
            return frame

    async def process_employee(self, employee_id, face_img):
        try:
            # Get employee info
            employeeInfo = await self.db.get_employee_info(employee_id)

            if employeeInfo:
                # Check attendance status
                status = await self.check_attendance(employeeInfo)

                # Create result dictionary
                result = {
                    'employee_id': employee_id,
                    'name': employeeInfo['name'],
                    'major': employeeInfo['major'],
                    'total_attendance': employeeInfo['total_attendance'],
                    'face_img': face_img,
                    'status': status
                }

                # Emit signal with employee info
                self.face_detected_signal.emit(result)
            else:
                self.status_signal.emit(f"Employee ID {employee_id} not found")

        except Exception as e:
            self.status_signal.emit(f"Database error: {str(e)}")

    async def check_attendance(self, employeeInfo):
        try:
            last_attendance_time = employeeInfo["last_attendance_time"]

            # Handle different types of datetime objects
            if isinstance(last_attendance_time, datetime):
                datetimeObject = last_attendance_time
            else:
                # Try different formats if needed
                try:
                    datetimeObject = datetime.strptime(str(last_attendance_time), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # In case of different format from database
                    try:
                        datetimeObject = datetime.strptime(str(last_attendance_time), "%Y-%m-%d")
                    except ValueError:
                        # If all parsing fails, use current time and log the error
                        self.status_signal.emit(f"Error parsing date: {last_attendance_time}")
                        datetimeObject = datetime.now()  # Set to current time as a fallback

            # Calculate time difference
            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

            if secondsElapsed > 30:  # Allow marking attendance after 30 seconds
                # Update attendance count
                employeeInfo["total_attendance"] += 1
                await self.db.update_employee_attendance(self.id, employeeInfo["total_attendance"])
                await self.db.update_employee_last_attendance_time(self.id, datetime.now())
                self.image_saved = False  # Reset the image saved flag to allow saving a new image next time
                return "MARKED"
            else:
                return "ALREADY MARKED"
        except Exception as e:
            self.status_signal.emit(f"Error processing attendance: {str(e)}")
            return "ERROR"