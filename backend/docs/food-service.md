# Food Service API

Food service manages food items, including creation, retrieval, updating, and deletion.

## Endpoints

### Create Food

Create a new food item.

-   **URL:** `/foods`
-   **Method:** `POST`
-   **Authentication Required:** Yes (Admin)

**Request Body:**

```json
{
    "name": "Nasi Goreng Spesial",
    "description": "Nasi goreng dengan telur, ayam, dan udang",
    "category": "Main Course",
    "price": 35000
}
```

**Success Response:**

```json
{
    "error": false,
    "message": "Food created successfully",
    "data": {
        "id": 1,
        "name": "Nasi Goreng Spesial",
        "description": "Nasi goreng dengan telur, ayam, dan udang",
        "category": "Main Course",
        "price": 35000
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Food name is required"
}
```

**Notes:**

-   Only `name` is required, other fields are optional

### Get All Foods

Get a list of all food items with their details.

-   **URL:** `/foods`
-   **Method:** `GET`
-   **Authentication Required:** No

**Success Response:**

```json
{
    "error": false,
    "data": {
        "foods": [
            {
                "id": 1,
                "name": "Nasi Goreng Spesial",
                "description": "Nasi goreng dengan telur, ayam, dan udang",
                "category": "Main Course",
                "price": 35000,
                "average_rating": 4.5,
                "rating_count": 12
            }
            // More food items...
        ]
    }
}
```

### Get Food Detail

Get detailed information about a specific food item.

-   **URL:** `/foods/:food_id`
-   **Method:** `GET`
-   **Authentication Required:** No

**Success Response:**

```json
{
    "error": false,
    "data": {
        "id": 1,
        "name": "Nasi Goreng Spesial",
        "description": "Nasi goreng dengan telur, ayam, dan udang",
        "category": "Main Course",
        "price": 35000,
        "average_rating": 4.5,
        "rating_count": 12,
        "reviews": [
            {
                "id": 1,
                "user_id": 3,
                "food_id": 1,
                "content": "Sangat enak dan porsinya banyak!",
                "username": "foodlover"
            }
            // More reviews...
        ]
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Food not found"
}
```

### Update Food

Update a food item's information.

-   **URL:** `/foods/:food_id`
-   **Method:** `PUT`
-   **Authentication Required:** Yes (Admin)

**Request Body:**

```json
{
    "name": "Nasi Goreng Super Spesial",
    "description": "Nasi goreng dengan telur, ayam, udang, dan bakso",
    "category": "Main Course",
    "price": 40000
}
```

**Success Response:**

```json
{
    "error": false,
    "message": "Food updated successfully",
    "data": {
        "id": 1,
        "name": "Nasi Goreng Super Spesial",
        "description": "Nasi goreng dengan telur, ayam, udang, dan bakso",
        "category": "Main Course",
        "price": 40000
    }
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Food not found"
}
```

**Notes:**

-   All fields are optional. Only provided fields will be updated.

### Delete Food

Delete a food item from the system.

-   **URL:** `/foods/:food_id`
-   **Method:** `DELETE`
-   **Authentication Required:** Yes (Admin)

**Success Response:**

```json
{
    "error": false,
    "message": "Food deleted successfully"
}
```

**Error Response:**

```json
{
    "error": true,
    "message": "Food not found"
}
```

### Search Foods

Search for food items by category.

-   **URL:** `/foods/search`
-   **Method:** `GET`
-   **Authentication Required:** No
-   **Query Parameters:**
    -   `category` (optional): Filter by food category
    -   `limit` (optional): Maximum number of results to return (default: 10)

**Success Response:**

```json
{
    "error": false,
    "data": {
        "foods": [
            {
                "id": 1,
                "name": "Nasi Goreng Spesial",
                "description": "Nasi goreng dengan telur, ayam, dan udang",
                "category": "Main Course",
                "price": 35000,
                "average_rating": 4.5,
                "rating_count": 12
            }
            // More food items...
        ]
    }
}
```
