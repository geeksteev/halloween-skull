"""
Display manager for controlling three round GC9A01A displays
"""

import spidev
import RPi.GPIO as GPIO
import time
import numpy as np
from config import *

class GC9A01A:
    """Driver for GC9A01A round display"""
    
    # GC9A01A Commands
    CMD_SLPOUT = 0x11  # Sleep out
    CMD_DISPON = 0x29  # Display on
    CMD_CASET = 0x2A   # Column address set
    CMD_RASET = 0x2B   # Row address set
    CMD_RAMWR = 0x2C   # Memory write
    CMD_MADCTL = 0x36  # Memory data access control
    CMD_COLMOD = 0x3A  # Interface pixel format
    
    def __init__(self, spi, cs_pin, dc_pin, rst_pin, width=240, height=240):
        self.spi = spi
        self.cs_pin = cs_pin
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.width = width
        self.height = height
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        
        # Initialize display
        self.reset()
        self.init_display()
    
    def reset(self):
        """Hardware reset"""
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)
    
    def write_cmd(self, cmd):
        """Write command byte"""
        GPIO.output(self.dc_pin, GPIO.LOW)
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.cs_pin, GPIO.HIGH)
    
    def write_data(self, data):
        """Write data bytes"""
        GPIO.output(self.dc_pin, GPIO.HIGH)
        GPIO.output(self.cs_pin, GPIO.LOW)
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)
        GPIO.output(self.cs_pin, GPIO.HIGH)
    
    def init_display(self):
        """Initialize display with proper settings"""
        self.write_cmd(self.CMD_SLPOUT)
        time.sleep(0.12)
        
        # Set color mode to 16-bit (RGB565)
        self.write_cmd(self.CMD_COLMOD)
        self.write_data(0x55)
        
        # Set rotation
        self.write_cmd(self.CMD_MADCTL)
        self.write_data(0x00)  # Adjust based on rotation needed
        
        # Display on
        self.write_cmd(self.CMD_DISPON)
        time.sleep(0.01)
    
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window"""
        self.write_cmd(self.CMD_CASET)
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        
        self.write_cmd(self.CMD_RASET)
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        
        self.write_cmd(self.CMD_RAMWR)
    
    def draw_pixel(self, x, y, color):
        """Draw a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.set_window(x, y, x, y)
            self.write_data([color >> 8, color & 0xFF])
    
    def fill_screen(self, color):
        """Fill entire screen with color"""
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Prepare color data
        color_bytes = [(color >> 8) & 0xFF, color & 0xFF]
        data = color_bytes * (self.width * self.height)
        
        # Write in chunks to avoid memory issues
        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self.write_data(chunk)
    
    def draw_buffer(self, buffer):
        """Draw a full screen buffer (240x240 RGB565 data)"""
        self.set_window(0, 0, self.width - 1, self.height - 1)
        self.write_data(buffer)


class DisplayManager:
    """Manages all three displays"""
    
    def __init__(self):
        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = SPI_SPEED_HZ
        self.spi.mode = 0
        
        # Initialize displays
        self.displays = {}
        for name, pins in DISPLAY_PINS.items():
            self.displays[name] = GC9A01A(
                self.spi,
                pins['cs'],
                pins['dc'],
                pins['rst'],
                DISPLAY_SIZE,
                DISPLAY_SIZE
            )
        
        print("Display manager initialized")
        self.clear_all()
    
    def clear_all(self):
        """Clear all displays to black"""
        for display in self.displays.values():
            display.fill_screen(0x0000)
    
    def test_displays(self):
        """Test all displays with colors"""
        colors = [0xF800, 0x07E0, 0x001F]  # Red, Green, Blue
        
        for i, (name, display) in enumerate(self.displays.items()):
            print(f"Testing {name} display...")
            display.fill_screen(colors[i % 3])
            time.sleep(1)
        
        self.clear_all()
    
    def get_display(self, name):
        """Get a specific display by name"""
        return self.displays.get(name)
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.clear_all()
        GPIO.cleanup()