# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp.osv import osv, orm
from openerp.tools.translate import _


class HrPayslip(osv.Model):

    _inherit = 'hr.payslip'

    def hr_verify_sheet(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            if not payroll.employee_id.address_home_id:
                raise orm.except_orm(
                    _('Warning'), _('This employee don´t have a home address'))
        return super(HrPayslip, self).hr_verify_sheet(cr, uid, ids)
