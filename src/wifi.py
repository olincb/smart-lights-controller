# wifi.py
# Establish WiFi connection

from display import disp
import network
import time
import utime


class NetworkNotFoundException(Exception):
    pass


class WiFi:
    statuses = {
        network.STAT_IDLE: 'IDLE',
        network.STAT_CONNECTING: 'CONNECTING',
        network.STAT_WRONG_PASSWORD: 'WRONG_PASSWORD',
        network.STAT_NO_AP_FOUND: 'NO_AP_FOUND',
    #     network.STAT_CONNECT_FAIL: 'CONNECT_FAIL',
        network.STAT_GOT_IP: 'GOT_IP'}
    home_wifi = {
        'ssid': 'home_wifi_ssid',
        'password': 'home_wifi_password'}
    class_wifi = {
        'ssid': 'class_wifi_ssid',
        'password': 'class_wifi_password'}
    
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.n_retries_before_reset = 4
        
        if self.wlan.active():
            self.disconnect()
            self.wlan.active(False)
            utime.sleep_ms(100)

    def _connect(self, ssid, password):
        # Pass the ssid and password for the desired network
        # Return the IP address assigned to the ESP32 by the router
        
        self.wlan.active(True)

        print('Available networks:')
        available_networks = []
        for (scan_ssid, bssid, channel, RSSI, security, hidden) in self.wlan.scan():
            if len(scan_ssid) > 0:
                available_networks.append(scan_ssid.decode('utf-8'))
        for network in available_networks:
            print(f'    {network}')
        
        if not ssid in available_networks:
            raise NetworkNotFoundException(f'{ssid} not found! (Available networks: {', '.join(available_networks)})')
        
        print(f'\nConnecting to {ssid}')
        
        self.disconnect()
        self.wlan.connect(ssid, password)
        utime.sleep_ms(20)
        begin_time = time.ticks_ms()
        n_retries = 0
        while not self.wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), begin_time) > 30000:
                self.disconnect()
                print('Retrying...')
                utime.sleep_ms(5000)
                if n_retries >= self.n_retries_before_reset:
                    print('Retried a lot and failed... resetting device.')
                    import machine
                    machine.reset()
                n_retries += 1
                self.wlan.connect(ssid, password)
                begin_time = time.ticks_ms()
            timestamp = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), timestamp) < 2000: utime.sleep_ms(100)
            print(WiFi.statuses[self.wlan.status()])
        
        ip = self.wlan.ifconfig()[0]
        
        return ip

    def connect(self, ssid, password, show_ip=False):
        if isinstance(show_ip, int):
            linenum = show_ip
            show_ip = True
        else:
            linenum = 4
        if show_ip:
            disp.clear()
            disp.center_text('connecting',2)  
            disp.center_text('to',3)  
            disp.center_text(ssid, 4) 
            disp.show()
        ip = self._connect(ssid, password)
        if show_ip:
            disp.clear()
            disp.center_text(ip, linenum)
            disp.show()
        print(f'ip: {ip}')
        return ip
    
    def disconnect(self):
        self.wlan.disconnect()
        utime.sleep_ms(30)
    
