"""
LED controller for DotStar (SK9822) LED strip
"""

import time
import math
import board
import adafruit_dotstar
from config import *

class LEDPattern:
    """LED animation patterns"""
    SOLID = 'solid'
    PULSE = 'pulse'
    RAINBOW = 'rainbow'
    CHASE = 'chase'
    FIRE = 'fire'
    STROBE = 'strobe'

class LEDController:
    """Manages DotStar LED strip"""
    
    def __init__(self):
        try:
            # Initialize DotStar strip
            # Note: DotStar uses hardware SPI, shares with displays
            self.strip = adafruit_dotstar.DotStar(
                board.SCK,  # Clock pin (GPIO 11)
                board.MOSI,  # Data pin (GPIO 10)
                DOTSTAR_NUM_LEDS,
                brightness=DOTSTAR_BRIGHTNESS,
                auto_write=False
            )
            
            self.num_leds = DOTSTAR_NUM_LEDS
            self.brightness = DOTSTAR_BRIGHTNESS
            self.current_color = DEFAULT_LED_COLOR
            self.current_pattern = DEFAULT_LED_PATTERN
            self.pattern_speed = 1.0
            
            # Animation state
            self.animation_frame = 0
            self.last_update = time.time()
            
            # Clear strip on init
            self.clear()
            self.strip.show()
            
            print(f"LED controller initialized: {self.num_leds} LEDs")
            
        except Exception as e:
            print(f"Error initializing LED controller: {e}")
            self.strip = None
    
    def set_color(self, r, g, b):
        """
        Set the base color for LED effects
        
        Args:
            r, g, b: RGB values (0-255)
        """
        self.current_color = (
            max(0, min(255, int(r))),
            max(0, min(255, int(g))),
            max(0, min(255, int(b)))
        )
        
        if DEBUG_MODE:
            print(f"LED color set to RGB({r}, {g}, {b})")
    
    def set_brightness(self, brightness):
        """
        Set overall brightness
        
        Args:
            brightness: Float between 0.0 and 1.0
        """
        self.brightness = max(0.0, min(1.0, brightness))
        if self.strip:
            self.strip.brightness = self.brightness
        
        if DEBUG_MODE:
            print(f"LED brightness set to {self.brightness * 100:.0f}%")
    
    def set_pattern(self, pattern, speed=1.0):
        """
        Set LED animation pattern
        
        Args:
            pattern: Pattern name (use LEDPattern constants)
            speed: Animation speed multiplier (default 1.0)
        """
        self.current_pattern = pattern
        self.pattern_speed = speed
        self.animation_frame = 0
        
        if DEBUG_MODE:
            print(f"LED pattern set to: {pattern} (speed: {speed}x)")
    
    def clear(self):
        """Turn off all LEDs"""
        if self.strip:
            self.strip.fill((0, 0, 0))
    
    def update(self):
        """Update LED animation - call this regularly in main loop"""
        if not self.strip:
            return
        
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Update animation frame based on speed
        self.animation_frame += dt * self.pattern_speed * 60  # 60fps base rate
        
        # Execute current pattern
        if self.current_pattern == LEDPattern.SOLID:
            self._pattern_solid()
        elif self.current_pattern == LEDPattern.PULSE:
            self._pattern_pulse()
        elif self.current_pattern == LEDPattern.RAINBOW:
            self._pattern_rainbow()
        elif self.current_pattern == LEDPattern.CHASE:
            self._pattern_chase()
        elif self.current_pattern == LEDPattern.FIRE:
            self._pattern_fire()
        elif self.current_pattern == LEDPattern.STROBE:
            self._pattern_strobe()
        
        # Update physical LEDs
        self.strip.show()
    
    def _pattern_solid(self):
        """Solid color fill"""
        self.strip.fill(self.current_color)
    
    def _pattern_pulse(self):
        """Breathing/pulsing effect"""
        # Sine wave for smooth pulsing
        pulse = (math.sin(self.animation_frame * 0.05) + 1) / 2  # 0.0 to 1.0
        
        r, g, b = self.current_color
        dimmed_color = (
            int(r * pulse),
            int(g * pulse),
            int(b * pulse)
        )
        
        self.strip.fill(dimmed_color)
    
    def _pattern_rainbow(self):
        """Rainbow color cycle"""
        for i in range(self.num_leds):
            # Calculate hue based on position and animation frame
            hue = (i / self.num_leds + self.animation_frame * 0.001) % 1.0
            color = self._hsv_to_rgb(hue, 1.0, 1.0)
            self.strip[i] = color
    
    def _pattern_chase(self):
        """Color chase effect"""
        position = int(self.animation_frame * 0.2) % self.num_leds
        
        for i in range(self.num_leds):
            if i == position:
                self.strip[i] = self.current_color
            else:
                # Fade trail
                distance = min(abs(i - position), self.num_leds - abs(i - position))
                fade = max(0, 1.0 - distance / 5.0)
                r, g, b = self.current_color
                self.strip[i] = (int(r * fade), int(g * fade), int(b * fade))
    
    def _pattern_fire(self):
        """Fire flicker effect"""
        import random
        
        for i in range(self.num_leds):
            # Random flicker
            flicker = random.uniform(0.3, 1.0)
            
            # Fire colors (red/orange/yellow)
            r = int(255 * flicker)
            g = int(100 * flicker * random.uniform(0.3, 0.7))
            b = 0
            
            self.strip[i] = (r, g, b)
    
    def _pattern_strobe(self):
        """Strobe effect"""
        # Fast on/off
        if int(self.animation_frame * 0.5) % 2 == 0:
            self.strip.fill(self.current_color)
        else:
            self.strip.fill((0, 0, 0))
    
    def _hsv_to_rgb(self, h, s, v):
        """
        Convert HSV color to RGB
        
        Args:
            h: Hue (0.0 to 1.0)
            s: Saturation (0.0 to 1.0)
            v: Value/brightness (0.0 to 1.0)
            
        Returns:
            (r, g, b) tuple with values 0-255
        """
        if s == 0.0:
            r = g = b = int(v * 255)
            return (r, g, b)
        
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def set_individual_led(self, index, r, g, b):
        """
        Set individual LED color
        
        Args:
            index: LED index (0 to num_leds-1)
            r, g, b: RGB values (0-255)
        """
        if self.strip and 0 <= index < self.num_leds:
            self.strip[index] = (r, g, b)
    
    def fill_range(self, start, end, r, g, b):
        """
        Fill a range of LEDs with a color
        
        Args:
            start: Start index
            end: End index (inclusive)
            r, g, b: RGB values (0-255)
        """
        if not self.strip:
            return
        
        for i in range(max(0, start), min(self.num_leds, end + 1)):
            self.strip[i] = (r, g, b)
    
    def cleanup(self):
        """Turn off all LEDs and cleanup"""
        if self.strip:
            self.clear()
            self.strip.show()
            print("LED controller stopped")