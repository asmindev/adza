# User Service API

User service manages user registration, authentication, and user profile operations.

## Endpoints

### User Registration

Register a new user in the system.

-   **URL:** `/auth/register`
-   **Method:** `POST`
-   **Authentication Required:** No

**Request Body:**

```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secure_password123"
}
```

**Success Response:**

```json
{
    "error": false,
    "message": "User registered successfully",
    "data": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com"
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Missing required fields"
}
```

**Notes:**

-   All fields are required
-   Email must be valid and unique
-   Username must be unique

### User Login

Authenticate a user and get an access token.

-   **URL:** `/auth/login`
-   **Method:** `POST`
-   **Authentication Required:** No

**Request Body:**

```json
{
    "username": "johndoe",
    "password": "secure_password123"
}
```

**Success Response:**

```json
{
    "error": false,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com"
        },
        "token": "access-token-here"
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Invalid username or password"
}
```

### Get All Users (Admin Only)

Get a list of all users in the system.

-   **URL:** `/users`
-   **Method:** `GET`
-   **Authentication Required:** Yes (Admin)

**Success Response:**

```json
{
    "error": false,
    "data": {
        "users": [
            {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com"
            },
            {
                "id": 2,
                "username": "janedoe",
                "email": "jane@example.com"
            }
        ]
    }
}
```

### Get User Detail

Get details of a specific user.

-   **URL:** `/users/:user_id`
-   **Method:** `GET`
-   **Authentication Required:** Yes (Admin or Owner)

**Success Response:**

```json
{
    "error": false,
    "data": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com"
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "User not found"
}
```

### Update User

Update a user's information.

-   **URL:** `/users/:user_id`
-   **Method:** `PUT`
-   **Authentication Required:** Yes (Admin or Owner)

**Request Body:**

```json
{
    "username": "john_updated",
    "email": "john_new@example.com",
    "password": "new_password123"
}
```

**Success Response:**

```json
{
    "error": false,
    "message": "User updated successfully",
    "data": {
        "id": 1,
        "username": "john_updated",
        "email": "john_new@example.com"
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "User not found"
}
```

**Notes:**

-   All fields are optional. Only provided fields will be updated.

### Delete User

Delete a user from the system.

-   **URL:** `/users/:user_id`
-   **Method:** `DELETE`
-   **Authentication Required:** Yes (Admin or Owner)

**Success Response:**

```json
{
    "error": false,
    "message": "User deleted successfully"
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "User not found"
}
```

### Get User Recommendations

Get personalized food recommendations for a user.

-   **URL:** `/users/:user_id/recommendations`
-   **Method:** `GET`
-   **Authentication Required:** Yes (Admin or Owner)
-   **Query Parameters:**
    -   `limit` (optional): Maximum number of recommendations to return (default: 10)
    -   `alpha` (optional): Weight for collaborative filtering (0-1, default: 0.7)

**Success Response:**

```json
{
    "error": false,
    "data": {
        "recommendations": [
            {
                "food": {
                    "id": 5,
                    "name": "Nasi Goreng Spesial",
                    "description": "Nasi goreng dengan telur, ayam, dan udang",
                    "category": "Main Course",
                    "price": 35000
                },
                "predicted_rating": 4.8,
                "normalized_rating_score": 0.96,
                "normalized_review_similarity": 0.85,
                "hybrid_score": 0.93
            }
            // More recommendations...
        ]
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "User not found"
}
```
