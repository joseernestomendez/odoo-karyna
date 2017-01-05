import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, exceptions, _



class DriversOrderLineExtension(models.Model):
    _name = 'drivers.order.line'
    _inherit = 'drivers.order.line'

    #Production d efinitive
    # prod_qty = rend sac * sac
    # prod_diff = prod_qty - order_total
    # prod_sac Flotante

    # Sugestion
    # Rend / Sac
    # Sacs
    name = fields.Char(string="name", required=False, )
    prod_qty = fields.Float(string="Qty",  required=False, readonly=False)
    prod_diff = fields.Float(string="Diff",  required=False, readonly=False )
    prod_sacs = fields.Float(string="Sacs",  required=False, )
    whitespace_field1 = fields.Char(string="", required=False, readonly=True)
    whitespace_field2 = fields.Char(string="", required=False, readonly=True)


    @api.onchange('prod_sacs')
    def _compute_prod_qty(self):
        self.prod_qty = (self.yield_sack * self.prod_sacs)
        self.prod_diff = (self.prod_qty - self.order_total)

    @api.onchange('order_total')
    def _compute_prod_diff(self):
        #self.prod_qty = (self.yield_sack * self.prod_sacs)
        self.prod_diff = (self.prod_qty - self.order_total)
    #
    # @api.depends('prod_sac')
    # @api.onchange('prod_qty')
    # def _create_order_line(self):
    #     import pdb; pdb.set_trace()
    #     line_obj = self.env['sale.order.line']
    #     for order in self:
    #         line_obj.write(order.line_id.id,
    #                        {'product_uom_qty': order.prod_qty})





