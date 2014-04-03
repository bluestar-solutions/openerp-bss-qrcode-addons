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

# Pseudo constants
FAIL_QRCODE = "OpenERP qrcode cannot be found."
FAIL_OBJECT = "OpenERP object cannot be found."
SUCCESS = "success"
FAIL = "fail"
   
""" Successful imported document. """            
class bss_success(osv.osv):

    _name = 'bss_qrcode.success'
    _description = "Successfully imported files"
    _rec_name = 'qrcode_id'
   
    _columns = {
        'import_id': fields.many2one('bss_qrcode.import', string="Imported date", ondelete='cascade', required=True, readonly=True),
        'qrcode_id': fields.many2one('bss_qrcode.qrcode', string='File', required=True),
        'document': fields.binary('Document'),
        'qrcode_create_date': fields.related('qrcode_id', 'create_date', type='date', string='First downloaded date', store=False),
        'oe_version': fields.related('qrcode_id', 'oe_version', type='char', string='Version', store=False),
        'oe_object': fields.related('qrcode_id', 'oe_object', type='char', string='Object', store=False),
        'oe_id': fields.related('qrcode_id', 'oe_id', type='char', string='Id', store=False),
        'user_id': fields.related('qrcode_id', 'user_id', type='char', string='User id', store=False),
        'report': fields.related('qrcode_id', 'report', type='char', string='Report', store=False),
        'filename': fields.related('qrcode_id', 'filename', type='char', string='Filename', store=False),
    }

bss_success()

""" Failed imported document for any reason (id not found, report not found, etc). """           
class bss_fail(osv.osv):

    _name = 'bss_qrcode.fail'
    _description = "Failed imported files"
   
    _columns = {
        'import_id': fields.many2one('bss_qrcode.import', string="Import", ondelete='cascade', required=True, readonly=True),
        'qrcode_id': fields.many2one('bss_qrcode.qrcode', string='QR Code', required=True),
        'document': fields.binary('Document'),
        'reason': fields.char('Reason'),
        'qrcode_create_date': fields.related('qrcode_id', 'create_date', type='date', string='First downloaded date', store=False),
        'oe_version': fields.related('qrcode_id', 'oe_version', type='char', string='Version', store=False),
        'oe_object': fields.related('qrcode_id', 'oe_object', type='char', string='Object', store=False),
        'oe_id': fields.related('qrcode_id', 'oe_id', type='char', string='Id', store=False),
        'user_id': fields.related('qrcode_id', 'user_id', type='char', string='User id', store=False),
        'report': fields.related('qrcode_id', 'report', type='char', string='Report', store=False),
        'filename': fields.related('qrcode_id', 'filename', type='char', string='Filename', store=False),
    }
    
bss_fail()

""" Imported document where QR Code was not found. """               
class bss_qrcode_not_found(osv.osv):

    _name = 'bss_qrcode.qrcode_not_found'
    _description = "Imported files where QR Code were not found"
   
    _columns = {
        'import_id': fields.many2one('bss_qrcode.import', string="Import", ondelete='cascade', required=True, readonly=True),
        'document': fields.binary('Document')
    }

bss_qrcode_not_found()

""" Class which contains all imported files of an xmlrpc call. """
class bss_import(osv.osv):
    
    _name = 'bss_qrcode.import'
    _description = "Imported files by xmlrpc"
    _rec_name = 'create_date'
   
    _columns = {
        'create_date' : fields.datetime('Date created', readonly=True),
        'identifier': fields.char('Identifier from java'),
        'success_ids': fields.one2many('bss_qrcode.success', 'import_id', string='Succeed imported documents'),
        'fail_ids': fields.one2many('bss_qrcode.fail', 'import_id', string='Failed imported documents'),
        'qrcode_not_found_ids': fields.one2many('bss_qrcode.qrcode_not_found', 'import_id', string='QR Code not found'),
        'status': fields.selection([('success','Success'), ('fail','Fail')], 'Status', required=True),
        'terminated': fields.boolean('Terminated'),    
    }
    
    """ Set the import status to fail. """
    def set_status_to_fail(self, cr, uid, ids, myimport):
        myimport.write({'status': FAIL})
        
    """ Add the document to the correct column (i.e success, fail or qrcode_not_found).  """
    def add_document_to_column(self, cr, uid, myimport, qrcode_id, document):        
        # 1. The QR Code is not found
        if qrcode_id == 0:
            row_id = self.pool.get('bss_qrcode.qrcode_not_found').create(cr, uid, {
               'import_id': myimport.id, 
               'document': document
            })
            myimport.set_status_to_fail(myimport)
        else:
            qrcode = self.pool.get('bss_qrcode.qrcode').read(cr, uid, qrcode_id)
        
            # 2. The OpenERP QRCode dont'exist
            if(qrcode is None):
                row_id = self.pool.get('bss_qrcode.fail').create(cr, uid, {
                   'import_id': myimport.id, 
                   'qrcode_id': qrcode_id, 
                   'document': document,
                   'reason': FAIL_QRCODE
                })
                myimport.set_status_to_fail(myimport)
            else:
                myobject = self.pool.get(qrcode['oe_object']).read(cr, uid, qrcode['oe_id'])
                
                # 3. The specific OpenERP object don't exist
                if(myobject is None):
                    row_id = self.pool.get('bss_qrcode.fail').create(cr, uid, {
                       'import_id': myimport.id, 
                       'qrcode_id': qrcode_id, 
                       'document': document,
                       'reason': FAIL_OBJECT
                    })
                    myimport.set_status_to_fail(myimport)
                # 4. The document doesn't have any problem  
                else:
                    row_id = self.pool.get('bss_qrcode.success').create(cr, uid, {
                       'import_id': myimport.id, 
                       'qrcode_id': qrcode_id, 
                       'document':  document,
                    })
                    self.pool.get('bss_qrcode.qrcode').attach_file(cr, uid, qrcode['id'], document)
            
        return row_id
        
    """ Function called by an xmlrpc connection. Create an import object with documents. """
    def add_to_import_object(self, cr, uid, java_identifier, qrcode_id, document):
        import_id = self.search(cr, uid, [('identifier', '=', java_identifier)])
        
        # If the import object already exists then use it, create it else
        if import_id:
            myimport = self.read(cr, uid, import_id[0])
            # In order to have a dictionary and not an array
            myimport = self.browse(cr, uid, myimport['id'])
        else:
            myimport_id = self.create(cr, uid, {'identifier': java_identifier, 'status': SUCCESS})
            myimport = self.browse(cr, uid, myimport_id)
        
        # Add the document to the correct column
        row_id = self.add_document_to_column(cr, uid, myimport, qrcode_id, document)
        
        return row_id 
                 
bss_import()
