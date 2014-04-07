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
SUCCESS_MSG = "The document is successfully added."
FAIL_QRCODE_MSG = "OpenERP QR Code cannot be found."
FAIL_OBJECT_MSG = "OpenERP object cannot be found."
NOT_FOUND_MSG = "The QR Code cannot be found."
SUCCESS = "success"
FAIL = "fail"
NOT_FOUND = "not_found"
FILENAME_QRCODE_NOT_FOUND = "qrcode_not_found"
   
""" Imported document. """            
class bss_imported_document(osv.osv):

    _name = 'bss_qrcode.imported_document'
    _description = "Imported QR Code documented"
    _rec_name = 'qrcode_id'
   
    _columns = {
        'import_id': fields.many2one('bss_qrcode.import', string="Imported date", ondelete='cascade', required=True, readonly=True),
        'status': fields.selection([('success','Success'), ('fail','Fail'), ('not_found', 'QR Code not found')], 'Status', required=True),
        'qrcode_id': fields.many2one('bss_qrcode.qrcode', string='File'),
        'message': fields.char('Message'),
        'qrcode_create_date': fields.related('qrcode_id', 'create_date', type='char', string='First downloaded date', store=False),
        'oe_version': fields.related('qrcode_id', 'oe_version', type='char', string='Version', store=False),
        'oe_object': fields.related('qrcode_id', 'oe_object', type='char', string='Object', store=False),
        'oe_id': fields.related('qrcode_id', 'oe_id', type='char', string='Id', store=False),
        'user_id': fields.related('qrcode_id', 'user_id', type='char', string='User id', store=False),
        'report': fields.related('qrcode_id', 'report', type='char', string='Report', store=False),
        'filename': fields.related('qrcode_id', 'filename', type='char', string='Filename', store=False),
    }

bss_imported_document()

""" Class which contains all imported files of an xmlrpc call. """
class bss_import(osv.osv):
    
    _name = 'bss_qrcode.import'
    _description = "Imported files from xmlrpc"
   
    def get_nb(self, cr, uid, ids, name, arg, context=None):
        res = {}
        bss_imported_document = self.pool.get('bss_qrcode.imported_document')
        
        for import_id in ids:
            res[import_id] = bss_imported_document.search(cr, uid, [('import_id', '=', import_id), ('status', 'like', arg['status'])], count=True)

        return res
    
    _columns = {
        'create_date' : fields.datetime('Date created', readonly=True),

        'identifier': fields.char('Identifier from java'),
        'imported_document_ids': fields.one2many('bss_qrcode.imported_document', 'import_id', string='Imported documents'),
        'status': fields.selection([('success','All documents succeed'), ('fail','At least one failed document')], 'Status', required=True),
        'terminated': fields.boolean('Terminated'),  
        'success_nb': fields.function(get_nb, arg={'status': 'success'}, method=True, store=False, string="Number of successes", type="integer"),  
        'fail_nb': fields.function(get_nb, arg={'status': 'fail'}, method=True, store=False, string="Number of fails", type="integer"),  
        'not_found_nb': fields.function(get_nb, arg={'status': 'not_found'}, method=True, store=False, string="Number of not found", type="integer"),  
        'total': fields.function(get_nb, arg={'status': '%'}, method=True, store=False, string="Total", type="integer"),  
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['create_date'], context=context)
        res = []
        for record in reads:
            name = record['create_date']
            res.append((record['id'], name))
        return res
    
    """ Set the import status to fail. """
    def set_status_to_fail(self, cr, uid, ids, myimport):
        myimport.write({'status': FAIL})
        
    """ Add the document to the correct column (i.e success, fail or qrcode_not_found).  """
    def add_document_to_column(self, cr, uid, myimport, qrcode_id, document):
        qrcode = None
        
        # 1. The QR Code is not found
        if qrcode_id == 0:
            imported_document = {
                'import_id': myimport.id,
                'status': NOT_FOUND,
                'qrcode_id': qrcode_id,
                'message': NOT_FOUND_MSG,
            }
            myimport.set_status_to_fail(myimport)
        else:
            qrcode = self.pool.get('bss_qrcode.qrcode').read(cr, uid, qrcode_id)
        
            # 2. The OpenERP QRCode dont'exist
            if(qrcode is None):
                imported_document = {
                    'import_id': myimport.id,
                    'status': FAIL,
                    'qrcode_id': qrcode_id,
                    'message': FAIL_QRCODE_MSG,
                }
                myimport.set_status_to_fail(myimport)
            else:
                myobject = self.pool.get(qrcode['oe_object']).read(cr, uid, qrcode['oe_id'])
                
                # 3. The specific OpenERP object don't exist
                if(myobject is None):
                    imported_document = {
                        'import_id': myimport.id,
                        'status': FAIL,
                        'qrcode_id': qrcode_id,
                        'message': FAIL_OBJECT_MSG,
                    }
                    myimport.set_status_to_fail(myimport)
                # 4. The document doesn't have any problem  
                else:
                    imported_document = {
                        'import_id': myimport.id,
                        'status': SUCCESS,
                        'qrcode_id': qrcode_id,
                        'message': SUCCESS_MSG,
                    }
                    self.pool.get('bss_qrcode.qrcode').attach_file(cr, uid, qrcode['id'], document)
                    
        row_id = self.pool.get('bss_qrcode.imported_document').create(cr, uid, imported_document)
        
        # Filename attachment
        if qrcode is None:
            filename = FILENAME_QRCODE_NOT_FOUND
        else:
            filename = qrcode['filename']
        
        # Attach the document to the object
        ir_attachment = self.pool.get('ir.attachment')
        ir_attachment.create(cr, uid, {
            'name': filename,
            'datas_fname': filename,
            'res_model': 'bss_qrcode.imported_document',
            'res_id': row_id,
            'type': 'binary',
            'db_datas': document,
        })

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
