# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
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
from openerp import http, fields
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_event_register_free.\
    controllers.website_event import WebsiteEvent


class WebsiteSale(website_sale):
    mandatory_free_registration_fields = ["name", "phone", "email"]
    # TODO: Not used yet
    optional_free_registration_fields = ["street", "city", "country_id", "zip"]

    def checkout_form_validate(self, data):
        errors = dict()
        if request.session.get('free_tickets'):
            # Make validation for free tickets
            for field_name in self.mandatory_free_registration_fields:
                if not data.get(field_name, '').strip():
                    errors[field_name] = 'missing'
                elif not WebsiteEvent()._validate(field_name, data, True):
                    # Patch for current free registration implementation
                    errors[field_name] = 'error'
        if request.session.get('has_paid_tickets'):
            # Make validation for paid tickets
            errors.update(super(WebsiteSale, self).checkout_form_validate(
                data))
        return errors

    def _prepare_event_registration(self, session, post):
        return {
            'origin': 'Website',
            'nb_register': int(session['free_tickets']),
            'event_id': session['event_id'],
            'date_open': fields.Datetime.now(),
            'email': post['email'],
            'phone': post['phone'],
            'name': post['name']
        }

    @http.route(['/shop/confirm_order'], type='http', auth="public",
                website=True)
    def confirm_order(self, **post):
        if request.session.get('free_tickets'):
            values = self.checkout_values(post)
            values['error'] = self.checkout_form_validate(post)
            if values["error"]:
                return request.website.render("website_sale.checkout", values)
            registration = request.env['event.registration'].sudo().create(
                self._prepare_event_registration(request.session, post))
            registration.registration_open()
        if request.session.get('has_paid_tickets'):
            return super(WebsiteSale, self).confirm_order(**post)
        else:
            return http.request.render(
                'website_event_register_free.partner_register_confirm',
                {'registration': registration})
