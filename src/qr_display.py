from uQR import QRCode, ERROR_CORRECT_H
from display import disp

class QRDisp(QRCode):
    
    def __init__(self, **kwargs):
        options = {'version':7, 'error_correction':ERROR_CORRECT_H, 'border':0}
        options.update(kwargs)
        super().__init__(**options)
        
        
    def show_qr_for(self, s, x='centered', y=16):
        disp.clear_bottom()
        disp.center_text('Generating', 4)
        disp.center_text('QR code...', 5)
        disp.show()
        self.add_data(s)
        matrix = self.get_matrix()
        if x == 'centered':
            x = disp.width//2 - len(matrix[0])//2
        disp.clear_bottom()
        for i, row in enumerate(matrix):
            for j, cell in enumerate(row):
                if cell:
                    disp.pixel(x+i,y+j,1)
                    
        disp.show()        
    