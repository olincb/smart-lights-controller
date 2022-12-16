# Some functions in this file are slight modifications from
# https://github.com/softScheck/tplink-smartplug/blob/master/tplink_smartplug.py
# which is licensed under the Apache License, Version 2.0

from struct import pack
import socket

class Kasa:
    
    commands = {
        'info'     : '{"system":{"get_sysinfo":{}}}',
        'on'       : '{"system":{"set_relay_state":{"state":1}}}',
        'off'      : '{"system":{"set_relay_state":{"state":0}}}',
        'ledoff'   : '{"system":{"set_led_off":{"off":1}}}',
        'ledon'    : '{"system":{"set_led_off":{"off":0}}}',
        'cloudinfo': '{"cnCloud":{"get_info":{}}}',
        'wlanscan' : '{"netif":{"get_scaninfo":{"refresh":0}}}',
        'time'     : '{"time":{"get_time":{}}}',
        'schedule' : '{"schedule":{"get_rules":{}}}',
        'countdown': '{"count_down":{"get_rules":{}}}',
        'antitheft': '{"anti_theft":{"get_rules":{}}}',
        'reboot'   : '{"system":{"reboot":{"delay":1}}}',
        'reset'    : '{"system":{"reset":{"delay":1}}}',
        'energy'   : '{"emeter":{"get_realtime":{}}}'
    }
    
    def __init__(self):
        self.plug_hostname = 'HS100'
        self.plug_port = 9999
        self.timeout = 8
        self.command_retries = 3
        
    def _send_command(self, command, verbose=True):
        if verbose: print(f'Sending command: {command}')
        success = False
        data = None
        tries = 0
        while not (success or tries >= self.command_retries):
            tries += 1
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.settimeout(self.timeout)
            if verbose: print(f'Connecting to {self.plug_hostname}:{self.plug_port}')
            try:
                sock_tcp.connect((self.plug_hostname, self.plug_port))
                sock_tcp.settimeout(None)
                if verbose: print('Connected to device.')
                sock_tcp.send(Kasa._encrypt(command))
                if verbose: print('Command sent.')
                data = sock_tcp.recv(2048)
                success = True
            except OSError as e:
                print(f'OSError: {e}')
            finally:
                sock_tcp.close()
        if data:
            decrypted = Kasa._decrypt(data)
            if verbose: print(f'Received: {decrypted}')
            return decrypted
        else:
            return ""
    
    def _encrypt(string):
        key = 171
        result = pack(">I", len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            result += bytes([a])
        return result
    
    def _decrypt(string):
        string = string[4:]  # chop off length of string 
        key = 171
        result = ""
        for i in string:
            a = key ^ i
            key = i
            result += chr(a)
        return result
    
    def info(self):
        return self._send_command(Kasa.commands['info'])
    
    def lights_are_on(self):
        """ Check if the lights are on.
        Returns True if the lights are on,
                False if the lights are off, and
                None if it can't determine the state.
        """
        state = self.info()
        loc = state.find('"relay_state":') + 14
        state = state[loc:loc+1]
        if state == '1':  # lights are on
            return True
        elif state == '0':  # lights are off
            return False
        else:  # something unexpected happened
            print("Error! Don't know if lights are on or off...")
            return None
    
    def toggle(self):
        """ Toggles the state of the lights.
        Does nothing if it was unable to determine if the lights were on or off.
        Returns True if success and False if failure.
        """
        on = self.lights_are_on()
        if on:
            res = self.off()
        elif on == False:
            res = self.on()
        else:
            res = ""
        return res
    
    def _action_command(self, command):
        """ Works for things like `on` and `off`
        Returns True on success and False on failure
        """
        resp = self._send_command(Kasa.commands[command])
        loc = resp.find('"err_code":') + 9
        success = resp[loc:loc+1] == '0'
        return success 
        
    def off(self):
        """ Turn the lights off.
        Returns True on success and False on failure
        """
        return self._action_command('off')
    
    def on(self):
        """ Turn the lights on.
        Returns True on success and False on failure
        """
        return self._action_command('on')
