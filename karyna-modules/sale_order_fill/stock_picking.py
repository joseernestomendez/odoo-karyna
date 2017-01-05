#-*- coding: utf-8 -*-
from openerp.osv import osv, orm, fields


class stock_picking(osv.osv):
    """Class description"""

    _inherit = 'stock.picking'

    def _get_partner_to_invoice(self, cr, uid, picking, context=None):
        """ Inherit the original function of the 'stock' module
            We select the partner of the sales order as the partner of the customer invoice
        """
        if picking.sale_id:
            saleorder_ids = self.pool['sale.order'].search(cr, uid, [('procurement_group_id' ,'=', picking.group_id.id)], context=context)
            saleorders = self.pool['sale.order'].browse(cr, uid, saleorder_ids, context=context)
            if saleorders and saleorders[0] and saleorders[0].order_policy == 'picking' \
                    and (not saleorders.drivers_order_ids):
                saleorder = saleorders[0]
                return saleorder.partner_invoice_id.id
        return super(stock_picking, self)._get_partner_to_invoice(cr, uid, picking, context=context)