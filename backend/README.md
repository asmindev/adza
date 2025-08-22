# Food Recommendation System API

A REST API built with Flask for a food recommendation system. The API uses MySQL for data storage and implements a hybrid recommendation algorithm combining collaborative filtering (SVD) and content-based filtering (TF-IDF) for more personalized recommendations.

## Features

-   User management (CRUD operations)
-   Food management (CRUD operations)
-   Rating system for users to rate foods
-   Review system for users to write detailed reviews of foods
-   Hybrid food recommendations (SVD + TF-IDF)
-   Collaborative Filtering (SVD) recommendations
-   Content-based recommendations using reviews
-   Top-rated food recommendations

## Requirements

-   Python 3.8+
-   MySQL database

## Project Structure

The application follows a modular repository architecture for better organization and maintainability:

```
app/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           ├── user/
│           │   ├── __init__.py
│           │   └── routes.py
│           ├── food/
│           │   ├── __init__.py
│           │   └── routes.py
│           ├── rating/
│           │   ├── __init__.py
│           │   └── routes.py
│           ├── recommendation/
│           │   ├── __init__.py
│           │   └── routes.py
│           └── outlet/
│               ├── __init__.py
│               └── routes.py
├── models/
│   ├── __init__.py
│   ├── models.py
│   └── gofood.py
└── services/
    ├── food_service.py
    ├── rating_service.py
    ├── recommendation_service.py
    └── user_service.py
```

-   **Routes**: Organized by domain in separate subfolders
-   **Models**: Database models using SQLAlchemy ORM
-   **Services**: Business logic for each domain

## Installation

1. Clone the repository:

```
git clone <repository-url>
cd food-recommendation-api
```

2. Create a virtual environment and activate it:

```
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:

```
pip install -r requirements.txt
```

4. Configure the database:

    - Create a MySQL database called `food_recommendation`
    - Update the `.env` file with your database credentials

5. Initialize the database:

```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Populate the database with sample data:

```
python create_sample_data.py
```

## Running the Application

```
flask run
```

The API will be available at http://localhost:5000

## API Endpoints

### User Management

-   `GET /api/v1/users` - Get all users
-   `GET /api/v1/users/<user_id>` - Get a specific user
-   `POST /api/v1/users` - Create a new user
    ```json
    {
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    }
    ```
-   `PUT /api/v1/users/<user_id>` - Update a user
    ```json
    {
        "username": "updated_username",
        "email": "updated_email@example.com",
        "password": "new_password"
    }
    ```
-   `DELETE /api/v1/users/<user_id>` - Delete a user

### Food Management

-   `GET /api/v1/foods` - Get all foods
-   `GET /api/v1/foods/<food_id>` - Get a specific food
-   `POST /api/v1/foods` - Create a new food
    ```json
    {
        "name": "Nasi Goreng",
        "description": "Indonesian fried rice",
        "category": "Rice",
        "price": 25000
    }
    ```
-   `PUT /api/v1/foods/<food_id>` - Update a food
    ```json
    {
        "name": "Updated Food Name",
        "description": "Updated description",
        "category": "Updated category",
        "price": 30000
    }
    ```
-   `DELETE /api/v1/foods/<food_id>` - Delete a food

### Rating and Review Management

-   `GET /api/v1/ratings` - Get all ratings
-   `GET /api/v1/users/<user_id>/ratings` - Get all ratings by a user
-   `GET /api/v1/foods/<food_id>/ratings` - Get all ratings for a food
-   `GET /api/v1/users/<user_id>/reviews` - Get all reviews written by a user
-   `GET /api/v1/foods/<food_id>/reviews` - Get all reviews for a specific food
-   `POST /api/v1/users/<user_id>/foods/<food_id>/rating` - Create or update a rating and review
    ```json
    {
        "rating": 4.5,
        "comment": "This food is delicious!",
        "review_title": "Sangat Enak!",
        "review_text": "Saya sangat menyukai makanan ini. Rasanya enak dan porsinya pas. Sangat direkomendasikan untuk dicoba!"
    }
    ```
-   `DELETE /api/v1/users/<user_id>/foods/<food_id>/rating` - Delete a rating and its associated review

### Recommendations

-   `GET /api/v1/recommendations/users/<user_id>?limit=10` - Get food recommendations for a user using collaborative filtering
-   `GET /api/v1/recommendations/hybrid/users/<user_id>?limit=10&alpha=0.7` - Get hybrid recommendations combining rating predictions and review similarity
-   `GET /api/v1/recommendations/top-rated?limit=10` - Get top-rated foods

