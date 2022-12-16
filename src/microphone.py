import time
from machine import Pin
import random


class ClapMic:
    
    def __init__(self, pin, callback, clap_length_ms=100, double_clap_sensitivity_ms=1000, timeout_ms=1500):
        self.pin = pin
        self.callback = callback
        self.clap_length_ms = clap_length_ms
        self.double_clap_sensitivity_ms = double_clap_sensitivity_ms
        self.timeout_ms = timeout_ms
        self.last_clap = 0
        self.last_called = 0
        self.pin.irq(handler=self._callback, trigger=Pin.IRQ_FALLING)
        
        self.debug = False
        
    def _callback(self, p):
        cur_time = time.ticks_ms()
        clap_diff = cur_time - self.last_clap
        if clap_diff > self.clap_length_ms:  # we're hearing a new clap
            if self.debug: print('single clap.', ''.join([random.choice(['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']) for _ in range(3)]))
            self.last_clap = cur_time
            call_diff = cur_time - self.last_called
            if (clap_diff < self.double_clap_sensitivity_ms  # only run the callback if it's a double clap
                and call_diff > self.timeout_ms):            # and if it wasn't just called
                self.last_called = cur_time
                self.callback()
                self.last_called = time.ticks_ms()  # reset when done too in case the callback took a bit
