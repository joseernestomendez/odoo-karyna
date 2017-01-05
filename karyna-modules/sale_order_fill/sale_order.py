#-*- coding: utf-8-*-
from openerp import api, _
from openerp.osv import orm, fields,osv
import pdb
from datetime import datetime, timedelta
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class res_partner(orm.Model):
    _inherit = 'res.partner'
    
    _columns = {
        'is_driver': fields.boolean("it's a Driver?"),
         'driver': fields.selection([('driver1','Driver 1'),('driver2','Driver 2'),
                                     ('driver3','Driver 3'),('driver4','Driver 4'),
                                     ('driver5','Driver 5'),('driver6','Driver 6'),
                                     ('driver7','Driver 7'),('driver8','Driver 8'),
                                     ('driver9','Driver 9'),('driver10','Driver 10'),
                                     ('driver11','Driver 11'),('driver12','Driver 12'),
                                     ('driver13','Driver 13'),('driver14','Driver 14'),
                                     ('driver15','Driver 15'),('driver16','Driver 16'),
                                     ('driver17','Driver 17'),('driver18','Driver 18')],'Driver'),
    }

    _sql_constraints = {('driver_uniq', 'unique(driver)', 'This driver is alredy assigned. Cannot select same driver twice.')}
    
class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    def _prepare_picking_assign(self, cr, uid, move, context=None):
        """ Prepares a new picking for this move as it could not be assigned to
        another picking. This method is designed to be inherited.
        """
        values = {
            'origin': move.origin,
            'company_id': move.company_id and move.company_id.id or False,
            'move_type': move.group_id and move.group_id.move_type or 'direct',
            'partner_id': move.partner_id.id or False,
            'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
            }
        return values
    
    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        """Assign a picking on the given move_ids, which is a list of move supposed to share the same procurement_group, location_from and location_to
        (and company). Those attributes are also given as parameters.
        """
        pick_obj = self.pool.get("stock.picking")
        drivers = map(lambda x:x.partner_id.id, self.browse(cr, uid, move_ids, context=context))
        # Use a SQL query as doing with the ORM will split it in different queries with id IN (,,)
        # In the next version, the locations on the picking should be stored again.
        query = """
            SELECT stock_picking.id FROM stock_picking, stock_move
            WHERE
                stock_picking.state in ('draft', 'confirmed', 'waiting') AND
                stock_move.picking_id = stock_picking.id AND
                stock_move.location_id = %s AND
                stock_move.location_dest_id = %s AND
                stock_move.partner_id in %s AND
        """
        params = (location_from, location_to, (tuple(drivers),))
        if not procurement_group:
            query += "stock_picking.group_id IS NULL LIMIT 1"
        else:
            query += "stock_picking.group_id = %s LIMIT 1"
            params += (procurement_group,)
        cr.execute(query, params)
        [pick] = cr.fetchone() or [None]
        if not pick:
            #pick_obj = self.pool.get("stock.picking")
            move = self.browse(cr, uid, move_ids, context=context)[0]
            values = self._prepare_picking_assign(cr, uid, move, context=context)
            pick = pick_obj.create(cr, uid, values, context=context)
        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
        
