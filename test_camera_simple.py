"""
Simple camera test using OpenCV VideoCapture (no picamera2)
"""

import cv2
import time

def test_camera_opencv():
    """Test camera using OpenCV's VideoCapture"""
    print("Testing camera with OpenCV VideoCapture...")
    
    try:
        # Open camera (try different indices if needed)
        cap = cv2.VideoCapture(0)  # 0 is usually the first camera
        
        if not cap.isOpened():
            print("ERROR: Could not open camera")
            return False
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("Camera opened successfully!")
        
        # Load face cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("ERROR: Could not load face cascade")
            return False
        
        print("Starting face detection (30 seconds)...\n")
        
        frame_count = 0
        face_count = 0
        start_time = time.time()
        test_duration = 30
        
        while time.time() - start_time < test_duration:
            ret, frame = cap.read()
            
            if not ret:
                print("ERROR: Failed to capture frame")
                continue
            
            frame_count += 1
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) > 0:
                face_count += 1
                largest = max(faces, key=lambda r: r[2]*r[3])
                x, y, w, h = largest
                
                # Calculate normalized position
                center_x = x + w/2
                center_y = y + h/2
                norm_x = (center_x - 320) / 320
                norm_y = (center_y - 240) / 240
                
                print(f"FACE! Position: X={norm_x:+.2f}, Y={norm_y:+.2f}, Size={w}x{h}px")
            
            # Progress update
            elapsed = time.time() - start_time
            if int(elapsed) % 5 == 0 and frame_count % 30 == 0:
                detection_rate = (face_count / frame_count * 100)
                print(f"[{int(elapsed)}s] Frames: {frame_count}, Detections: {face_count}, Rate: {detection_rate:.1f}%")
            
            time.sleep(0.033)  # ~30 FPS
        
        # Cleanup
        cap.release()
        
        # Results
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        detection_rate = (face_count / frame_count * 100)
        
        print(f"\n{'='*50}")
        print(f"TEST RESULTS:")
        print(f"{'='*50}")
        print(f"Duration: {elapsed:.1f}s")
        print(f"Total frames: {frame_count}")
        print(f"Frames with faces: {face_count}")
        print(f"Detection rate: {detection_rate:.1f}%")
        print(f"Average FPS: {fps:.1f}")
        print(f"{'='*50}\n")
        
        if detection_rate > 50:
            print("SUCCESS - Camera and face detection working!")
        else:
            print("Camera working but face detection needs improvement")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*50)
    print("OPENCV CAMERA TEST")
    print("="*50)
    print()
    test_camera_opencv()