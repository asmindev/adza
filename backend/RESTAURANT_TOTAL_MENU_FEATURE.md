# Restaurant API - Total Menu Feature

## ✅ Perubahan yang Telah Dilakukan

### 1. **Model Restaurant - Enhanced to_dict()**

```python
# Sekarang selalu mengembalikan:
{
    "id": "uuid",
    "name": "Restaurant Name",
    "rating": {
        "average": 4.5,
        "total": 25  # Total rating count
    },
    "foods": {
        "total": 15  # Total menu count
    },
    "total_foods": 15,  # Backward compatibility
    # ... other fields
}
```

### 2. **Enhanced API Parameters**

-   `search` - Pencarian nama, alamat, deskripsi
-   `status` - Filter berdasarkan status (`active`, `inactive`)
-   `sortBy` - Sorting berdasarkan:
    -   `name` - Nama restoran (A-Z)
    -   `rating` - Rating tertinggi
    -   `foods` - Jumlah menu terbanyak
    -   `created_at` - Terbaru (default)

### 3. **All Endpoints Updated**

#### GET `/api/v1/restaurants`

```bash
# Basic pagination
GET /api/v1/restaurants?page=1&limit=20

# With search
GET /api/v1/restaurants?search=pizza&page=1&limit=20

# With status filter
GET /api/v1/restaurants?status=active&page=1&limit=20

# With sorting by menu count
GET /api/v1/restaurants?sortBy=foods&page=1&limit=20

# Combined filters
GET /api/v1/restaurants?search=pizza&status=active&sortBy=rating&page=1&limit=20
```

#### Response Format:

```json
{
    "success": true,
    "data": {
        "restaurants": [
            {
                "id": "uuid",
                "name": "Pizza Palace",
                "rating": {
                    "average": 4.5,
                    "total": 25
                },
                "foods": {
                    "total": 15
                },
                "total_foods": 15,
                "is_active": true
                // ... other fields
            }
        ],
        "count": 20,
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 61,
            "pages": 4
        },
        "metadata": {
            "count": 20,
            "search_applied": true,
            "search_term": "pizza",
            "status_filter": "active",
            "sort_by": "rating"
        }
    }
}
```

#### GET `/api/v1/restaurants/{id}`

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Pizza Palace",
    "rating": {
      "average": 4.5,
      "total": 25
    },
    "foods": {
      "total": 15
    },
    "total_foods": 15,
    "categories": [...],
    "foods": [...]  // Full food list with details
  }
}
```

## 🎯 **Frontend Integration**

### Hook Update Required

Update `useInfiniteRestaurants.js` untuk menggunakan data yang baru:

```javascript
// Sekarang data restaurant memiliki:
restaurant.foods.total; // Total menu count
restaurant.rating.total; // Total rating count
restaurant.rating.average; // Average rating
```

### Display in RestaurantCard

```jsx
// Di RestaurantCard.jsx
<div className="flex items-center gap-1 ml-auto">
    <Utensils className="h-4 w-4 text-primary" />
    <span className="text-sm font-medium">
        {restaurant.foods.total} menu
    </span>
</div>

<div className="flex items-center gap-2 mb-4">
    <div className="flex items-center gap-1">
        <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
        <span className="font-semibold text-sm">
            {restaurant.rating.average.toFixed(1)}
        </span>
    </div>
    <span className="text-muted-foreground text-sm">
        ({restaurant.rating.total} ulasan)
    </span>
</div>
```

## 🔄 **Sorting by Menu Count**

Untuk sorting berdasarkan jumlah menu, gunakan parameter:

```
GET /api/v1/restaurants?sortBy=foods
```

Backend akan melakukan:

1. JOIN dengan tabel Food
2. GROUP BY restaurant_id
3. COUNT food per restaurant
4. ORDER BY count DESC

## 📊 **Data Consistency**

Semua endpoint restaurant sekarang selalu mengembalikan:

-   ✅ Total menu count (`foods.total`)
-   ✅ Total rating count (`rating.total`)
-   ✅ Average rating (`rating.average`)
-   ✅ Status restaurant (`is_active`)
-   ✅ Categories list
-   ✅ Full restaurant details

## 🚀 **Ready for Frontend**

Backend siap mendukung infinite scroll dengan:

1. **Server-side filtering** untuk performance
2. **Total menu count** untuk setiap restaurant
3. **Enhanced sorting** termasuk berdasarkan jumlah menu
4. **Consistent data structure** di semua endpoint