## Implementation Details

-   **Models**: User, Food, Rating (with review features)
-   **Services**: UserService, FoodService, RatingService, RecommendationService
-   **Algorithms**:
    -   Collaborative Filtering using SVD (Singular Value Decomposition)
    -   Content-based Filtering using TF-IDF and Cosine Similarity
    -   Hybrid approach combining both methods with adjustable weights
-   **Database**: MySQL with SQLAlchemy ORM
-   **Architecture**: Repository pattern with modular organization by domain

## Hybrid Recommendation System

The hybrid recommendation system combines:

1. **Collaborative Filtering (SVD)**: Predicts ratings based on user-item interaction patterns
2. **Content-Based Filtering (TF-IDF)**: Uses review text similarity to find foods with similar characteristics

The final recommendation score is calculated using:

```
final_score = alpha * normalized_rating_score + (1 - alpha) * normalized_review_similarity
```

Where:

-   `alpha` is a configurable weight parameter (default: 0.7)
-   Both scores are normalized using MinMaxScaler to ensure fair comparison

## Detail Algoritma Sistem Rekomendasi Hybrid

Sistem rekomendasi yang diimplementasikan menggabungkan dua pendekatan utama untuk memberikan rekomendasi makanan yang lebih akurat dan personal kepada pengguna.

### 1. Collaborative Filtering dengan SVD (Singular Value Decomposition)

SVD adalah teknik dalam collaborative filtering yang mereduksi dimensi matriks rating user-item untuk menemukan faktor laten yang mempengaruhi preferensi pengguna.

#### Alur Kerja SVD:

1. **Pengumpulan Data**:

    - Semua rating diambil dari database dan dikonversi menjadi DataFrame
    - Format data: `user_id`, `food_id`, dan `rating`

2. **Pembuatan Model**:

    - Data diubah ke format Surprise menggunakan `Reader` dan `Dataset`
    - Rating scale diatur antara 1 sampai 5

3. **Pelatihan Model**:

    - Model SVD dilatih dengan parameter:
        - `n_factors=100` (jumlah faktor laten)
        - `n_epochs=20` (jumlah iterasi)
        - `random_state=42` (untuk reprodusibilitas)

4. **Prediksi Rating**:
    - Model memprediksi rating untuk makanan yang belum diberi rating oleh pengguna
    - Hasil prediksi berupa nilai numerik antara 1-5

### 2. Content-Based Filtering dengan TF-IDF & Cosine Similarity

Pendekatan ini menggunakan teks ulasan makanan untuk menemukan kemiripan antar makanan berdasarkan konten deskriptifnya.

#### Alur Kerja Content-Based Filtering:

1. **Pengumpulan Ulasan**:

    - Semua ulasan (review_text, review_title, comment) untuk setiap makanan dikumpulkan
    - Ulasan digabungkan menjadi satu dokumen per makanan

2. **Preprocessing Teks**:

    - Konversi ke huruf kecil
    - Penghapusan tanda baca
    - Penghapusan whitespace berlebih
    - Penghapusan stop words bahasa Indonesia

3. **Vektorisasi TF-IDF**:

    - Teks ulasan diubah menjadi vektor numerik menggunakan TF-IDF
    - Parameter TF-IDF:
        - `min_df=1` (kata harus muncul minimal di 1 dokumen)
        - `max_df=0.9` (kata yang muncul di >90% dokumen diabaikan)
        - `stop_words=STOPWORDS_ID` (menghilangkan kata umum bahasa Indonesia)
        - `ngram_range=(1, 2)` (menggunakan unigram dan bigram)

4. **Perhitungan Cosine Similarity**:

    - Menghitung matriks kemiripan antar makanan berdasarkan vektor TF-IDF
    - Hasil berupa nilai antara 0-1, di mana 1 berarti sangat mirip

5. **Pembobotan Similarity**:
    - Skor kemiripan diberi bobot berdasarkan rating yang diberikan pengguna
    - Makanan yang diberi rating tinggi oleh pengguna akan lebih mempengaruhi rekomendasi

### 3. Penggabungan Menjadi Sistem Hybrid

Pendekatan hybrid menggabungkan kedua metode di atas dengan parameter alpha yang dapat disesuaikan.

