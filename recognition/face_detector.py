import os
import pickle
import cv2
import face_recognition
import numpy as np


class FaceRecognition:
    def __init__(self, encoded_image_path):
        if os.path.exists(encoded_image_path):
            with open(encoded_image_path, "rb") as file:
                self.encodeListKnownWithIds = pickle.load(file)
                self.encodeListKnown, self.employeeIds = self.encodeListKnownWithIds
        else:
            self.encodeListKnown = []
            self.employeeIds = []
            print(f"Warning: Encoded image file not found: {encoded_image_path}")

    def recognize_faces(self, frame):
        imgSmall = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)
        faceCurFrame = face_recognition.face_locations(imgSmall)

        # Return empty lists if no faces are detected
        if not faceCurFrame:
            return [], []

        try:
            encodeCurFace = face_recognition.face_encodings(imgSmall, faceCurFrame)
            faceCurFrame = [(int(top), int(right), int(bottom), int(left)) for (top, right, bottom, left) in faceCurFrame]
            return faceCurFrame, encodeCurFace
        except Exception as e:
            print(f"Error in face encoding: {str(e)}")
            return [], []

    def match_faces(self, encodeFace):
        if not self.encodeListKnown:
            return [], 0

        matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)

        if len(faceDis) > 0:
            matchIndex = np.argmin(faceDis)
            return matches, matchIndex
        return [], 0