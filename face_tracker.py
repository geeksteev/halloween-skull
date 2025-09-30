"""
Face tracking using OpenCV and camera
"""

import cv2
import numpy as np
import time
from picamera2 import Picamera2
from config import *

class FaceTracker:
    """Handles camera and face detection"""
    
    def __init__(self):
        # Initialize camera
        try:
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration(
                main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT), "format": "RGB888"}
            )
            self.camera.configure(config)
            self.camera.start()
            print("Camera initialized successfully")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            raise
        
        # Load face detection cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            raise RuntimeError("Failed to load face cascade classifier")
        
        # State
        self.last_face_position = None
        self.face_detected = False
        self.last_detection_time = 0
        self.frames_without_face = 0
        self.detection_confidence = 0
        
        # Performance tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Give camera time to warm up
        time.sleep(2)
        print("Face tracker initialized and ready")
    
    def detect_faces(self):
        """Capture frame and detect faces, return normalized position"""
        try:
            # Capture frame
            frame = self.camera.capture_array()
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=FACE_DETECTION_SCALE,
                minNeighbors=FACE_MIN_NEIGHBORS,
                minSize=(30, 30)
            )
            
            # Update FPS counter
            self.frame_count += 1
            elapsed = time.time() - self.fps_start_time
            if elapsed > 1.0:
                self.current_fps = self.frame_count / elapsed
                self.frame_count = 0
                self.fps_start_time = time.time()
                if DEBUG_MODE and SHOW_FPS:
                    print(f"Face detection FPS: {self.current_fps:.1f}")
            
            if len(faces) > 0:
                # Get largest face (closest person)
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                x, y, w, h = largest_face
                
                # Calculate center of face
                face_center_x = x + w / 2
                face_center_y = y + h / 2
                
                # Normalize to -1.0 to 1.0 range
                # X: -1.0 = far left, 0 = center, 1.0 = far right
                # Y: -1.0 = top, 0 = center, 1.0 = bottom
                normalized_x = (face_center_x - CAMERA_WIDTH / 2) / (CAMERA_WIDTH / 2)
                normalized_y = (face_center_y - CAMERA_HEIGHT / 2) / (CAMERA_HEIGHT / 2)
                
                # Clamp values to -1.0 to 1.0 range
                normalized_x = max(-1.0, min(1.0, normalized_x))
                normalized_y = max(-1.0, min(1.0, normalized_y))
                
                # Calculate detection confidence based on face size
                face_area = w * h
                max_area = CAMERA_WIDTH * CAMERA_HEIGHT
                self.detection_confidence = min(1.0, face_area / (max_area * 0.25))
                
                # Update state
                self.last_face_position = (normalized_x, normalized_y)
                self.face_detected = True
                self.last_detection_time = time.time()
                self.frames_without_face = 0
                
                if DEBUG_MODE:
                    print(f"Face detected at: ({normalized_x:.2f}, {normalized_y:.2f}), "
                          f"confidence: {self.detection_confidence:.2f}")
                
                return self.last_face_position
            else:
                # No face detected
                self.frames_without_face += 1
                
                # Keep last position briefly for smooth tracking
                if self.frames_without_face < 30:  # ~1 second at 30fps
                    return self.last_face_position
                else:
                    self.face_detected = False
                    self.detection_confidence = 0
                    return None
                    
        except Exception as e:
            print(f"Error during face detection: {e}")
            return None
    
    def get_face_position(self):
        """Get last detected face position"""
        return self.last_face_position if self.face_detected else None
    
    def is_face_detected(self):
        """Check if face is currently detected"""
        return self.face_detected
    
    def get_detection_confidence(self):
        """Get confidence level of current detection (0.0 to 1.0)"""
        return self.detection_confidence
    
    def get_time_since_detection(self):
        """Get seconds since last face detection"""
        if self.last_detection_time == 0:
            return float('inf')
        return time.time() - self.last_detection_time
    
    def cleanup(self):
        """Stop camera and cleanup resources"""
        try:
            self.camera.stop()
            print("Face tracker stopped cleanly")
        except Exception as e:
            print(f"Error stopping camera: {e}")