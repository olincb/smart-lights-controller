from machine import Pin, Timer


class Detector:
    
    def __init__(self, pin, motion_callback, stillness_callback, idle_time_min=5):
        self.pin = pin
        self.motion_callback = motion_callback
        self.stillness_callback = stillness_callback
        self.idle_time_min = idle_time_min
        self.countdown_timer = Timer(0)
        self.pin.irq(handler=self._sensor_change, trigger=(Pin.IRQ_RISING | Pin.IRQ_FALLING))
        
    def _still_cb_proxy(self, t):
        self.stillness_callback()        
        
    def _sensor_change(self, pin):
        if self.motion_detected(pin):
            self.countdown_timer.deinit()
            self.motion_callback()
        else:  # no motion
            self.countdown_timer.init(mode=Timer.ONE_SHOT, period=self.idle_time_min*60*1000, callback=self._still_cb_proxy)
        
    def motion_detected(self, pin=None):
        if pin is None:
            pin = self.pin
        return pin() == 1
        