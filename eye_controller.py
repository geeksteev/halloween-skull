"""
Eye animation controller based on Adafruit M4_Eyes logic
"""

import time
import random
import math
from config import *

class EyeState:
    """Blink states"""
    NOBLINK = 0
    ENBLINK = 1  # Eye closing
    DEBLINK = 2  # Eye opening

class Eye:
    """Individual eye with animation state"""
    
    def __init__(self, name, display):
        self.name = name
        self.display = display
        
        # Position (-1.0 to 1.0 normalized coordinates)
        self.eye_x = 0.0
        self.eye_y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        
        # Movement state
        self.in_motion = False
        self.move_start_time = 0
        self.move_duration = 0
        self.old_x = 0.0
        self.old_y = 0.0
        self.new_x = 0.0
        self.new_y = 0.0
        
        # Blink state
        self.blink_state = EyeState.NOBLINK
        self.blink_start_time = 0
        self.blink_duration = 0
        self.blink_factor = 0.0
        
        # Appearance
        self.pupil_factor = 0.5
        self.upper_lid_factor = 1.0
        self.lower_lid_factor = 1.0
        
        # Last saccade timing
        self.last_saccade_stop = time.time() * 1000000
        self.saccade_interval = 0
        
    def update_autonomous(self, current_time_us):
        """Update eye with autonomous wandering behavior"""
        dt = current_time_us - self.move_start_time
        
        if self.in_motion:
            if dt >= self.move_duration:
                # Movement complete
                self.in_motion = False
                self.eye_x = self.old_x = self.new_x
                self.eye_y = self.old_y = self.new_y
                
                # Set hold duration
                limit = min(1000000, GAZE_MAX)
                self.move_duration = random.randint(35000, limit)
                
                if not self.saccade_interval:
                    self.last_saccade_stop = current_time_us
                    self.saccade_interval = random.randint(self.move_duration, GAZE_MAX)
                
                self.move_start_time = current_time_us
            else:
                # Interpolate position with easing
                e = dt / self.move_duration
                e = 3 * e * e - 2 * e * e * e  # Smooth easing function
                self.eye_x = self.old_x + (self.new_x - self.old_x) * e
                self.eye_y = self.old_y + (self.new_y - self.old_y) * e
        else:
            # Eye stopped, check if time to move
            self.eye_x = self.old_x
            self.eye_y = self.old_y
            
            if dt > self.move_duration:
                if (current_time_us - self.last_saccade_stop) > self.saccade_interval:
                    # Time for a big saccade
                    r = DISPLAY_SIZE * 0.75
                    self.new_x = random.uniform(-r, r)
                    h = math.sqrt(r * r - self.new_x * self.new_x)
                    self.new_y = random.uniform(-h, h)
                    self.move_duration = random.randint(SACCADE_MIN_DURATION, SACCADE_MAX_DURATION)
                    self.saccade_interval = 0
                else:
                    # Microsaccade
                    r = DISPLAY_SIZE * 0.07
                    dx = random.uniform(-r, r)
                    self.new_x = self.eye_x + dx
                    h = math.sqrt(r * r - dx * dx)
                    self.new_y = self.eye_y + random.uniform(-h, h)
                    self.move_duration = random.randint(MICROSACCADE_MIN_DURATION, MICROSACCADE_MAX_DURATION)
                
                self.move_start_time = current_time_us
                self.in_motion = True
    
    def update_tracking(self, target_x, target_y):
        """Update eye to track a target (-1.0 to 1.0 range)"""
        r = DISPLAY_SIZE * 0.9
        self.eye_x = target_x * r
        self.eye_y = target_y * r
    
    def update_blink(self, current_time_us):
        """Update blink animation"""
        if self.blink_state != EyeState.NOBLINK:
            dt = current_time_us - self.blink_start_time
            
            if dt >= self.blink_duration:
                # State transition
                if self.blink_state == EyeState.ENBLINK:
                    # Switch to opening
                    self.blink_state = EyeState.DEBLINK
                    self.blink_duration *= 2  # Opening is slower
                    self.blink_start_time = current_time_us
                    self.blink_factor = 1.0
                else:
                    # Blink complete
                    self.blink_state = EyeState.NOBLINK
                    self.blink_factor = 0.0
            else:
                # Calculate blink progress
                self.blink_factor = dt / self.blink_duration
                if self.blink_state == EyeState.DEBLINK:
                    self.blink_factor = 1.0 - self.blink_factor
    
    def start_blink(self, current_time_us, duration):
        """Trigger a blink"""
        if self.blink_state == EyeState.NOBLINK:
            self.blink_state = EyeState.ENBLINK
            self.blink_start_time = current_time_us
            self.blink_duration = duration
    
    def render(self):
        """Render the eye to the display (simplified for now)"""
        # This would be the complex polar mapping and texture code
        # For now, just draw a simple representation
        
        # Calculate screen position
        screen_x = int(DISPLAY_SIZE / 2 + self.eye_x)
        screen_y = int(DISPLAY_SIZE / 2 + self.eye_y)
        
        # Clear display
        self.display.fill_screen(SCLERA_COLOR)
        
        # Draw iris (simplified - just a filled region)
        iris_radius = int(IRIS_RADIUS * (1.0 - self.blink_factor))
        # This is where you'd draw the actual eye graphics
        
        # TODO: Implement full eye rendering with polar mapping


