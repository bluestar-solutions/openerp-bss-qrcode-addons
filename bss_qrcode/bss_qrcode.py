# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2014 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import osv
import qrcode
import StringIO
import json
import datetime

class bss_qrcode(osv.osv):

    _name = 'bss_qrcode.qrcode'
    _description = "QR Code generation and files association"
    
    def print_qrcode(self, cr, uid, ids, size, version, context, report, filename, server_id, specific={}):
        
        # QR Code creation
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_M,
            box_size = size,
            border = 0,
        )

        # Get server instance

        
        # JSon parsing
        data = {
                 "datetime": str(datetime.datetime.now()),
                 "version": version,
                 "oe_object": context[u'active_model'],
                 "oe_id": context[u'active_ids'],
                 "user_id": uid,
                 "report": report,
                 "filename": filename,
                 "server_id": server_id,
                 "specific": specific
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
