# -*- coding: utf-8 -*-
import json
from odoo import http

BASE_URL = '/openacademy/openacademy'


class Openacademy(http.Controller):

    @http.route('%s/objects/' % BASE_URL, auth='public')
    def list(self, **kw):
        obj = http.request.env['openacademy.openacademy'].search([])
        data = obj.read(
            ['first_name', 'last_name', 'value', 'description']
        )
        return self.__jsonResponse(data, 200)

    @http.route(
        '%s/objects/<model("openacademy.openacademy"):obj>/' % BASE_URL,
        auth='public')
    def object(self, obj, **kw):
        data = obj.read(
            ['first_name', 'last_name', 'value', 'description']
        )[0]
        return self.__jsonResponse(data, 200)

    def __jsonResponse(self, data, status):
        return http.Response(
            json.dumps(data),
            content_type='application/json;charset=utf-8',
            status=status)
