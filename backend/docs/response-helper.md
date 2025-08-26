# ResponseHelper Documentation

## Overview

ResponseHelper adalah class dengan static methods yang menyediakan format response API yang konsisten untuk semua endpoint dalam aplikasi Flask.

## Features

-   ✅ **Konsisten**: Semua response menggunakan format yang sama
-   ✅ **Type Safe**: Menggunakan dataclass untuk structure yang jelas
-   ✅ **Flexible**: Support untuk berbagai jenis response (success, error, paginated, dll)
-   ✅ **Easy to Use**: Static methods yang mudah dipanggil dari controller
-   ✅ **Backward Compatible**: Function aliases untuk kompatibilitas dengan kode lama

## Response Structure

### Success Response

```json
{
    "message": "Success message",
    "error": false,
    "data": {...},
    "meta": {...} // optional
}
```

### Error Response

```json
{
    "message": "Error message",
    "error": true,
    "error_code": "ERROR_CODE", // optional
    "details": {...} // optional
}
```

### Paginated Response

```json
{
    "message": "Data retrieved successfully",
    "error": false,
    "data": [...],
    "meta": {
        "pagination": {
            "page": 1,
            "limit": 10,
            "total": 100,
            "pages": 10,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

## Static Methods

### ResponseHelper.success()

Create success response with optional data and metadata.

```python
from app.utils.response import ResponseHelper

# Basic success
resp, code = ResponseHelper.success(message="User created")

# Success with data
resp, code = ResponseHelper.success(
    data={"id": 1, "name": "John"},
    message="User retrieved successfully"
)

# Success with custom status code
resp, code = ResponseHelper.success(
    data=new_user.to_dict(),
    message="User created successfully",
    status_code=201
)
```

### ResponseHelper.error()

Create error response with optional error code and details.

```python
# Basic error
resp, code = ResponseHelper.error("Something went wrong")

# Error with code and details
resp, code = ResponseHelper.error(
    message="Validation failed",
    status_code=422,
    error_code="VALIDATION_ERROR",
    details={"email": "Invalid format"}
)
```

### ResponseHelper.paginated()

Create paginated response for list endpoints.

```python
# Get paginated data from service
result = UserService.get_all_users(page=1, limit=10)

# Return paginated response
resp, code = ResponseHelper.paginated(
    items=[user.to_dict() for user in result["items"]],
    page=result["page"],
    limit=result["limit"],
    total=result["total"],
    message="Users retrieved successfully"
)
```

### Specialized Error Methods

```python
# Validation error (422)
resp, code = ResponseHelper.validation_error(
    errors={"email": "This field is required"},
    message="Validation failed"
)

# Not found (404)
resp, code = ResponseHelper.not_found("User", "123")

# Unauthorized (401)
resp, code = ResponseHelper.unauthorized("Please login first")

# Forbidden (403)
resp, code = ResponseHelper.forbidden("Access denied")

# Conflict (409)
resp, code = ResponseHelper.conflict("Email", "Email already exists")

# Internal server error (500)
resp, code = ResponseHelper.internal_server_error("Database error")
```

## Usage in Controllers

### Example Controller with ResponseHelper

```python
from flask import Blueprint, request
from app.modules.user.service import UserService
from app.utils.response import ResponseHelper
from app.utils.auth import token_required

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/users", methods=["POST"])
@token_required
def create_user():
    """Create a new user."""
    data = request.get_json()

    # Validation
    if not data or not data.get("email"):
        return ResponseHelper.validation_error("Email is required")

    try:
        user = UserService.create_user(data)
        return ResponseHelper.success(
            data=user.to_dict(),
            message="User created successfully",
            status_code=201
        )
    except ValueError as e:
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return ResponseHelper.internal_server_error("Failed to create user")

@user_blueprint.route("/users", methods=["GET"])
def get_users():
    """Get paginated users."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        result = UserService.get_all_users(page=page, limit=limit)
        return ResponseHelper.paginated(
            items=[user.to_dict() for user in result["items"]],
            page=result["page"],
            limit=result["limit"],
            total=result["total"]
        )
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        return ResponseHelper.internal_server_error("Failed to retrieve users")

@user_blueprint.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get user by ID."""
    user = UserService.get_user_by_id(user_id)

    if not user:
        return ResponseHelper.not_found("User", user_id)

    return ResponseHelper.success(data=user.to_dict())
```

## Migration from Old Format

### Before (Old Format)

```python
from flask import jsonify

# Success
return jsonify({
    "error": False,
    "message": "Success",
    "data": user.to_dict()
}), 200

# Error
return jsonify({
    "error": True,
    "message": "User not found"
}), 404
```

### After (ResponseHelper)

```python
from app.utils.response import ResponseHelper

# Success
return ResponseHelper.success(
    data=user.to_dict(),
    message="Success"
)

# Error
return ResponseHelper.not_found("User", user_id)
```

## Backward Compatibility

Function aliases tersedia untuk kompatibilitas:

```python
# These still work but deprecated
from app.utils.response import (
    success_response,      # -> ResponseHelper.success
    error_response,        # -> ResponseHelper.error
    paginated_response,    # -> ResponseHelper.paginated
    validation_error_response,  # -> ResponseHelper.validation_error
    not_found_response,    # -> ResponseHelper.not_found
    # ... etc
)
```

## Best Practices

1. **Always use ResponseHelper**: Jangan gunakan `jsonify` langsung untuk API responses
2. **Consistent messaging**: Gunakan pesan yang jelas dan konsisten
3. **Proper status codes**: Gunakan status code HTTP yang sesuai
4. **Error handling**: Tangkap exception dan kembalikan error response yang tepat
5. **Logging**: Log error sebelum mengembalikan error response
6. **Validation**: Gunakan `validation_error()` untuk validation errors
7. **Documentation**: Tambahkan docstring yang menjelaskan response format

## Testing ResponseHelper

```python
# Test in Python shell
from app.utils.response import ResponseHelper

# Test success response
resp, code = ResponseHelper.success({"id": 1}, "Success")
print(f"Response: {resp}, Status: {code}")

# Test error response
resp, code = ResponseHelper.error("Error occurred", 400)
print(f"Response: {resp}, Status: {code}")
```
