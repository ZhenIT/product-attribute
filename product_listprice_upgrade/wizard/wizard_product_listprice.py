##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import pooler
from osv import osv, fields


class wizard_product_pricelist(osv.osv_memory):
    _name = "wizard.product.pricelist"

    _columns = {
              'pricelist':fields.many2one('product.pricelist', string=''),
              'product_category':fields.many2many('product.category', string=''),
              }
    def _get_pricelist(self, cr, uid, context):
        pricelist_obj = pooler.get_pool(cr.dbname).get('product.pricelist')
        ids = pricelist_obj.search(cr, uid, [('type', '=', 'internal'), ])
        pricelists = pricelist_obj.browse(cr, uid, ids)
        return [(pricelist.id, pricelist.name) for pricelist in pricelists]

    def upgrade_listprice(self, cr, uid, ids, context):
        self.update_products = 0
        categories = self.browse(cr, uid, ids[0]).product_category
        pricelist_obj = pooler.get_pool(cr.dbname).get('product.pricelist')
        cat_obj = pooler.get_pool(cr.dbname).get('product.category')
        product_obj = pooler.get_pool(cr.dbname).get('product.product')
        pricelist_id = self.browse(cr, uid, ids[0]).pricelist.id

        def _upgrade(category_id):
            child_ids = cat_obj.search(
                    cr, uid, [('parent_id', '=', category_id), ]
                )
            for child_id in child_ids:
                _upgrade(child_id)

            product_ids = product_obj.search(
                cr, uid, [('categ_id', '=', category_id), ]
            )
            for product_id in product_ids:
                list_price = pricelist_obj.price_get(
                    cr, uid, [pricelist_id], product_id, 1
                )
                product_obj.write(
                    cr, uid, [product_id], {
                        'list_price': list_price[pricelist_id]
                    }
                )
                self.update_products += 1

        for category in categories:
            _upgrade(category.id)

        return {'update_products': self.update_products}


wizard_product_pricelist()
