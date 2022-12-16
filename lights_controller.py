from qr_display import QRDisp  # for some reason this needs to come first or it'll run out of memory

from machine import Pin, ADC
import time
import utime

from microphone import ClapMic
from motion import Detector
from web import Server
from tp_link import Kasa
from wifi import WiFi, NetworkNotFoundException
from display import disp


class DummyDetector:
    idle_time_min = 5

class DummyMic:
    pass
    

class LightsController:
    
    def __init__(self, mic_pin_no=14, motion_pin_no=27, motion_timeout_minutes=10, wifi_credentials=WiFi.home_wifi):        
        self.CLAP_TOGGLE_ENABLED = True
        self.MOTION_TURN_ON_ENABLED = True
        self.NO_MOTION_TURN_OFF_ENABLED = True
        
        self.motion_timeout_minutes = motion_timeout_minutes
        
        self.mic = ClapMic(
            pin=Pin(mic_pin_no, Pin.IN),
            callback=self._clap)
        self.motion_detector = Detector(
            pin=Pin(motion_pin_no, Pin.IN),
            motion_callback=self._motion,
            stillness_callback=self._no_motion,
            idle_time_min=self.motion_timeout_minutes)
        self.wifi = WiFi()
        self.wifi_credentials = wifi_credentials
        self.web_server = Server()
        self.lights = None  # This will be initialized after the wifi is set up
    
    def control_lights(self):

        while True:
            try:
                ip = self._set_up_wifi()
                self.lights = Kasa()
                self.web_server.start(  # this call is blocking unless an error is thrown
                    control_callback=self._control,
                    status_callback=self._status)
            
            except OSError as e:
                print("OSError!")
                print(e)
            finally:
                print('Error thrown, cleaning up.')
                self.lights = None
                if self.wifi.wlan.active():
                    self.wifi.disconnect()
                disp.clear()
                disp.center_text('ERROR!', 3)
                disp.center_text('Resetting...', 4)
                disp.show()
                utime.sleep_ms(1000)
    
    def _clap(self):
        print('double clap!')
        if self.CLAP_TOGGLE_ENABLED and self.lights:
            self.lights.toggle()
    
    def _motion(self):
        print('motion!')
        if self.MOTION_TURN_ON_ENABLED and self.lights:
            self.lights.on()
    
    def _no_motion(self):
        print('stillness...')
        if self.NO_MOTION_TURN_OFF_ENABLED and self.lights:
            self.lights.off()
    
    def _set_up_wifi(self):
        try:
            ip = self.wifi.connect(**self.wifi_credentials, show_ip=1)  # print ip on top line
        except NetworkNotFoundException as e:
            # If the network isn't found, wait a bit and try one more time
            print(e)
            print('Trying once more to connect...')
            utime.sleep_ms(4000)
            ip = self.wifi.connect(**self.wifi_credentials, show_ip=1)
        # The QRDisp object is intentionally not stored as an instance variable
        # to allow it to be garbage collected so we don't run out of memory
        QRDisp().show_qr_for(f'http://{ip}')
        return ip
    
    def _status(self):
        return (self.lights.lights_are_on(),
                self.CLAP_TOGGLE_ENABLED,
                self.MOTION_TURN_ON_ENABLED,
                self.NO_MOTION_TURN_OFF_ENABLED,
                self.motion_detector.idle_time_min)
    
    def _control(self,
                 clap_toggle=None,
                 movement_on=None,
                 stillness_off=None,
                 timeout=None,
                 lights_command=None):
        if clap_toggle is not None:
            self.CLAP_TOGGLE_ENABLED = clap_toggle
        if movement_on is not None:
            self.MOTION_TURN_ON_ENABLED = movement_on
        if stillness_off is not None:
            self.NO_MOTION_TURN_OFF_ENABLED = stillness_off
        if timeout is not None:
            self.motion_detector.idle_time_min = timeout
        if lights_command is not None:
            if lights_command == 'on':
                self.lights.on()
            elif lights_command == 'off':
                self.lights.off()
            elif lights_command == 'toggle':
                self.lights.toggle()
