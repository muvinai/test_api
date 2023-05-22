from fastapi import HTTPException, status
from typing import List, Optional

from config.constants import API_KEY, ENVISION_APP_API_KEY, CURRENT_ENVIRONMENT, EnvironmentEnum
from utils.security import decode
from models.admin import RoleEnum
from exceptions.auth_exceptions import AdminNotAllowed


def verify_api_key(api_key: str):
    valid_api_keys = [API_KEY, ENVISION_APP_API_KEY]
    if CURRENT_ENVIRONMENT != EnvironmentEnum.test and api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Forbidden'
        )


def verify_role(token, allowed_roles: List[RoleEnum] = None) -> Optional[dict]:
    admin = decode(token)
    if allowed_roles is not None and admin.get('role') not in allowed_roles:
        raise AdminNotAllowed()
    return admin


def verify_credentials(*, api_key: str = None, token: str = None,
                       allowed_roles: List[RoleEnum] = None) -> Optional[dict]:
    if token:
        return verify_role(token, allowed_roles)

    verify_api_key(api_key)
