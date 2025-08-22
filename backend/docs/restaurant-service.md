# Restaurant Service API Documentation

## Overview

The Restaurant module provides comprehensive CRUD operations for managing restaurants with location-based features using latitude and longitude coordinates.

## Features

-   Create, read, update, and delete restaurants
-   Location-based search using latitude/longitude coordinates
-   Restaurant status management (active/inactive)
-   Search restaurants by name
-   Integration with food items through foreign key relationships

## Restaurant Model Fields

| Field          | Type        | Required | Description                   |
| -------------- | ----------- | -------- | ----------------------------- |
| id             | Integer     | Auto     | Primary key                   |
| name           | String(100) | Yes      | Restaurant name               |
| description    | Text        | No       | Restaurant description        |
| address        | String(255) | Yes      | Restaurant address            |
| phone          | String(20)  | No       | Contact phone number          |
| email          | String(100) | No       | Contact email                 |
| latitude       | Float       | Yes      | GPS latitude coordinate       |
| longitude      | Float       | Yes      | GPS longitude coordinate      |
| rating_average | Float       | No       | Average rating (default: 0.0) |
| is_active      | Boolean     | No       | Status flag (default: true)   |
| created_at     | DateTime    | Auto     | Creation timestamp            |
| updated_at     | DateTime    | Auto     | Last update timestamp         |

## API Endpoints

### 1. Create Restaurant (Admin Only)

**POST** `/api/v1/restaurants`

**Headers:**

```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**

```json
{
    "name": "Warung Makan Sederhana",
    "description": "Traditional Indonesian restaurant",
    "address": "Jl. Sudirman No. 123, Jakarta",
    "phone": "+62812345678",
    "email": "info@warungsederhana.com",
    "latitude": -6.2088,
    "longitude": 106.8456
}
```

**Response (201):**

```json
{
    "error": false,
    "message": "Restaurant created successfully",
    "data": {
        "id": 1,
        "name": "Warung Makan Sederhana",
        "description": "Traditional Indonesian restaurant",
        "address": "Jl. Sudirman No. 123, Jakarta",
        "phone": "+62812345678",
        "email": "info@warungsederhana.com",
        "latitude": -6.2088,
        "longitude": 106.8456,
        "rating_average": 0.0,
        "is_active": true,
        "foods": [],
        "created_at": "2025-05-26T10:30:00Z",
        "updated_at": "2025-05-26T10:30:00Z"
    }
}
```

### 2. Get All Restaurants

**GET** `/api/v1/restaurants`

**Query Parameters:**

-   `active=true` - Get only active restaurants
-   `search=<name>` - Search by restaurant name
-   `latitude=<lat>&longitude=<lng>&radius=<km>` - Location-based search

**Examples:**

```
GET /api/v1/restaurants
GET /api/v1/restaurants?active=true
GET /api/v1/restaurants?search=warung
GET /api/v1/restaurants?latitude=-6.2088&longitude=106.8456&radius=5
```

**Response (200):**

```json
{
  "error": false,
  "data": {
    "restaurants": [...],
    "count": 10
  }
}
```

### 3. Get Restaurant by ID

**GET** `/api/v1/restaurants/{id}`

**Response (200):**

```json
{
    "error": false,
    "data": {
        "id": 1,
        "name": "Warung Makan Sederhana",
        "description": "Traditional Indonesian restaurant",
        "address": "Jl. Sudirman No. 123, Jakarta",
        "phone": "+62812345678",
        "email": "info@warungsederhana.com",
        "latitude": -6.2088,
        "longitude": 106.8456,
        "rating_average": 4.5,
        "is_active": true,
        "foods": [
            {
                "id": 1,
                "name": "Nasi Gudeg",
                "price": 15000,
                "category": "Traditional"
            }
        ],
        "created_at": "2025-05-26T10:30:00Z",
        "updated_at": "2025-05-26T10:30:00Z"
    }
}
```

### 4. Update Restaurant (Admin Only)

**PUT** `/api/v1/restaurants/{id}`

**Headers:**

```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**

