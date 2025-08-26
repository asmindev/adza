"""
Response utilities for consistent API responses across the application.

This module provides standardized response formats for success and error cases,
ensuring all API endpoints return responses in a consistent structure.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Union


@dataclass
class ApiResponse:
    """Base dataclass for API responses."""

    message: str
    error: bool = False


@dataclass
class SuccessResponse(ApiResponse):
    """Dataclass for successful API responses."""

    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = None
    error: bool = False


@dataclass
class ErrorResponse(ApiResponse):
    """Dataclass for error API responses."""

    error_code: Optional[str] = None
    details: Optional[Any] = None
    error: bool = True


@dataclass
class PaginationMeta:
    """Dataclass for pagination metadata."""

    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class ResponseHelper:
    """
    Response helper class with static methods for creating standardized API responses.
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None,
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized success response.

        Args:
            data: The response data to include
            message: Success message (default: "Success")
            status_code: HTTP status code (default: 200)
            meta: Optional metadata (e.g., pagination info)

        Returns:
            Tuple of (response_dict, status_code)
        """
        response = SuccessResponse(message=message, data=data, meta=meta)

        # Remove None values from response
        response_dict = {k: v for k, v in asdict(response).items() if v is not None}

        return response_dict, status_code

    @staticmethod
    def error(
        message: str = "An error occurred",
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized error response.

        Args:
            message: Error message
            status_code: HTTP status code (default: 400)
            error_code: Optional error code for programmatic handling
            details: Optional additional error details

        Returns:
            Tuple of (response_dict, status_code)
        """
        response = ErrorResponse(
            message=message, error_code=error_code, details=details
        )

        # Remove None values from response
        response_dict = {k: v for k, v in asdict(response).items() if v is not None}

        return response_dict, status_code

    @staticmethod
    def paginated(
        items: list,
        page: int,
        limit: int,
        total: int,
        message: str = "Data retrieved successfully",
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized paginated response.

        Args:
            items: List of items for current page
            page: Current page number
            limit: Items per page
            total: Total number of items
            message: Success message

        Returns:
            Tuple of (response_dict, status_code)
        """
        pages = (total + limit - 1) // limit  # Calculate total pages (ceiling division)

        pagination_meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )

        return ResponseHelper.success(
            data=items, message=message, meta={"pagination": asdict(pagination_meta)}
        )

    @staticmethod
    def validation_error(
        errors: Union[str, Dict[str, Any], list],
        message: str = "Validation failed",
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized validation error response.

        Args:
            errors: Validation errors (string, dict, or list)
            message: Error message

        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseHelper.error(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=errors,
        )

    @staticmethod
    def not_found(
        resource: str = "Resource",
        identifier: Optional[str] = None,
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized not found response.

        Args:
            resource: Name of the resource that wasn't found
            identifier: Optional identifier of the resource

        Returns:
            Tuple of (response_dict, status_code)
        """
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"
        else:
            message = f"{resource} not found"

        return ResponseHelper.error(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
        )

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized access",
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized unauthorized response.

        Args:
            message: Unauthorized message

        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseHelper.error(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )

    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized forbidden response.

        Args:
            message: Forbidden message

        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseHelper.error(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )

    @staticmethod
    def conflict(
        resource: str,
        message: Optional[str] = None,
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized conflict response.

        Args:
            resource: Name of the resource causing conflict
            message: Optional custom message

        Returns:
            Tuple of (response_dict, status_code)
        """
        if not message:
            message = f"{resource} already exists"

        return ResponseHelper.error(
            message=message,
            status_code=409,
            error_code="CONFLICT",
        )

    @staticmethod
    def internal_server_error(
        message: str = "Internal server error occurred",
    ) -> tuple[Dict[str, Any], int]:
        """
        Create a standardized internal server error response.

        Args:
            message: Error message

        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseHelper.error(
            message=message,
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
        )


# Backward compatibility - keep the old function names as aliases
success_response = ResponseHelper.success
error_response = ResponseHelper.error
paginated_response = ResponseHelper.paginated
validation_error_response = ResponseHelper.validation_error
not_found_response = ResponseHelper.not_found
unauthorized_response = ResponseHelper.unauthorized
forbidden_response = ResponseHelper.forbidden
conflict_response = ResponseHelper.conflict
internal_server_error_response = ResponseHelper.internal_server_error
