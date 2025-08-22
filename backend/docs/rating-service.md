# Rating Service API

Rating service manages food ratings given by users.

## Endpoints

### Get Food Ratings

Get all ratings for a specific food item.

-   **URL:** `/foods/:food_id/ratings`
-   **Method:** `GET`
-   **Authentication Required:** No

**Success Response:**

```json
{
    "error": false,
    "data": {
        "food_id": 1,
        "average_rating": 4.5,
        "rating_count": 12,
        "ratings": [
            {
                "id": 1,
                "user_id": 3,
                "food_id": 1,
                "rating": 5,
                "username": "foodlover"
            }
            // More ratings...
        ]
    }
}
```

### Get User Ratings

Get all ratings given by a specific user.

-   **URL:** `/users/:user_id/ratings`
-   **Method:** `GET`
-   **Authentication Required:** Yes (Admin or Owner)

**Success Response:**

```json
{
    "error": false,
    "data": {
        "user_id": 3,
        "ratings": [
            {
                "id": 1,
                "user_id": 3,
                "food_id": 1,
                "rating": 5,
                "food_name": "Nasi Goreng Spesial"
            }
            // More ratings...
        ]
    }
}
```

### Create or Update Rating

Rate a food item or update an existing rating.

-   **URL:** `/users/:user_id/foods/:food_id/rating`
-   **Method:** `POST` (create) or `PUT` (update)
-   **Authentication Required:** Yes (Owner)

**Request Body:**

```json
{
    "rating": 4.5
}
```

**Success Response:**

```json
{
    "error": false,
    "message": "Rating added successfully",
    "data": {
        "id": 1,
        "user_id": 3,
        "food_id": 1,
        "rating": 4.5
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Rating must be between 1 and 5"
}
```

**Notes:**

-   Rating value must be between 1 and 5
-   A user can only rate a food item once (but can update their rating)

### Delete Rating

Delete a user's rating for a food item.

-   **URL:** `/users/:user_id/foods/:food_id/rating`
-   **Method:** `DELETE`
-   **Authentication Required:** Yes (Owner or Admin)

**Success Response:**

```json
{
    "error": false,
    "message": "Rating deleted successfully"
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Rating not found"
}
```
