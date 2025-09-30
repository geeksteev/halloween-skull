"""
Main program for three-eyed skull Halloween decoration
Integrates face tracking, eye animation, audio, and LEDs
"""

import time
import signal
import sys
from config import *
from display_manager import DisplayManager
from eye_controller import EyeController
from face_tracker import FaceTracker
from audio_manager import AudioManager
from led_controller import LEDController, LEDPattern

class SkullController:
    """Main controller for the skull decoration"""
    
    def __init__(self):
        print("Initializing Three-Eyed Skull...")
        
        # Initialize all subsystems
        self.display_manager = None
        self.eye_controller = None
        self.face_tracker = None
        self.audio_manager = None
        self.led_controller = None
        
        # State management
        self.current_mode = DEFAULT_MODE
        self.last_activity_time = time.time()
        self.last_mode_check = time.time()
        self.face_was_detected = False
        self.last_ambient_sound = time.time()
        
        # Performance tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.initialize_systems()
    
    def initialize_systems(self):
        """Initialize all hardware and software subsystems"""
        try:
            # Initialize displays
            print("Initializing displays...")
            self.display_manager = DisplayManager()
            
            # Initialize eye controller
            print("Initializing eye controller...")
            self.eye_controller = EyeController(self.display_manager)
            
            # Initialize face tracker
            print("Initializing face tracker...")
            self.face_tracker = FaceTracker()
            
            # Initialize audio manager
            print("Initializing audio manager...")
            self.audio_manager = AudioManager()
            
            # Initialize LED controller
            print("Initializing LED controller...")
            self.led_controller = LEDController()
            self.led_controller.set_color(*DEFAULT_LED_COLOR)
            self.led_controller.set_pattern(DEFAULT_LED_PATTERN)
            
            print("\nAll systems initialized successfully!")
            print(f"Starting in {self.current_mode} mode\n")
            
            # Test sequence
            if DEBUG_MODE:
                self.run_test_sequence()
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            self.cleanup()
            sys.exit(1)
    
    def run_test_sequence(self):
        """Run a quick test of all systems"""
        print("Running system tests...")
        
        # Test displays
        print("Testing displays...")
        self.display_manager.test_displays()
        time.sleep(1)
        
        # Test LEDs
        print("Testing LEDs...")
        self.led_controller.set_pattern(LEDPattern.RAINBOW, speed=2.0)
        for _ in range(60):  # ~1 second
            self.led_controller.update()
            time.sleep(0.016)
        self.led_controller.set_pattern(DEFAULT_LED_PATTERN)
        
        # Test audio
        print("Testing audio...")
        self.audio_manager.play_sound('ambient')
        time.sleep(2)
        
        print("System tests complete\n")
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        print("\nShutdown signal received...")
        self.cleanup()
        sys.exit(0)
    
    def check_inactivity(self):
        """Check for inactivity timeout and switch to rest mode"""
        current_time = time.time()
        
        # Only check periodically to save CPU
        if current_time - self.last_mode_check < LAST_ACTIVITY_CHECK_INTERVAL:
            return
        
        self.last_mode_check = current_time
        
        # Calculate time since last activity
        inactive_time = current_time - self.last_activity_time
        
        # Switch to rest mode if inactive too long
        if inactive_time > INACTIVITY_TIMEOUT:
            if self.current_mode != EYE_MODES['REST']:
                print(f"No activity for {INACTIVITY_TIMEOUT}s, entering rest mode")
                self.set_mode(EYE_MODES['REST'])
                self.led_controller.set_brightness(0.2)  # Dim LEDs
        else:
            # If in rest mode but activity detected, wake up
            if self.current_mode == EYE_MODES['REST'] and self.face_tracker.is_face_detected():
                print("Activity detected, waking up")
                self.set_mode(DEFAULT_MODE)
                self.led_controller.set_brightness(DOTSTAR_BRIGHTNESS)
                self.audio_manager.play_detection_sound()
    
    def set_mode(self, mode):
        """Change operating mode"""
        if mode != self.current_mode:
            self.current_mode = mode
            self.eye_controller.set_mode(mode)
            print(f"Mode changed to: {mode}")
    
    def update(self):
        """Main update loop - called every frame"""
        
        # Get face position from tracker
        face_position = None
        if self.current_mode != EYE_MODES['REST']:
            face_position = self.face_tracker.detect_faces()
        
        # Handle face detection state changes
        face_detected = self.face_tracker.is_face_detected()
        
        if face_detected:
            self.last_activity_time = time.time()
            
            # Face just detected
            if not self.face_was_detected:
                if DEBUG_MODE:
                    print("Face detected!")
                self.audio_manager.play_detection_sound()
                self.led_controller.set_pattern(LEDPattern.PULSE, speed=1.5)
            
            self.face_was_detected = True
        else:
            # Face lost
            if self.face_was_detected:
                if DEBUG_MODE:
                    print("Face lost")
                self.led_controller.set_pattern(DEFAULT_LED_PATTERN, speed=1.0)
            
            self.face_was_detected = False
        
        # Update eyes based on mode and face position
        self.eye_controller.update(face_position)
        self.eye_controller.render_all()
        
        # Update LEDs
        self.led_controller.update()
        
        # Play random ambient sounds occasionally
        current_time = time.time()
        if current_time - self.last_ambient_sound > 30:  # Every 30 seconds
            if not self.audio_manager.is_currently_playing():
                self.audio_manager.play_random_ambient()
                self.last_ambient_sound = current_time
        
        # Check for inactivity
        self.check_inactivity()
        
        # Update FPS counter
        self.frame_count += 1
        elapsed = time.time() - self.fps_start_time
        if elapsed > 5.0 and SHOW_FPS:  # Report every 5 seconds
            fps = self.frame_count / elapsed
            print(f"Main loop FPS: {fps:.1f}")
            self.frame_count = 0
            self.fps_start_time = time.time()
    
    def run(self):
        """Main program loop"""
        print("Starting main loop...\n")
        
        try:
            while True:
                self.update()
                
                # Small delay to prevent CPU overload
                # Adjust this based on performance
                time.sleep(0.01)  # ~100 FPS max
                
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean shutdown of all systems"""
        print("\nShutting down...")
        
        try:
            if self.led_controller:
                self.led_controller.cleanup()
            
            if self.audio_manager:
                self.audio_manager.cleanup()
            
            if self.face_tracker:
                self.face_tracker.cleanup()
            
            if self.display_manager:
                self.display_manager.cleanup()
            
            print("Shutdown complete")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")


def main():
    """Entry point"""
    print("="*50)
    print("THREE-EYED SKULL HALLOWEEN DECORATION")
    print("="*50)
    print()
    
    # Create and run skull controller
    skull = SkullController()
    skull.run()


if __name__ == "__main__":
    main()