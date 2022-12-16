"""
Module for controlling the display.

An instantiated Display is provided as disp (see final line)

"""
from machine import SoftI2C as I2C
from machine import Pin
from micropython import const
from ssd1306 import SSD1306_I2C
import time


class Display(SSD1306_I2C):
    
    def __init__(self):
        # Set up I2C (neded for the OLED display).
        sda_pin, scl_pin = const(4), const(15)  # white HiLetgo board
        sda = Pin(sda_pin)
        scl = Pin(scl_pin)
        i2c = I2C(sda=sda, scl=scl) 

        # Reset I2C.
        rst = Pin(16, Pin.OUT)   # I2C reset pin
        rst.off()    # set GPIO16 low to reset OLED
        rst.on()     # while using I2C GPIO16 must be high

        # Set up the OLED display:
        w = const(128) # screen width
        h = const(64)  # screen height
        self.ch = const(8)  # character width/height
        super().__init__(w, h, i2c)
        
        # Say hello.
        self.say_hello()
        self.clear_()
        
    def unit(self, i=1):
        return int(i * self.ch)
    
    # Function to center text on display
    def center_text(self, s, row):
        self.text(s, self.width//2 - len(s)//2 * self.ch, row*self.ch)  #FrameBuffer.text(s, x, y)
        
    def clear(self):
        self.fill(0)
    
    def clear_(self):
        self.fill(0)
        self.show()
    
    def clear_top(self):
        self.fill_rect(0,0,self.width,16,0)
        
    def clear_bottom(self):
        self.fill_rect(0,16,self.width,48,0)
    
    # Clear contents of screen and create 1px border
    def clear_keep_border(self):
        display.fill(1)
        display.fill_rect(1,1,self.width-2,self.height-2,0)
    
    def show_row_labels(self):
        self.clear()
        for i in range(8):
            self.text(str(i), 0, self.unit(i))
        
        self.show()
        
    def ellipse(self, cx, cy, rx, ry, c=1, f=False):
        for i in range(cx-rx, cx+rx):
            for j in range(cy-ry, cy+ry):
                if f and self._in_ellipse(i, j, cx, cy, rx, ry):
                    self.pixel(i, j, c)
                elif (not f
                      and self._in_ellipse(i, j, cx, cy, rx, ry)
                      and not self._in_ellipse(i, j, cx, cy, rx-1, ry-1)):
                    self.pixel(i, j, c)
    
    def _in_ellipse(self, x, y, cx, cy, rx, ry):
        dx = x - cx
        dy = y - cy
        x_term = dx**2 / rx**2
        y_term = dy**2 / ry**2
        if x_term + y_term <= 1:
            return True
        else:
            return False
        
    # Function to say hello at startup
    def say_hello(self, long=False):
        if long:
            for amt in range(10, -1, -2):
                self._hello()
                self.dissolve(amt)
                self.show()
        else:
            self._hello()
            self.show()
        time.sleep(1)
    
    def dissolve(self, amt):
        for i in range(self.width):
            for j in range(self.height):
                if (i + j) % 10 < amt:
                    self.pixel(i, j, 0)
    
    def _hello(self):
        x = self.unit(0.5)
        self.clear()
        self.h(x)
        self.e(x + self.unit(4))
        self.l(x + self.unit(8))
        self.l(x + self.unit(9))
        self.o(x + self.unit(10))
        self.exc(x + self.unit(14))
    
    def h(self, x):
        self.ellipse(x+self.unit(2), self.unit(7), self.unit(2), self.unit(3), f=True)
        self.ellipse(x+self.unit(2)-1, self.unit(7), self.unit(1), self.unit(2), c=0, f=True)
        self.fill_rect(x, self.unit(7), self.unit(2), self.unit(1), 0)
        self.fill_rect(x, self.unit(2), self.unit(1), self.unit(6), 1)
    
    def e(self, x):
        self.ellipse(x+self.unit(2), self.unit(6), self.unit(2)-1, self.unit(2), f=True)
        self.ellipse(x+self.unit(2), self.unit(6), self.unit(1), self.unit(1), c=0, f=True)
        self.fill_rect(x+self.unit(0.5), self.unit(5.75), self.unit(3), self.unit(0.5), 1)
        self.fill_rect(x+self.unit(2), self.unit(6.25), self.unit(2), self.unit(0.5), 0)
    
    def l(self, x):
        self.fill_rect(x, self.unit(2), self.unit(1)-1, self.unit(6), 1)
        
    def o(self, x):
        self.ellipse(x+self.unit(2), self.unit(6), self.unit(2)-1, self.unit(2), f=True)
        self.ellipse(x+self.unit(2), self.unit(6), self.unit(1), self.unit(1), c=0, f=True)
    
    def exc(self, x):
        self.fill_rect(x, self.unit(2), self.unit(1)-1, self.unit(6), 1)
        self.fill_rect(x, self.unit(6), self.unit(1)-1, self.unit(1), 0)
        
disp = Display()
