# Recommendation Service API

Recommendation service provides personalized food recommendations using various algorithms.

## Endpoints

### Get Collaborative Filtering Recommendations

Get food recommendations for a user based on collaborative filtering.

-   **URL:** `/recommendations/users/:user_id`
-   **Method:** `GET`
-   **Authentication Required:** Yes (Owner or Admin)
-   **Query Parameters:**
    -   `limit` (optional): Maximum number of recommendations to return (default: 10)

**Success Response:**

```json
[
    {
        "food": {
            "id": 5,
            "name": "Nasi Goreng Spesial",
            "description": "Nasi goreng dengan telur, ayam, dan udang",
            "category": "Main Course",
            "price": 35000
        },
        "predicted_rating": 4.8
    }
    // More recommendations...
]
```

**Error Response:**

```json
{
    "error": "User not found"
}
```

**Notes:**

-   Collaborative filtering uses user-item interaction patterns to predict ratings

### Get Hybrid Recommendations

Get hybrid recommendations for a user combining collaborative filtering and content-based approaches.

-   **URL:** `/recommendations/hybrid/users/:user_id`
-   **Method:** `GET`
-   **Authentication Required:** Yes (Owner or Admin)
-   **Query Parameters:**
    -   `limit` (optional): Maximum number of recommendations to return (default: 10)
    -   `alpha` (optional): Weight for collaborative filtering (0-1, default: 0.7)

**Success Response:**

```json
[
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
```

**Error Response:**

```json
{
    "error": "User not found"
}
```

**Notes:**

-   `alpha` controls the balance between collaborative filtering (`alpha`) and content-based filtering (`1-alpha`)
-   Higher alpha values prioritize rating patterns, lower values prioritize review content similarity

### Get Top Rated Foods

Get a list of top-rated food items.

-   **URL:** `/recommendations/top-rated`
-   **Method:** `GET`
-   **Authentication Required:** No
-   **Query Parameters:**
    -   `limit` (optional): Maximum number of items to return (default: 10)

**Success Response:**

```json
[
    {
        "id": 5,
        "name": "Nasi Goreng Spesial",
        "description": "Nasi goreng dengan telur, ayam, dan udang",
        "category": "Main Course",
        "price": 35000,
        "average_rating": 4.8,
        "rating_count": 25,
        "popularity_score": 0.92
    }
    // More food items...
]
```

**Notes:**

-   Popularity score is calculated based on average rating and number of ratings