class EyeController:
    """Controls all three eyes"""
    
    def __init__(self, display_manager):
        self.display_manager = display_manager
        self.mode = DEFAULT_MODE
        
        # Create eye objects
        self.eyes = {
            'left': Eye('left', display_manager.get_display('left')),
            'right': Eye('right', display_manager.get_display('right')),
            'middle': Eye('middle', display_manager.get_display('middle'))
        }
        
        # Blink timing
        self.last_blink_time = time.time() * 1000000
        self.next_blink_time = self.last_blink_time + random.randint(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MIN * 2)
        
        print(f"Eye controller initialized in {self.mode} mode")
    
    def set_mode(self, mode):
        """Change eye behavior mode"""
        if mode in EYE_MODES.values():
            self.mode = mode
            print(f"Eye mode changed to: {mode}")
        else:
            print(f"Invalid mode: {mode}")
    
    def update(self, face_position=None):
        """Update all eyes based on current mode"""
        current_time_us = int(time.time() * 1000000)
        
        # Handle blinks (all eyes)
        if current_time_us >= self.next_blink_time:
            duration = random.randint(BLINK_MIN_DURATION, BLINK_MAX_DURATION)
            for eye in self.eyes.values():
                eye.start_blink(current_time_us, duration)
            self.last_blink_time = current_time_us
            self.next_blink_time = current_time_us + duration * 3 + random.randint(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MIN * 2)
        
        # Update blink animation
        for eye in self.eyes.values():
            eye.update_blink(current_time_us)
        
        # Update eye positions based on mode
        if self.mode == EYE_MODES['TRACKING']:
            # Middle eye tracks, left/right wander
            if face_position:
                self.eyes['middle'].update_tracking(face_position[0], face_position[1])
            else:
                self.eyes['middle'].update_autonomous(current_time_us)
            
            self.eyes['left'].update_autonomous(current_time_us)
            self.eyes['right'].update_autonomous(current_time_us)
            
        elif self.mode == EYE_MODES['WANDERING']:
            # All eyes wander
            for eye in self.eyes.values():
                eye.update_autonomous(current_time_us)
                
        elif self.mode == EYE_MODES['REST']:
            # Eyes closed or minimal movement
            for eye in self.eyes.values():
                eye.blink_factor = 1.0  # Keep closed
    
    def render_all(self):
        """Render all eyes to their displays"""
        for eye in self.eyes.values():
            eye.render()