```json
{
    "name": "Warung Makan Sederhana Updated",
    "phone": "+62812345679",
    "latitude": -6.209,
    "longitude": 106.846
}
```

**Response (200):**

```json
{
  "error": false,
  "message": "Restaurant updated successfully",
  "data": {...}
}
```

### 5. Delete Restaurant (Admin Only)

**DELETE** `/api/v1/restaurants/{id}`

**Headers:**

```
Authorization: Bearer <admin_token>
```

**Response (200):**

```json
{
    "error": false,
    "message": "Restaurant deleted successfully"
}
```

### 6. Toggle Restaurant Status (Admin Only)

**PATCH** `/api/v1/restaurants/{id}/toggle-status`

**Headers:**

```
Authorization: Bearer <admin_token>
```

**Response (200):**

```json
{
  "error": false,
  "message": "Restaurant activated successfully",
  "data": {...}
}
```

### 7. Find Nearby Restaurants

**GET** `/api/v1/restaurants/nearby`

**Query Parameters:**

-   `latitude` (required) - GPS latitude
-   `longitude` (required) - GPS longitude
-   `radius` (optional) - Search radius in kilometers (default: 5)

**Example:**

```
GET /api/v1/restaurants/nearby?latitude=-6.2088&longitude=106.8456&radius=10
```

**Response (200):**

```json
{
  "error": false,
  "data": {
    "restaurants": [...],
    "count": 5,
    "search_location": {
      "latitude": -6.2088,
      "longitude": 106.8456,
      "radius_km": 10
    }
  }
}
```

## Error Responses

### Validation Errors (400)

```json
{
    "error": true,
    "message": "Latitude must be between -90 and 90"
}
```

### Unauthorized (401)

```json
{
    "error": true,
    "message": "Access token is missing or invalid"
}
```

### Forbidden (403)

```json
{
    "error": true,
    "message": "Admin access required"
}
```

### Not Found (404)

```json
{
    "error": true,
    "message": "Restaurant not found"
}
```

### Server Error (500)

```json
{
    "error": true,
    "message": "Failed to create restaurant"
}
```

## Location-Based Features

### Coordinate Validation

-   Latitude: -90 to 90 degrees
-   Longitude: -180 to 180 degrees
-   Radius: Must be greater than 0 km

### Distance Calculation

The system uses a simplified Haversine formula approximation for distance calculations. For production environments with high precision requirements, consider using PostGIS or similar spatial database extensions.

### Search Radius

-   Default radius: 5 km
-   Maximum recommended radius: 50 km
-   The system filters restaurants within a bounding box approximation

## Integration with Food Module

Restaurants have a one-to-many relationship with foods. When retrieving restaurant data, associated foods are included in the response. Similarly, when retrieving food data, restaurant information (including location) is included.

## Usage Examples

### Creating a Restaurant Chain

```bash
# Create main restaurant
curl -X POST http://localhost:5000/api/v1/restaurants \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "McDonald'\''s Sudirman",
    "address": "Plaza Indonesia, Jakarta",
    "latitude": -6.1944,
    "longitude": 106.8229
  }'

# Create branch restaurant
curl -X POST http://localhost:5000/api/v1/restaurants \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "McDonald'\''s Kelapa Gading",
    "address": "Mall of Indonesia, Jakarta",
    "latitude": -6.1588,
    "longitude": 106.9056
  }'
```

### Finding Restaurants Near User Location

```bash
# Get restaurants within 5km of user location
curl "http://localhost:5000/api/v1/restaurants/nearby?latitude=-6.2088&longitude=106.8456&radius=5"
```

### Searching Restaurants

```bash
# Search by name
curl "http://localhost:5000/api/v1/restaurants?search=mcdonald"

# Get only active restaurants
curl "http://localhost:5000/api/v1/restaurants?active=true"
```
