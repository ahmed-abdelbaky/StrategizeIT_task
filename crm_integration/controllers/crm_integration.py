import ast
import json
from pickle import FALSE
import logging

from odoo import http, _, SUPERUSER_ID
from odoo.api import returns
from odoo.http import Controller, request, route, Response
from odoo.exceptions import AccessDenied, ValidationError, UserError

from passlib.context import CryptContext
from ..tools.jwt_token import create_access_token, validate_token, get_user_id

_logger = logging.getLogger(__name__)


class CrmIntegration(http.Controller):

    @route('/v1/customer/auth', auth='none', type="json", methods=["POST"], csrf=False)
    def authenticate(self):
        """ Authenticate
            Request
                body
                {"userName": "user","password": "password"}
            Response
                http status
                200             ok -> get access token, timeStamp of access token, refresh token
                422             Incorrect credentials(login,password) of user
                403             Unauthorized User
        """
        data = request.httprequest.data.decode('utf-8')
        data = ast.literal_eval(data)
        if not ("userName" in data and "password" in data and data['userName'] and data['password']):
            _logger.info("You must send userName and password")
            return {"error_msg": "You must send userName and password "}
        login = 'userName' in data and str(data['userName'])
        password = 'password' in data and str(data['password'])

        user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        ctx = CryptContext(['pbkdf2_sha512', 'plaintext'], deprecated=['plaintext'])
        if user:
            request.env.cr.execute(
                "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                [user.id]
            )
            [hashed] = request.env.cr.fetchone()

            valid, replacement = ctx \
                .verify_and_update(password, hashed)
        else:
            return {"error_message": "User is not found may be archived or deleted"}

        if not valid:
            return {"error_message": "Invalid password"}

        access_token, exp_time = create_access_token(user)
        return {'accessToken': access_token, 'timeStamp': str(exp_time), "status_code": 200}

    @http.route('/v1/customer/create', type='json', methods=['POST'], auth='none', csrf=False)
    @validate_token
    def insert_customer_data(self, **post):
        # print("Api Test ")
        args = request.httprequest.data.decode('utf-8')
        vals = json.loads(args)
        error = self._check_data(vals)
        if error:
            _logger.info(error)
            return {
                "error_message": error
            }
        user = get_user_id()
        try:
            res = request.env['res.partner'].sudo().with_user(user.id).create(vals)
            if res:
                _logger.info("Create New Partner Successfully")
            return {
                "message": "Create New Partner Successfully", "res_id": res.id
            }
        except Exception as Error:
            _logger.info(str(Error))
            return {
                'error_message': Error
            }

    @http.route('/v1/customer/update/<string:customer_id>', type='json', methods=['PUT'], auth='none', csrf=False)
    @validate_token
    def update_customer_data(self, customer_id, **post):
        # print("Api Test ")
        customer_id = customer_id and int(customer_id)
        args = request.httprequest.data.decode('utf-8')
        vals = json.loads(args)
        if not vals:
            return {"error_message": "Please enter valid data"}
        customer = request.env['res.partner'].sudo().browse(customer_id)
        if not customer:
            return {"error_message": "Customer Not Found"}
        user = get_user_id()
        try:
            customer.sudo().with_user(user.id).write(vals)
            _logger.info("Update Successfully")
            return {
                "message": "Update Successfully", "res_id": customer.id
            }
        except Exception as rrr_msg:
            _logger.info(str(rrr_msg))
            return {
                'error_message': f"Error At Update {rrr_msg}"
            }

    @http.route("/v1/customer/write/<string:partner_id>", auth='none', type="json", methods=["GET"], csrf=False)
    @validate_token
    def get_partner(self, partner_id):
        try:
            partner_id = partner_id and int(partner_id)
            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner:
                return {
                    "error_message": f"No Partner has this is id {partner_id}", "res_id": partner_id
                }
            return {
                'id': partner_id,
                'name': partner.name,
                'phone': partner.phone
            }
        except Exception as Error:
            return {
                "error_message": Error
            }

    @http.route("/v1/customer/Delete/<int:partner_id>", auth='none', type="json", methods=["DELETE"], csrf=False)
    @validate_token
    def delete_partner(self, partner_id):
        try:
            partner_id = partner_id and int(partner_id)
            user = get_user_id()
            partner = request.env['res.partner'].with_user(user.id).browse(partner_id)

            if not  partner:
                return {
                    'message_error': f"No Partner Has this id{partner_id}"
                }
            partner.with_user(user.id).unlink()
            return {
                'message': f"Partner Has Deleted"
            }
        except Exception as Error:
            return {
                'message_error': Error
            }

    def _check_data(self, vals):
        if not vals.get('name'):
            error = "partner name must be enter"
            return error
        if not isinstance(vals.get('name'), str):
            error = "partner name must be Character"
            return error
        if not isinstance(vals.get('email'), str):
            error = "partner email must be Character"
            return error
        if not isinstance(vals.get('phone'), str):
            error = "partner Phone must be Character"
            return error
        if not isinstance(vals.get('street'), str):
            error = " street must be Character"
            return error
        if not isinstance(vals.get('street2'), str):
            error = " Street2 must be Character"
            return error
        if not isinstance(vals.get('city'), str):
            error = "City Name must be Character"
            return error
