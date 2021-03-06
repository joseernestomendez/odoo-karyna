# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2012-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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

from osv import fields, osv
from openerp.tools.safe_eval import safe_eval

class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'

    _columns = {
        'check_quantity_on_invoices': fields.boolean('Check invoiced quantity',
                                                     help='Check if invoiced quantity matches received/delivered quantity.')
    }
    
    def get_default_check_quantity_on_invoices(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        return {
            'check_quantity_on_invoices': safe_eval(icp.get_param(cr, uid,
                                                                  'account.check_quantity_on_invoices',
                                                                  'False')),
        }

    def set_check_quantity_on_invoices(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        # we store the repr of the values, since the value of the parameter is a required string
        icp.set_param(cr, uid, 'account.check_quantity_on_invoices', repr(config.check_quantity_on_invoices))
