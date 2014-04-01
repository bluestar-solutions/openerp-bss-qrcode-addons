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

from openerp.osv import osv, fields

""" Class which contains all imported files of an xmlrpc call. """
class bss_import(osv.osv):

    _name = 'bss_qrcode.import'
    _description = "Imported files by xmlrpc"
   
    _columns = {
        'identifier': fields.char('Identifier from java'),
        'success_ids': fields.one2many('bss_qrcode.success', 'success_id', string='Succeed imported documents'),
        'fail_ids': fields.one2many('bss_qrcode.error', 'error_ids', string='Failed imported documents'),
        'qrcode_not_found_ids': fields.one2many('bss_qrcode.qrcode_not_found', 'qrcode_not_found_id', string='QR Code not found'),        
    }
    
    """ Function called by an xmlrpc connection. Create an import object with documents. """
    def add_to_import_object(self, cr, uid, java_identifier, qrcode_id, document):
        import_id = self.search(cr, uid, [('identifier', '=', java_identifier)])
        
        # If the import object already exists then use it, create it else
        if import_id:
            myimport = self.read(cr, uid, import_id[0])
        else:
            myimport = self.create(cr, uid, {'identifier': java_identifier})
        
        
        # Create the row document
        row = self.pool.get('bss_qrcode.success').create(cr, uid, {'qrcode_id': qrcode_id, 'document': document})        
        
        myimport.append({'success': row})
        
        print myimport.success_ids
        
        return myimport.id
                 
bss_import()
   
""" Successful imported document. """            
class bss_success(osv.osv):

    _name = 'bss_qrcode.success'
    _description = "Successfully imported files"
   
    _columns = {
        'qrcode_id': fields.many2one('bss_qrcode.qrcode', string='QR Code', required=True),
        'document': fields.binary('Document')
    }

bss_success()

""" Failed imported document for any reason (id not found, report not found, etc). """           
class bss_fail(osv.osv):

    _name = 'bss_qrcode.fail'
    _description = "Failed imported files"
   
    _columns = {
        'qrcode_id': fields.many2one('bss_qrcode.qrcode', string='QR Code', required=True),
        'document': fields.binary('Document'),
        'reason': fields.char('Reason')
    }
    
bss_fail()

""" Imported document where QR Code was not found. """               
class bss_qrcode_not_found(osv.osv):

    _name = 'bss_qrcode.qrcode_not_found'
    _description = "Imported files where QR Code were not found"
   
    _columns = {
        'document': fields.binary('Document')
    }

bss_qrcode_not_found()