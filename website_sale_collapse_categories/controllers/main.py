# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import http
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):
    @http.route(
        ['/shop',
         '/shop/page/<int:page>',
         '/shop/category/<model("product.public.category"):category>',
         '/shop/category/<model("product.public.category"):category>/'
         'page/<int:page>'],
        type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        def recursive_category(category, parent_category=None):
            if parent_category is None:
                parent_category = []
            parent_category.append(category.id)
            if category.parent_id:
                recursive_category(category.parent_id, parent_category)
            return parent_category

        response = super(WebsiteSale, self).shop(
            page=page, category=category, search=search, **post)
        response.qcontext['parent_category'] = (
            recursive_category(category) if category else [])
        return response
