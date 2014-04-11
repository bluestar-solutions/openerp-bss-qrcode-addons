# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
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

import unittest2
import openerp.tests.common as common
import zbar
from PIL import Image
from StringIO import StringIO
import json

class test_bss_qrcode(common.TransactionCase):

    @classmethod
    def setUpClass(self):
        super(test_bss_qrcode, self).setUpClass()
        self.bss_qrcode = self.registry('bss_qrcode.qrcode')
        self.res_partner = self.registry('res.partner')
        
    def setUp(self):
        super(test_bss_qrcode, self).setUp()
        
        self.bss_qrcode_manager = self.bss_qrcode.browse(
            self.cr, self.uid, self.bss_qrcode.create(self.cr, self.uid, {})
        )
        
    def test_00_print_qrcode(self):
        """I test printing qrcode"""
        
        # I get a partner
        partner_1 = self.res_partner.browse(
            self.cr, self.uid, self.ref('base.res_partner_1'))
        
        context = {
            'active_model': u'res.partner',
            'active_ids': partner_1.id  
        }

        # I get the qrcode
        qrcode_partner = self.bss_qrcode_manager.print_qrcode("7.0.1.2", context, "partner_report", "parner_file", "myserver_id")

        # Create and configure the reader
        scanner = zbar.ImageScanner()        
        scanner.parse_config('enable')
        
        # Obtain image data
        pil = Image.open(StringIO(qrcode_partner)).convert('L')
        width, height = pil.size
        raw = pil.tostring()
                
        # Wrap image data
        image = zbar.Image(width, height, 'Y800', raw)
        
        # Scan the image for barcodes
        scanner.scan(image)
        
        # Extract results
        for symbol in image:
            val = json.loads(symbol.data)
            self.assertEquals(val['version'], "7.0.1.2", "The version is not correct.")
            self.assertEquals(val['oe_object'], "res.partner", "The object is not correct.")
            self.assertEquals(val['oe_id'], partner_1.id, "The id is not correct.")
            self.assertEquals(val['report'], "partner_report", "The report is not correct.")
            self.assertEquals(val['filename'], "parner_file", "The filename is not correct.")
            self.assertEquals(val['server_id'], "myserver_id", "The server id is not correct.")

        # Clean up the image
        del(image)
        
if __name__ == '__main__':
    print "TEST"
    unittest2.main()