#-*- coding: utf-8-*-
from openerp.osv import osv, fields
import logging
import pdb
 
class SaleOrderFill(osv.osv_memory):
 
    _name = 'sale.order.fill'
    _auto = True
 
    _columns = {
        'product_ids': fields.many2many('product.template',
                                         'sale_order_product_rel',
                                         'order_id',
                                         'product_id', string="Products")
 
    }
 
    def fill_sale_order(self, cr, uid, ids, context=None):
        product_pool = self.pool.get('product.product')
        sale_order_line_pool = self.pool.get('sale.order.line')
        drivers_order_line_pool = self.pool.get('drivers.order.line')
        order_id = context.get('active_id')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        if not data['product_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select product(s) to generate sale order line(s)."))
        for prod in product_pool.browse(cr, uid, data['product_ids'], context=context):
            sale_order_line_values = {
                'name': prod.name,
                'product_id': prod.id,
                'product_uom_qty': 0,
                'product_uom': prod.uom_id.id,
                'price_unit': prod.list_price,
                'delay': prod.sale_delay,
                'state': 'draft',
                'order_id': context.get('active_id', False),
                #'tax_id': [(6, 0, taxes)],
                'product_packaging': False,
                #'product_packaging': packaging,
                }
            drivers_order_line_values = {
                'product_id': prod.id,
                'yield_sack': prod.yield_sack,
                'sale_order': context.get('active_id', False),
                }
            sale_order_line_pool.create(cr, uid,sale_order_line_values, context=context)
            drivers_order_line_pool.create(cr, uid, drivers_order_line_values, context=context)
        return {'type': 'ir.actions.act_window_close'}
