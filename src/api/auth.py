from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.common.exceptions import AuthorizationError
from src.services.firebase_service import FirebaseService

firebase_service = FirebaseService()
security = HTTPBearer(
    description="Enter your Firebase ID token",
    scheme_name="Bearer Authentication",
    bearerFormat="JWT",
    auto_error=True,
)


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:  # noqa: B008
    """Dependency to get current authenticated user.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token

    Returns:
        dict: Decoded user token
    """
    token = credentials.credentials
    return firebase_service.verify_token(token)


def require_role(required_role: str) -> dict:
    """Create a dependency for role-based access control.

    Args:
        required_role (str): Required role for access

    Returns:
        Callable: Dependency function
    """

    def role_checker(user_data: dict) -> dict:
        user_roles = user_data.get("roles", [])
        if required_role not in user_roles:
            raise AuthorizationError(f"Requires {required_role} role")
        return user_data

    return Depends(lambda: role_checker(Depends(get_current_user)))
