# -*- coding: utf-8 -*-
import jwt
import pytz
from datetime import datetime, timedelta
from odoo.http import request
import functools
from odoo.exceptions import AccessDenied
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
import logging
_logger = logging.getLogger(__name__)


access_token_info = {
    "minutes": 30,
    "algorithm": "HS256",
    "secret": "fb3561ae-4aa0-4ddf-b561-ae4aa08ddf3e",
}


def create_access_token(user):
    """Create Token Using jwt
    :param user indicate the user object
    return token which created
    """
    try:
        exp = datetime.utcnow() + timedelta(minutes=access_token_info.get("minutes") or 30)
        payload = {'exp': exp, 'id': user.id}
        encoded = jwt.encode(payload, key=access_token_info.get("secret"), algorithm=access_token_info.get("algorithm"))
        expiration_date = datetime.now().astimezone(pytz.timezone(user.tz)) + timedelta(minutes=30)
        return encoded, expiration_date
    except (jwt.exceptions.InvalidKeyError, jwt.exceptions.InvalidAlgorithmError):
        _logger.info("Can not create access token")
        return{"with_user":"Can not create access token"}


def get_user_id():
    headers = dict(request.httprequest.headers.items())
    token = headers.get('Authorization')
    token = token.split()[1]
    token_info = jwt.decode(token, key=access_token_info.get("secret"),
                            algorithms=access_token_info.get("algorithm"))
    return request.env['res.users'].sudo().search([('id', '=', token_info['id'])])


def validate_token(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        headers = dict(request.httprequest.headers.items())
        token = headers.get('Authorization')
        if isinstance(token, str):
            try:
                token = token.split()[1]
                token_info = jwt.decode(token, key=access_token_info.get("secret"),
                                        algorithms=access_token_info.get("algorithm"))
                if token_info.get('id'):
                    user = request.env['res.users'].sudo().search([('id', '=', token_info['id'])])
                    if user:
                        return func(*args, **kwargs)
                    else:
                        _logger.info("Access Denied")
                        return {"error_message": "Access Denied"}
                else:
                    _logger.info("Signature verification failed")
                    return {"error_message": "Signature verification failed"}
            except ExpiredSignatureError as exp_sign:
                _logger.info(f"Error At Token {str(exp_sign)}")
                return {"error_message": f"Error At Token {str(exp_sign)}"}

            except InvalidTokenError as invalid_sign:
                _logger.info( f"Error At Token {str(invalid_sign)}")
                return {"error_message": f"Error At Token {str(invalid_sign)}"}

        else:
            _logger.info("Invalid Token")
            return {"error_message": "Invalid Token"}

    return inner
