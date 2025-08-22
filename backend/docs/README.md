# GoFood API Documentation

This documentation provides details about the GoFood API endpoints, request/response formats, and examples.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:5000/api/v1
```

## Authentication

Most endpoints require authentication. Authentication is handled via Bearer tokens.

```
Authorization: Bearer your-token-here
```

## Available Services

The API provides the following services:

1. [User Service](./user-service.md) - User registration, authentication, and management
2. [Food Service](./food-service.md) - Food item CRUD operations and search
3. [Rating Service](./rating-service.md) - Food rating operations
4. [Review Service](./review-service.md) - Food review operations
5. [Recommendation Service](./recommendation-service.md) - Food recommendation algorithms

## Error Handling

All API endpoints follow a standard error response format:

```json
{
    "error": true,
    "message": "Error message describing what went wrong"
}
```

Successful responses typically have this format:

```json
{
    "error": false,
    "message": "Optional success message",
    "data": {
        // Response data object
    }
}
```

## Rate Limiting

The API implements rate limiting to protect against abuse. Clients should respect the rate limit headers in responses.
