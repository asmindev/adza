# Updated Recommendation API Documentation

## Overview

Updated API dengan support untuk hybrid food+restaurant recommendation system.

## Endpoints

### 1. GET /recommendation

Get personalized food recommendations using hybrid collaborative filtering

**Parameters:**

-   `limit` (int, optional): Number of recommendations (1-50, default: 10)
-   `alpha` (float, optional): Weight for food vs restaurant rating (0.0-1.0, default: 0.7)
-   `hybrid` (bool, optional): Enable/disable hybrid scoring (default: true)

**Alpha Parameter:**

-   `0.0`: 100% restaurant rating weight
-   `0.5`: 50% food, 50% restaurant
-   `0.7`: 70% food, 30% restaurant (default)
-   `1.0`: 100% food rating weight

**Headers:**

-   `Authorization: Bearer <token>` (required)

**Response:**

```json
{
  "status": "success",
  "data": {
    "recommendations": ["food_id_1", "food_id_2", ...],
    "fallback": false,
    "hybrid_info": {
      "hybrid_scoring_enabled": true,
      "alpha": 0.7,
      "restaurant_coverage": 0.0,
      "formula": "score = (0.7 * food_rating) + (0.3 * restaurant_rating)"
    },
    "system_stats": {
      "total_requests": 1,
      "successful_recommendations": 1,
      "fallback_recommendations": 0,
      "success_rate": 1.0,
      "fallback_rate": 0.0,
      "avg_processing_time": 0.25,
      "is_initialized": true,
      "cache_age": 0
    }
  }
}
```

### 2. GET /popular

Get popular foods based on user ratings

**Response:**

```json
{
  "status": "success",
  "data": {
    "top_rated": ["food_id_1", "food_id_2", ...]
  }
}
```

### 3. GET /hybrid-info

Get information about the hybrid scoring system

**Parameters:**

-   `alpha` (float, optional): Alpha value to test (0.0-1.0, default: 0.7)

**Response:**

```json
{
    "status": "success",
    "data": {
        "hybrid_info": {
            "hybrid_scoring_enabled": true,
            "alpha": 0.7,
            "restaurant_coverage": 0.0,
            "formula": "score = (0.7 * food_rating) + (0.3 * restaurant_rating)"
        },
        "system_stats": {
            "total_requests": 0,
            "successful_recommendations": 0,
            "fallback_recommendations": 0,
            "success_rate": 0,
            "fallback_rate": 0,
            "avg_processing_time": 0.0,
            "is_initialized": false,
            "cache_age": 0
        },
        "rating_statistics": {
            "total_ratings": 36,
            "avg_rating": 4.57,
            "min_rating": 2.0,
            "max_rating": 5.0,
            "std_rating": 0.62,
            "unique_users": 4,
            "unique_foods": 21,
            "restaurant_coverage_percent": 0.0
        },
        "config": {
            "default_alpha": 0.7,
            "min_recommendations": 1,
            "max_recommendations": 50,
            "default_recommendations": 10
        }
    }
}
```

## Example Usage

### Basic Recommendation Request

```bash
curl -X GET "http://localhost:5000/recommendation?limit=5" \
  -H "Authorization: Bearer <your_token>"
```

### Hybrid Recommendation with Custom Alpha

```bash
curl -X GET "http://localhost:5000/recommendation?limit=10&alpha=0.5&hybrid=true" \
  -H "Authorization: Bearer <your_token>"
```

### Food-Only Recommendations (No Restaurant Rating)

```bash
curl -X GET "http://localhost:5000/recommendation?alpha=1.0" \
  -H "Authorization: Bearer <your_token>"
```

### Restaurant-Only Recommendations (No Food Rating)

```bash
curl -X GET "http://localhost:5000/recommendation?alpha=0.0" \
  -H "Authorization: Bearer <your_token>"
```

### Disable Hybrid Scoring

```bash
curl -X GET "http://localhost:5000/recommendation?hybrid=false" \
  -H "Authorization: Bearer <your_token>"
```

### Get Hybrid System Info

```bash
curl -X GET "http://localhost:5000/hybrid-info?alpha=0.8"
```

### Get Popular Foods

```bash
curl -X GET "http://localhost:5000/popular"
```

## Key Features

1. **Hybrid Scoring**: Combines food and restaurant ratings with configurable weighting
2. **Fallback Logic**: Automatically falls back to food-only ratings when restaurant ratings unavailable
3. **Real-time Coverage**: Reports restaurant rating coverage percentage
4. **Flexible Alpha**: Runtime adjustable weighting parameter
5. **System Statistics**: Detailed performance and usage metrics
6. **Transparent Formula**: Shows exact scoring formula being used

## Migration from Old API

### Changes:

1. `alpha` parameter now controls food vs restaurant weight (was enhancement weight)
2. Removed price-related parameters (min_price, max_price, preferred_price)
3. Added `hybrid` parameter to enable/disable hybrid scoring
4. Added `/hybrid-info` endpoint for system information
5. Enhanced response with hybrid_info and system_stats

### Backward Compatibility:

-   All existing endpoints still work
-   Default behavior maintained for requests without new parameters
-   Error handling and validation improved
