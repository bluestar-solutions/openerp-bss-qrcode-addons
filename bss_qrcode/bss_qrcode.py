# -*- coding: utf-8 -*-

from openerp.osv import osv
import qrcode
import StringIO
import json

class bss_qrcode(osv.osv):

    _name = 'bss_qrcode.qrcode'
    _description = "QR Code generation and files association"
    
    def print_qrcode(self, cr, uid, ids, context=None):
        print context
        
        # QR Code creation
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_M,
            box_size = 5,
            border = 0,
        )

        # JSon parsing
        data = {
                 "oe_object": 1,
                 "oe_id": 1,
        }        
        json_values = json.dumps(data)
        
        # QR Code filling
        qr.add_data(json_values)
        qr.make(fit=True)
        img = qr.make_image()

        # Get the QR Code stream
        output = StringIO.StringIO()
        img.save(output)
        content = output.getvalue()
        output.close()
        
        return content
    
bss_qrcode()
