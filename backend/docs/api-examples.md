# API Usage Examples

This document provides practical examples of how to use the GoFood API with various programming languages and tools.

## User Registration and Login

### Using cURL

**Register a new user:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Login with the new user:**

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Using JavaScript (fetch)

**Register a new user:**

```javascript
fetch("http://localhost:5000/api/v1/auth/register", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        username: "testuser",
        email: "test@example.com",
        password: "password123",
    }),
})
    .then((response) => response.json())
    .then((data) => console.log(data))
    .catch((error) => console.error("Error:", error));
```

## Rating and Reviewing Food

### Using cURL

**Rate a food item:**

```bash
curl -X POST http://localhost:5000/api/v1/users/1/foods/5/rating \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{
    "rating": 4.5
  }'
```

**Add a review after rating:**

```bash
curl -X POST http://localhost:5000/api/v1/users/1/foods/5/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{
    "review_text": "Sangat enak dan porsinya banyak! Akan order lagi."
  }'
```

### Using Python (requests)

**Rate and review in one script:**

```python
import requests

# Configuration
base_url = 'http://localhost:5000/api/v1'
user_id = 1
food_id = 5
token = 'your-token-here'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

# Rate the food
rating_data = {'rating': 4.5}
rating_response = requests.post(
    f'{base_url}/users/{user_id}/foods/{food_id}/rating',
    headers=headers,
    json=rating_data
)
print('Rating response:', rating_response.json())

# If rating successful, add a review
if rating_response.status_code in (200, 201):
    review_data = {'review_text': 'Sangat enak dan porsinya banyak! Akan order lagi.'}
    review_response = requests.post(
        f'{base_url}/users/{user_id}/foods/{food_id}/review',
        headers=headers,
        json=review_data
    )
    print('Review response:', review_response.json())
```

## Getting Recommendations

### Using cURL

**Get hybrid recommendations:**

```bash
curl -X GET "http://localhost:5000/api/v1/recommendations/hybrid/users/1?limit=5&alpha=0.7" \
  -H "Authorization: Bearer your-token-here"
```

### Using jQuery

**Display recommendations on a webpage:**

```javascript
$.ajax({
    url: "http://localhost:5000/api/v1/recommendations/hybrid/users/1",
    type: "GET",
    headers: {
        Authorization: "Bearer your-token-here",
    },
    success: function (data) {
        const recommendations = data;
        let html = "<h2>Recommended for You</h2><ul>";

        recommendations.forEach((rec) => {
            html += `
        <li>
          <h3>${rec.food.name}</h3>
          <p>${rec.food.description}</p>
          <p>Predicted Rating: ${rec.predicted_rating}</p>
          <p>Price: Rp ${rec.food.price}</p>
        </li>
      `;
        });

        html += "</ul>";
        $("#recommendations").html(html);
    },
    error: function (error) {
        console.error("Error fetching recommendations:", error);
    },
});
```
