import os
import threading

import firebase_admin
from firebase_admin import auth, credentials

from src.api.common.exceptions import AuthenticationError
from src.api.config import settings
from src.api.utils.custom_logging import logger


class FirebaseService:
    """Manages Firebase Authentication and User Management."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "FirebaseService":
        """Singleton instance creation."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()  # noqa: SLF001
        return cls._instance

    def _initialize(self) -> None:
        """Initialize Firebase Admin SDK."""
        try:
            firebase_credentials = {
                "type": os.getenv("FIREBASE_TYPE"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
            }
            cred = credentials.Certificate(firebase_credentials)
            firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
            logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            raise

    def verify_token(self, id_token: str) -> dict:
        """Verify and decode Firebase ID token.

        Args:
            id_token (str): Firebase ID token

        Returns:
            dict: Decoded token payload

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)

            if not decoded_token.get("email_verified", False):
                raise AuthenticationError("Email not verified")
            return decoded_token  # noqa: TRY300

        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, ValueError) as e:
            logger.error(f"Token verification failed: {e}")
            raise AuthenticationError(str(e)) from e

    def get_user(self, uid: str) -> auth.UserRecord:
        """Retrieve Firebase user by UID.

        Args:
            uid (str): Firebase user ID

        Returns:
            firebase_admin.auth.UserRecord: User record
        """
        try:
            return auth.get_user(uid)
        except Exception as e:
            logger.error(f"User retrieval failed: {e}")
            raise AuthenticationError("User not found") from e
