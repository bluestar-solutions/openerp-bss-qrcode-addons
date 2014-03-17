# -*- coding: utf-8 -*-

from openerp.osv import osv
import qrcode
import StringIO
import json

class bss_qrcode(osv.osv):

    _name = 'bss_qrcode.qrcode'
    _description = "QR Code generation and files association"
    
    def print_qrcode(self, oe_object, oe_id, ):

        # QR Code creation
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_M,
            box_size = 5,
            border = 0,
        )

        # JSon parsing
        data = {
                 "oe_object": oe_object,
                 "oe_id": oe_id,
        }        
        json = json.dump(data)
        
        # QR Code filling
        qr.add_data(json)
        qr.make(fit=True)
        img = qr.make_image()

        # Get the QR Code stream
        output = StringIO.StringIO()
        img.save(output)
        content = output.getvalue()
        output.close()
        
        return content
    
bss_qrcode()
