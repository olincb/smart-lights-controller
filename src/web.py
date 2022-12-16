import socket
import utime


class Server:
    
    def __init__(self):
        # these will be initialized when the server is started
        self.control_callback = lambda **kwargs: None
        self.status_callback = lambda: (None, None, None, None, None)
    
    def start(self, control_callback, status_callback):
        self.control_callback = control_callback
        self.status_callback = status_callback
        
        try:
            print('Starting server')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 80))
            s.listen(3)
            while True:
                print('Waiting for connection...')
                try:
                    conn, addr = s.accept()
                    print(f'Connection from {addr}')
                    data = str(conn.recv(1024))  # specify buffer size (max data to be received)
                    print(f'Received: {data}')
                    self.send_response(conn, addr, data)  # this is where we do the logic
                finally:
                    conn.close()  # make sure the connection gets closed
                    utime.sleep_ms(30)
        finally:
            s.close()
            utime.sleep_ms(30)
                
    def send_response(self, conn, addr, data):
        endpoint = data[2:data.find('HTTP')]
        print(endpoint)
        png = 'png' in endpoint
        fav = 'favicon' in endpoint
        if len(data) > 3 and not png and not fav:
            conn.send('HTTP/1.0 200 OK\n')         # status line 
            conn.send('Content-type: text/html\n') # header (content type)
            conn.send('Connection: close\n\n')     # header (tell client to close at end)
            if addr[0] == '192.168.1.1':  # this is the router... it probably won't care what we return
                print('got request from router')
                conn.send('Hi, router!')
                return
            if 'status' in endpoint:
                self.send_lights_status_html(conn)
            elif 'on' in endpoint:
                self.control_callback(lights_command='on')
                self.send_lights_status_html(conn)
            elif 'off' in endpoint:
                self.control_callback(lights_command='off')
                self.send_lights_status_html(conn)
            elif 'settings' in endpoint:
                to_set = data[data.find(r'\r\n\r\n')+8:-1]
                self.parse_and_set_settings(to_set)
                self.send_lights_status_html(conn)
            else:
                self.send_html(conn)
        elif len(data) <= 3:  # `b''` is len 3 but still empty
            print('Empty request')
        elif png or fav:
            print('image requested... returning 404')
            conn.send('HTTP/1.0 404 Not Found\n')
            conn.send('Connection: close\r\n\r\n')
            
    def parse_and_set_settings(self, to_set):
        print(f'settings to set: {to_set}')
        clap_toggle = 'clap_toggle=on' in to_set
        movement_on = 'movement_on=on' in to_set
        stillness_off = 'stillness_off=on' in to_set
        loc = to_set.find('timeout=') + 8
        to_set = to_set[loc:]
        andloc = to_set.find('&')
        if andloc == -1:
            timeout = int(to_set)
        else:
            timeout = int(to_set[:andloc])
        self.control_callback(clap_toggle=clap_toggle,
                              movement_on=movement_on,
                              stillness_off=stillness_off,
                              timeout=timeout)
                
    def send_lights_status_html(self, conn):
        lights_status = self.generate_lights_status()
        try:
            f = open('lights_status.html')
            for line in f.readlines():
                conn.sendall(line.replace('<<<lights_status>>>', lights_status))
        finally:
            f.close()
            utime.sleep_ms(30)
    
    def generate_lights_status(self, on=None):
        if on is None:
            on, _, _, _, _ = self.status_callback()
        return '<b style="color:green;">ON</b>' if on else '<b style="color:darkgray;">OFF</b>'
        

    def send_html(self, conn):
        lights_on, clap_toggle, motion_on, stillness_off, timeout_min = self.status_callback()
        lights_status = self.generate_lights_status(lights_on)
        lights_status_safe = lights_status.replace('"', '&quot;')
        clap_toggle = " checked" if clap_toggle else ""
        motion_on = " checked" if motion_on else ""
        stillness_off = " checked" if stillness_off else ""
        timeout_min = str(timeout_min)
        try:
            f = open('controller_page.html')
            line = f.readline()
            while line:  # using this method because sending the whole string uses too much memory
                conn.sendall(line.replace(
                    '<<<lights_status>>>', lights_status_safe
                ).replace(
                    '<<<clap_toggle_checked>>>', clap_toggle
                ).replace(
                    '<<<movement_on_checked>>>', motion_on
                ).replace(
                    '<<<stillness_off_checked>>>', stillness_off
                ).replace(
                    '<<<timeout_min>>>', timeout_min))
                line = f.readline()
        finally:
            f.close()
