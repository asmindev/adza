# Review Service API

Review service manages text reviews for food items written by users.

## Endpoints

### Get Food Reviews

Get all reviews for a specific food item.

-   **URL:** `/foods/:food_id/reviews`
-   **Method:** `GET`
-   **Authentication Required:** No

**Success Response:**

```json
{
    "error": false,
    "data": {
        "food_id": 1,
        "reviews": [
            {
                "id": 1,
                "user_id": 3,
                "food_id": 1,
                "review_text": "Sangat enak dan porsinya banyak!",
                "username": "foodlover"
            }
            // More reviews...
        ]
    }
}
```

### Get User Reviews

Get all reviews written by a specific user.

-   **URL:** `/users/:user_id/reviews`
-   **Method:** `GET`
-   **Authentication Required:** Yes (Admin or Owner)

**Success Response:**

```json
{
    "error": false,
    "data": {
        "user_id": 3,
        "reviews": [
            {
                "id": 1,
                "user_id": 3,
                "food_id": 1,
                "review_text": "Sangat enak dan porsinya banyak!",
                "food_name": "Nasi Goreng Spesial"
            }
            // More reviews...
        ]
    }
}
```

### Create or Update Review

Create a review for a food item or update an existing review.

-   **URL:** `/users/:user_id/foods/:food_id/review`
-   **Method:** `POST` (create) or `PUT` (update)
-   **Authentication Required:** Yes (Owner)

**Request Body:**

```json
{
    "review_text": "Sangat enak dan porsinya banyak! Akan order lagi."
}
```

**Success Response:**

```json
{
    "error": false,
    "message": "Review added successfully",
    "data": {
        "id": 1,
        "user_id": 3,
        "food_id": 1,
        "review_text": "Sangat enak dan porsinya banyak! Akan order lagi."
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "User must rate the food before adding a review"
}
```

**Notes:**

-   User must rate the food item before being able to review it
-   A user can only review a food item once (but can update their review)

### Delete Review

Delete a user's review for a food item.

-   **URL:** `/users/:user_id/foods/:food_id/review`
-   **Method:** `DELETE`
-   **Authentication Required:** Yes (Owner or Admin)

**Success Response:**

```json
{
    "error": false,
    "message": "Review deleted successfully"
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Review not found"
}
```

**Notes:**

-   Deleting a review does not delete the associated rating
