# Detailed Rating System - API Examples

## Overview

Sistem rating sekarang mendukung penilaian berdasarkan kriteria yang lebih detail:

-   **flavor** (rasa): Rating untuk rasa makanan (1-5)
-   **serving** (porsi): Rating untuk porsi makanan (1-5)
-   **price** (harga): Rating untuk harga makanan (1-5)
-   **place** (tempat): Rating untuk tempat/suasana (1-5)

Rating akhir dihitung dari rata-rata keempat kriteria tersebut.

## API Endpoint

`POST/PUT /api/ratings`

## New Request Format (Detailed Rating)

```json
{
    "food_id": "123e4567-e89b-12d3-a456-426614174000",
    "rating_details": {
        "flavor": 5, // Rasa sangat enak
        "serving": 4, // Porsi cukup banyak
        "price": 4, // Harga cukup wajar
        "place": 5 // Tempat sangat nyaman
    }
}
```

## Response Format

```json
{
    "success": true,
    "message": "Rating added successfully",
    "data": {
        "id": "rating-uuid",
        "user_id": "user-uuid",
        "food_id": "food-uuid",
        "rating": 4.5, // Rata-rata dari (5+4+4+5)/4 = 4.5
        "rating_details": {
            "flavor": 5,
            "serving": 4,
            "price": 4,
            "place": 5
        },
        "created_at": "2025-09-24T10:30:00Z",
        "updated_at": "2025-09-24T10:30:00Z"
    }
}
```

## Legacy Format (Still Supported)

```json
{
    "food_id": "123e4567-e89b-12d3-a456-426614174000",
    "rating": 4.5
}
```

Ketika menggunakan format legacy, sistem akan mengonversi rating tunggal menjadi rating_details dengan nilai yang sama untuk semua kriteria.

## Validation Rules

1. **rating_details harus berisi semua kriteria wajib:**

    - flavor
    - serving
    - price
    - place

2. **Setiap nilai kriteria harus:**

    - Berupa angka (integer atau float)
    - Dalam rentang 1-5
    - Tidak boleh null atau kosong

3. **Contoh error response:**

```json
{
    "success": false,
    "message": "Missing required criteria: price",
    "errors": [
        "Missing required criteria: price",
        "flavor: Rating must be between 1.0 and 5.0"
    ]
}
```

## Use Cases

### 1. Rating Makanan Enak di Tempat Mahal

```json
{
    "food_id": "food-123",
    "rating_details": {
        "flavor": 5, // Rasa excellent
        "serving": 4, // Porsi cukup
        "price": 2, // Harga mahal
        "place": 5 // Tempat mewah
    }
}
// Result: rating = 4.0
```

### 2. Rating Makanan Biasa di Warteg

```json
{
    "food_id": "food-456",
    "rating_details": {
        "flavor": 3, // Rasa standar
        "serving": 4, // Porsi banyak
        "price": 5, // Harga murah
        "place": 3 // Tempat sederhana
    }
}
// Result: rating = 3.75
```

### 3. Rating Makanan Premium

```json
{
    "food_id": "food-789",
    "rating_details": {
        "flavor": 5, // Rasa istimewa
        "serving": 5, // Porsi pas
        "price": 4, // Harga sesuai kualitas
        "place": 5 // Ambiance bagus
    }
}
// Result: rating = 4.75
```

## Benefits

1. **Detailed Feedback**: User bisa memberikan feedback spesifik untuk setiap aspek
2. **Better Analytics**: Restaurant bisa tahu aspek mana yang perlu diperbaiki
3. **Fairer Rating**: Rating tidak bias terhadap satu aspek saja
4. **User Experience**: User merasa penilaiannya lebih meaningful
5. **Recommendation Quality**: Sistem rekomendasi bisa lebih akurat berdasarkan preferensi user

## Migration Notes

-   Database sudah support kolom `rating_details` (JSON)
-   Legacy API calls masih didukung untuk backward compatibility
-   Existing ratings akan tetap berfungsi
-   Frontend perlu diupdate untuk menggunakan format baru