class SaleOrder(orm.Model):

    _inherit = 'sale.order'
    _auto = True
    
    def copy(self, cr, uid, id, default=None, context=None, done_list=None, local=False):
        default = {} if default is None else default.copy()
        driver_obj = self.pool.get('drivers.order.line')
        drivers = []
        driver_dict = {}
        for i in range(1,19):
            driver_dict.update({'driver_'+str(i):0.0})
        driver_dict['procurement_ids'] = [(6, 0, [])]
        driver_dict['order_total'] = 0.0
        for driver in self.browse(cr, uid, id, context=context).drivers_order_ids:
            driver_obj.write(cr, uid, driver.id, driver_dict)
            drivers.append(driver.id)
    
        default['drivers_order_ids'] = [(6, 0, drivers)]
        return super(SaleOrder, self).copy(cr, uid, id, default, context=context)
    
    def fill_sale_order(self, cr, uid, ids, context=None):
        """Pass the order id to a wizard to retrieve a list of
        product categories for setting a default list of products."""
        action_obj = self.pool.get('ir.actions.act_window')
        view_obj = self.pool.get('ir.ui.view')
        #Defensive programming.
        if len(ids) > 1:
            raise orm.except_orm("ERROR","You tried to pass more than one order.")
        action_id = action_obj.search(cr, uid, [('name','=','Fill Sale Products'),
                                      ('res_model','=','sale.order.fill')],
                                      limit=1, context=context)
        view_id = view_obj.search(cr, uid, [('name','=','sale.order.fill.view'),
                                  ('model','=','sale.order.fill')], limit=1,
                                  context=context)
        try:
            action_content = action_obj.read(cr, uid, action_id,
                                             context=context)[0]
            action_content.update({'views': [(view_id[0], 'form')]})
            return action_content
        except IndexError:
            raise orm.except_orm('ERROR',
                                 """One or both of the following elements are missing:
                                 Action: Fill Sale Products
                                 View: sale.order.fill.view
                                 Please Update module.""")

    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        location_id = order.partner_shipping_id.property_stock_customer.id
        
        if context.get('driver'):
            date_planned = datetime.strptime(order.date_order, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=line.line_id.delay or 0.0)
            return {
                'name': line.line_id.name,
                'origin': order.name,
                'route_ids' : line.line_id.route_id and [(4, line.line_id.route_id.id)] or [],
                'location_id': location_id,
                'partner_dest_id' : context.get('driver'),
                'warehouse_id' :order.warehouse_id and order.warehouse_id.id or False,
                'date_planned': date_planned,
                'product_id': line.product_id.id,
                'product_qty': context['qty'] or 0.0,
                'product_uom': line.line_id.product_uom.id,
                'product_uos_qty': (line.line_id.product_uos and line.line_id.product_uos_qty) or line.line_id.product_uom_qty,
                'product_uos': (line.line_id.product_uos and line.line_id.product_uos.id) or line.line_id.product_uom.id,
                'company_id': order.company_id.id,
                'group_id': group_id,
                'invoice_state': (order.order_policy == 'picking') and '2binvoiced' or 'none',
                'sale_line_id': line.line_id.id,
                'driver_line_id':line.id
                
            }
        return {}
        
    def action_ship_create(self, cr, uid, ids, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        :return: True
        """
        context = dict(context or {})
        context['lang'] = self.pool['res.users'].browse(cr, uid, uid).lang
        procurement_obj = self.pool.get('procurement.order')
        sale_line_obj = self.pool.get('sale.order.line')
        driver_line_obj = self.pool.get('drivers.order.line')
        driver_obj = self.pool.get('res.partner')
        new_group_id = []
        for order in self.browse(cr, uid, ids, context=context):
            proc_ids = []
            vals = self._prepare_procurement_group(cr, uid, order, context=context)
            if not order.procurement_group_id:
                #import pdb; pdb.set_trace()
                group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                new_group_id.append(group_id)
                order.write({'procurement_group_id': group_id})

            for line in order.drivers_order_ids:
                
                #Try to fix exception procurement (possible when after a shipping exception the user choose to recreate)
                if line.procurement_ids:
                    #first check them to see if they are in exception or not (one of the related moves is cancelled)
                    procurement_obj.check(cr, uid, [x.id for x in line.procurement_ids if x.state not in ['cancel', 'done']])
                    line.refresh()
                    #run again procurement that are in exception in order to trigger another move
                    except_proc_ids = [x.id for x in line.procurement_ids if x.state in ('exception', 'cancel')]
                    procurement_obj.reset_to_confirmed(cr, uid, except_proc_ids, context=context)
                    proc_ids += except_proc_ids
                else:
                    if not line.product_id:
                        continue
                    ctx = context.copy()
                    for i in range(1,19):
                        proc_id = False
                        if eval('line.driver_'+str(i)) > 0:
                            driver = driver_obj.search(cr, uid, [('driver','=','driver'+str(i))])
                            if not driver:
                                raise osv.except_osv(_('Warning!'), _('Please define a partner as %s before confirming the order.'%('driver'+str(i))))
                        
                            ctx['driver'] = driver[0]
                            ctx['qty'] = eval('line.driver_'+str(i))
                            vals = self._prepare_order_line_procurement(cr, uid, order, line, group_id=order.procurement_group_id.id, context=ctx)
                            ctx['procurement_autorun_defer'] = True
                            self.pool.get("procurement.group").write(cr, uid, group_id, {'partner_id':ctx['driver']}, context=context)
                            proc_id = procurement_obj.create(cr, uid, vals, context=ctx)
                            proc_ids.append(proc_id)
                            procurement_obj.run(cr, uid, [proc_id], context=ctx)
                        self.pool.get("procurement.group").write(cr, uid, group_id, {'partner_id': order.partner_shipping_id.id}, context=context)
                        
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
                order.write(val)

        #procs = procurement_obj.browse(cr, uid, ids, context)
        #import pdb; pdb.set_trace()
        procs_ids = procurement_obj.search(cr, uid, [('group_id', '=', group_id), ('rule_id', '=', 16),
                                                     ('state', '=', 'running'), ('merged', '=', False),
                                                     ('from_merged', '=', False)])
        for elem in procs_ids:
            procs = procurement_obj.browse(cr, uid, elem, context)
            pids = procurement_obj.search(cr, uid, [('group_id', '=', group_id),
                                                    ('rule_id', '=', 16), ('product_id', '=', procs.product_id.id),
                                                    ('state', '=', 'running'), ('merged', '=', False),
                                                    ('from_merged', '=', False)])
            #self.pool.get('mrp.production').cancel(cr, uid, elem, context)
            if pids:
                procurement_obj.do_merge(cr, uid, pids, context)

        '''
        new_proc_ids = procurement_obj.search(cr, uid, [('group_id', '=', group_id), ('rule_id', '=', 13),
                                                     ('invoice_state', '=', '2binvoiced')])
        if new_proc_ids:
            for proc in new_proc_ids:
                procurement_obj.reset_to_confirmed(cr, uid, [proc], context)
                procurement_obj.run(cr, uid, [proc], context)
        '''
        return True

    def _get_shipped(self, cr, uid, ids, name, args, context=None):
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            group = sale.procurement_group_id
            if group:
                res[sale.id] = all([proc.state in ['cancel', 'done'] for proc in group.procurement_ids])
            else:
                res[sale.id] = False
        return res
    
    def _get_orders_procurements(self, cr, uid, ids, context=None):
        res = set()
        for proc in self.pool.get('procurement.order').browse(cr, uid, ids, context=context):
            if proc.state =='done' and proc.driver_line_id:
                res.add(proc.driver_line_id.sale_order.id)
        return list(res)
    
    _columns = {
        'drivers_order_ids': fields.one2many('drivers.order.line', 'sale_order',
                                          'Sales Agent'),
        'shipped': fields.function(_get_shipped, string='Delivered', type='boolean', store={
                'procurement.order': (_get_orders_procurements, ['state'], 10)
            }),
    }