#### Alur Kerja Hybrid Recommendation:

1. **Prediksi Dua Sumber**:

    - Sistem mendapatkan prediksi rating dari model SVD
    - Sistem mendapatkan skor kemiripan ulasan dari analisis TF-IDF

2. **Normalisasi Skor**:

    - Kedua skor (SVD dan similarity) dinormalisasi ke rentang [0,1] menggunakan MinMaxScaler
    - Normalisasi memastikan kontribusi seimbang dari kedua pendekatan

3. **Penggabungan Skor**:

    - Menghitung skor hybrid dengan formula:
        ```
        final_score = alpha * normalized_rating_score + (1 - alpha) * normalized_review_similarity
        ```
    - Parameter `alpha` (0-1) mengontrol bobot masing-masing pendekatan

4. **Pengurutan dan Seleksi**:
    - Makanan diurutkan berdasarkan skor hybrid tertinggi
    - Top-N rekomendasi dikembalikan kepada pengguna

## Alur Proses End-to-End

Berikut adalah alur proses lengkap saat pengguna meminta rekomendasi:

1. **Permintaan Rekomendasi**:

    - Pengguna meminta rekomendasi melalui endpoint `/api/v1/recommendations/hybrid/users/<user_id>`
    - Parameter `alpha` dan `limit` dapat ditentukan

2. **Verifikasi Pengguna**:

    - Sistem memeriksa apakah user_id valid
    - Jika tidak valid, kembalikan error 404

3. **Pengumpulan Data**:

    - Sistem mengambil semua makanan dari database
    - Sistem mengidentifikasi makanan yang sudah diberi rating oleh pengguna

4. **Perhitungan Collaborative Filtering**:

    - Model SVD dilatih menggunakan semua data rating yang tersedia
    - Prediksi rating dihitung untuk makanan yang belum diberi rating oleh pengguna

5. **Perhitungan Content-Based Filtering**:

    - Semua ulasan diproses menjadi matriks TF-IDF
    - Kemiripan dihitung antara makanan yang sudah diberi rating dan yang belum
    - Skor kemiripan diberi bobot berdasarkan rating pengguna

6. **Normalisasi dan Penggabungan**:

    - Kedua skor dinormalisasi ke rentang [0,1]
    - Skor digabungkan menggunakan parameter alpha yang ditentukan
    - Skor hybrid akhir dihitung untuk setiap makanan kandidat

7. **Pengurutan dan Pengembalian Hasil**:
    - Makanan diurutkan berdasarkan skor hybrid tertinggi
    - Top-N makanan dikembalikan dengan informasi detail skor

## Keunggulan Sistem Rekomendasi Hybrid

1. **Mengatasi Cold Start Problem**:

    - Content-based dapat memberikan rekomendasi meski data rating terbatas
    - Collaborative filtering bekerja baik untuk pengguna dengan banyak rating

2. **Keberagaman Rekomendasi**:

    - Collaborative filtering menemukan pola tersembunyi di antara pengguna
    - Content-based menjaga rekomendasi tetap relevan dengan preferensi pengguna

3. **Fleksibilitas**:

    - Parameter alpha memungkinkan penyesuaian keseimbangan antara kedua pendekatan
    - Bisa dioptimalkan untuk kasus penggunaan atau pengguna tertentu

4. **Peningkatan Akurasi**:

    - Menggabungkan kekuatan kedua pendekatan
    - Normalisasi memastikan kontribusi seimbang

5. **Adaptif untuk Bahasa Indonesia**:
    - Menggunakan daftar stop words Bahasa Indonesia
    - Preprocessing teks dirancang untuk menangani karakteristik bahasa Indonesia

## Customizing Recommendations

You can adjust the `alpha` parameter to change the weight balance:

-   `alpha=1.0`: Pure collaborative filtering (SVD only)
-   `alpha=0.0`: Pure content-based filtering (TF-IDF only)
-   `alpha=0.7`: 70% weight on ratings, 30% on review similarity (default)

### Example Response

```json
[
    {
        "food": {
            "id": 42,
            "name": "Nasi Padang",
            "description": "Traditional Padang cuisine with various side dishes",
            "category": "Indonesian",
            "price": 35000
        },
        "predicted_rating": 4.62,
        "normalized_rating_score": 0.92,
        "normalized_review_similarity": 0.78,
        "hybrid_score": 0.88
    }
    // more recommendations...
]
```

## License

MIT
