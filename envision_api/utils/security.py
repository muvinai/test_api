from passlib.context import CryptContext
from bson import ObjectId
from datetime import datetime, timedelta
import jwt
import json

from config.constants import JWT_SECRET
from exceptions.auth_exceptions import InvalidToken, ExpiredToken

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class Encoder(json.JSONEncoder):
    def default(self, x):
        if isinstance(x, (ObjectId, datetime)):
            return str(x)
        else:
            return super().default(x)


def encode(payload: dict) -> str:
    payload['iat'] = datetime.utcnow()
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256', json_encoder=Encoder)


def decode(token: str, expiration_delta: timedelta = 0) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms='HS256')
    except jwt.exceptions.PyJWTError:
        raise InvalidToken()

    if expiration_delta:
        validate_expiration(payload.get('iat'), expiration_delta)

    return payload


def validate_expiration(iat: int, expiration_delta: timedelta):
    if not iat or datetime.utcfromtimestamp(iat) + expiration_delta < datetime.utcnow():
        raise ExpiredToken()
