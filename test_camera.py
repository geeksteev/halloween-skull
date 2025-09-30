"""
Simple camera and face detection test
"""

import cv2
import time
from picamera2 import Picamera2

def test_camera_basic():
    """Test basic camera functionality"""
    print("Testing camera initialization...")
    
    try:
        camera = Picamera2()
        config = camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        camera.configure(config)
        camera.start()
        
        print("Camera started successfully!")
        print("Warming up for 2 seconds...")
        time.sleep(2)
        
        # Capture a test frame
        print("Capturing test frame...")
        frame = camera.capture_array()
        print(f"Frame captured: {frame.shape}, dtype: {frame.dtype}")
        
        camera.stop()
        print("Camera test PASSED\n")
        return True
        
    except Exception as e:
        print(f"Camera test FAILED: {e}\n")
        return False

def test_face_detection():
    """Test face detection with live preview"""
    print("Testing face detection...")
    print("Press 'q' to quit\n")
    
    try:
        # Initialize camera
        camera = Picamera2()
        config = camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        camera.configure(config)
        camera.start()
        time.sleep(2)
        
        # Load face cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("ERROR: Could not load face cascade classifier")
            return False
        
        print("Face detection ready!")
        print("Stand in front of camera...\n")
        
        frame_count = 0
        face_count = 0
        start_time = time.time()
        
        while True:
            # Capture frame
            frame = camera.capture_array()
            frame_count += 1
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Calculate normalized position
                center_x = x + w/2
                center_y = y + h/2
                norm_x = (center_x - 320) / 320
                norm_y = (center_y - 240) / 240
                
                # Display position
                text = f"X:{norm_x:.2f} Y:{norm_y:.2f}"
                cv2.putText(frame, text, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display face count
            if len(faces) > 0:
                face_count += 1
                status = f"FACE DETECTED ({len(faces)})"
                color = (0, 255, 0)
            else:
                status = "NO FACE"
                color = (0, 0, 255)
            
            cv2.putText(frame, status, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Calculate FPS
            elapsed = time.time() - start_time
            if elapsed > 0:
                fps = frame_count / elapsed
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 460),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Face Detection Test', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        camera.stop()
        cv2.destroyAllWindows()
        
        # Results
        detection_rate = (face_count / frame_count * 100) if frame_count > 0 else 0
        print(f"\nTest Results:")
        print(f"Total frames: {frame_count}")
        print(f"Frames with faces: {face_count}")
        print(f"Detection rate: {detection_rate:.1f}%")
        print(f"Average FPS: {fps:.1f}")
        print("\nFace detection test PASSED\n")
        
        return True
        
    except Exception as e:
        print(f"Face detection test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*50)
    print("CAMERA & FACE DETECTION TEST")
    print("="*50)
    print()
    
    # Test 1: Basic camera
    if not test_camera_basic():
        print("Cannot proceed - camera not working")
        return
    
    # Test 2: Face detection with preview
    test_face_detection()
    
    print("Testing complete!")

if __name__ == "__main__":
    main()