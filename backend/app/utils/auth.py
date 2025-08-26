from functools import wraps
from flask import request, g
from app.utils.jwt_utils import decode_token
from app.utils import api_logger as logger
from app.utils.response import ResponseHelper


def has_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        # Get token from header
        if auth_header:
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            # pass the request to the next function
            return f(*args, **kwargs)

        # Decode token
        payload = decode_token(token)
        if not payload:
            logger.warning("Token is invalid")
            return ResponseHelper.unauthorized("Invalid or expired token")

        # Store user info in Flask's g object for use in the route
        g.user_id = payload["sub"]
        g.is_admin = payload.get("admin", False)
        g.username = payload.get("username")

        return f(*args, **kwargs)

    return decorated


def token_required(f):
    """Decorator to require a valid JWT token for API access"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        # Get token from header
        if auth_header:
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            logger.warning("Token is missing")
            return ResponseHelper.unauthorized("Authentication token is missing")

        # Decode token
        payload = decode_token(token)
        if not payload:
            logger.warning("Token is invalid")
            return ResponseHelper.unauthorized("Invalid or expired token")

        # Store user info in Flask's g object for use in the route
        g.user_id = payload["sub"]
        g.is_admin = payload.get("admin", False)
        g.username = payload.get("username")

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Decorator to require admin privileges"""

    @wraps(f)
    def decorated(*args, **kwargs):
        # First verify the token
        token_result = token_required(lambda: None)()
        if isinstance(token_result, tuple):  # Error response
            return token_result

        # Now check admin status
        if not g.is_admin:
            logger.warning(f"User {g.user_id} attempted to access admin-only resource")
            return ResponseHelper.forbidden("Admin privileges required")

        return f(*args, **kwargs)

    return decorated


def user_matches_or_admin(f):
    """Decorator to require that the authenticated user matches the requested user ID or is an admin"""

    @wraps(f)
    def decorated(*args, **kwargs):
        # First verify the token
        token_result = token_required(lambda: None)()
        if isinstance(token_result, tuple):  # Error response
            return token_result

        # Check if user ID in route matches authenticated user, or if user is admin
        user_id = kwargs.get("user_id")
        if user_id is None:
            logger.error(
                "user_matches_or_admin decorator used on route without user_id parameter"
            )
            return ResponseHelper.internal_server_error("Internal server error")

        if g.user_id != user_id and not g.is_admin:
            logger.warning(
                f"User {g.user_id} attempted to access data of user {user_id}"
            )
            return ResponseHelper.forbidden(
                "You do not have permission to access this resource"
            )

        return f(*args, **kwargs)

    return decorated
