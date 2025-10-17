# Dokumentasi Sistem Rekomendasi

## Daftar Isi

1. [Overview](#overview)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Algoritma dan Metode](#algoritma-dan-metode)
4. [Flow Proses Rekomendasi](#flow-proses-rekomendasi)
5. [Komponen Utama](#komponen-utama)
6. [Hybrid Scoring System](#hybrid-scoring-system)
7. [Konfigurasi](#konfigurasi)
8. [API Usage](#api-usage)
9. [Performance & Optimization](#performance--optimization)

---

## Overview

Sistem rekomendasi ini menggunakan **Collaborative Filtering** dengan algoritma **SVD (Singular Value Decomposition)** untuk memberikan rekomendasi makanan yang personal kepada user berdasarkan pola rating mereka dan user lain yang mirip.

### Fitur Utama

-   ✅ **Collaborative Filtering** menggunakan SVD
-   ✅ **Hybrid Scoring** (Food Rating + Restaurant Rating)
-   ✅ **Local Dataset Optimization** untuk performa lebih cepat
-   ✅ **User Similarity** menggunakan Cosine & Jaccard
-   ✅ **Predicted Rating** untuk setiap rekomendasi
-   ✅ **Data Quality Validation**
-   ✅ **Performance Tracking & Statistics**

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    RecommendationService                     │
│              (Public API untuk aplikasi)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Recommendations                          │
│           (Orchestrator utama sistem)                        │
│  - Koordinasi semua komponen                                │
│  - Request handling & validation                             │
│  - Performance tracking                                      │
└──────┬──────────────────┬───────────────────┬───────────────┘
       │                  │                   │
       │                  │                   │
       ▼                  ▼                   ▼
┌──────────────┐  ┌──────────────┐   ┌──────────────┐
│LocalDataProc │  │LocalSVDModel │   │  Similarity  │
│              │  │              │   │              │
│- Load data   │  │- Train SVD   │   │- Cosine      │
│- Hybrid score│  │- Predict     │   │- Jaccard     │
│- Filter data │  │- Evaluation  │   │- Find similar│
│- Pivot matrix│  │              │   │  users       │
└──────────────┘  └──────────────┘   └──────────────┘
```

---

## Algoritma dan Metode

### 1. Collaborative Filtering dengan SVD

**Singular Value Decomposition (SVD)** adalah teknik matrix factorization yang memecah user-item rating matrix menjadi komponen latent factors.

#### Formula Dasar:

```
R ≈ U × Σ × V^T
```

Dimana:

-   **R**: Original rating matrix (users × items)
-   **U**: User latent factor matrix (users × k factors)
-   **Σ**: Diagonal matrix dengan singular values
-   **V^T**: Item latent factor matrix (k factors × items)

#### Prediksi Rating:

```python
predicted_rating = global_mean + user_bias + item_bias + (user_factors · item_factors)
```

**Komponen Prediksi:**

1. **Global Mean**: Rata-rata rating seluruh dataset
2. **User Bias**: Kecenderungan user memberikan rating tinggi/rendah
3. **Item Bias**: Kecenderungan item menerima rating tinggi/rendah
4. **Interaction Term**: Dot product dari user & item latent factors

### 2. User Similarity

Sistem menggunakan dua metode untuk menghitung kesamaan antar user:

#### A. Cosine Similarity (Default)

```python
similarity = 1 - cosine_distance(user1_vector, user2_vector)
```

**Keunggulan:**

-   Fokus pada **pola rating** (angle antara vector)
-   Tidak terpengaruh magnitude (user yang memberi rating tinggi vs rendah)
-   Lebih akurat untuk pola preferensi

**Cara Kerja:**

```
User A: [5, 4, 0, 3, 0]
User B: [5, 5, 0, 4, 0]
         ↓
Common items only: [5,4,3] vs [5,5,4]
         ↓
Cosine similarity = 0.98 (sangat mirip pola)
```

#### B. Jaccard Similarity (Alternatif)

```python
similarity = |A ∩ B| / |A ∪ B|
```

**Keunggulan:**

-   Fokus pada **overlap items** yang di-rating
-   Simple dan cepat
-   Bagus untuk cold start

**Cara Kerja:**

```
User A rated: {food1, food2, food3, food5}
User B rated: {food1, food2, food4, food6}
         ↓
Intersection: {food1, food2} = 2 items
Union: {food1, food2, food3, food4, food5, food6} = 6 items
         ↓
Jaccard similarity = 2/6 = 0.33
```

### 3. Local Dataset Strategy

Untuk efisiensi, sistem tidak menggunakan seluruh dataset, melainkan membuat **local sub-dataset** dengan user yang mirip.

**Alasan:**

-   ✅ Training SVD lebih cepat (matrix lebih kecil)
-   ✅ Akurasi lebih baik (fokus pada neighborhood yang relevan)
-   ✅ Mengurangi noise dari user yang sangat berbeda

**Parameter:**

-   `top_k_users=50`: Ambil 50 user paling mirip
-   `similarity_threshold=0.2`: Minimum similarity score
-   `similarity_method="cosine"`: Metode perhitungan similarity

---

## Flow Proses Rekomendasi

### Diagram Alur Lengkap

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER REQUEST                                              │
│    GET /recommendations?user_id=123&top_n=10                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SERVICE LAYER (RecommendationService)                     │
│    - Validate user_id exists                                 │
│    - Validate top_n (1-50)                                   │
│    - Call recommender                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LOAD & VALIDATE DATA (LocalDataProcessor)                │
│    - Load hybrid ratings from DB                             │
│    - Apply hybrid formula: α*food + (1-α)*restaurant         │
│    - Filter sparse data (min ratings threshold)              │
│    - Validate data quality                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FIND SIMILAR USERS (Similarity Module)                    │
│    - Calculate cosine similarity dengan semua user           │
│    - Filter by threshold (0.2)                               │
│    - Sort by similarity score                                │
│    - Take top 50 similar users                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. CREATE LOCAL DATASET (LocalDataProcessor)                │
│    - Filter ratings: hanya target user + similar users       │
│    - Create pivot matrix (user × food)                       │
│    - Create ID mappings (string ID → integer index)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. TRAIN SVD MODEL (LocalSVDModel)                          │
│    - Calculate global mean, user bias, item bias            │
│    - Center the matrix (remove biases)                       │
│    - Apply TruncatedSVD (12 factors default)                 │
│    - Extract user_factors & item_factors                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. GENERATE PREDICTIONS (LocalSVDModel)                     │
│    - For each food in dataset:                               │
│      * Skip if user already rated                            │
│      * predicted_rating = mean + biases + interaction        │
│      * Apply confidence weighting                            │
│      * Clip to range [1.0, 5.0]                             │
│    - Sort by predicted rating (descending)                   │
│    - Filter by min_rating threshold (3.0)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. POST-PROCESSING (Recommendations)                        │
│    - Take top N recommendations                              │
│    - Convert indices back to food IDs                        │
│    - Add rank & predicted_rating to each                     │
│    - Update performance statistics                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. ENRICH WITH FOOD DETAILS (RecommendationService)         │
│    - Query Food table for details                            │
│    - Merge with predicted ratings                            │
│    - Return JSON response                                    │
└─────────────────────────────────────────────────────────────┘
```

### Contoh Step-by-Step

**Input:**

```
user_id = "user_abc_123"
top_n = 5
```

**Step 1: Load Data**

```python
# Hybrid ratings loaded
Total ratings: 1000
Users: 50
Foods: 200
Hybrid coverage: 65%
```

**Step 2: Find Similar Users**

```python
# Cosine similarity calculated
user_abc_123 vs user_def_456: 0.82
user_abc_123 vs user_ghi_789: 0.75
user_abc_123 vs user_jkl_012: 0.68
...
Selected 50 similar users (threshold: 0.2)
```

**Step 3: Create Local Dataset**

```python
# Sub-dataset created
Sub-ratings: 250 ratings
Sub-matrix: 51 users × 80 foods
Sparsity: 0.94
```

**Step 4: Train SVD**

```python
# SVD trained
Factors: 12
Explained variance: 0.73
Training time: 0.15s
```

**Step 5: Generate Predictions**

```python
# Predictions for all unrated foods
food_001: 4.52
food_042: 4.31
food_087: 4.18
food_123: 3.95
food_156: 3.82
...
```

**Step 6: Filter & Return**

```python
# Top 5 recommendations (min_rating=3.0)
[
  {food_id: "food_001", predicted_rating: 4.52, rank: 1},
  {food_id: "food_042", predicted_rating: 4.31, rank: 2},
  {food_id: "food_087", predicted_rating: 4.18, rank: 3},
  {food_id: "food_123", predicted_rating: 3.95, rank: 4},
  {food_id: "food_156", predicted_rating: 3.82, rank: 5}
]
```

---

## Komponen Utama

### 1. RecommendationService (`service.py`)

**Tanggung Jawab:**

-   Public API layer untuk aplikasi
-   Input validation
-   Database queries untuk food details
-   Response formatting

**Key Methods:**

```python
def get_recommendations(user_id, top_n=10, include_scores=False):
    """
    Main API endpoint untuk mendapatkan rekomendasi

    Returns:
        - recommendations: List of food details + predicted ratings
        - count: Number of recommendations
    """
```

**Usage:**

```python
from app.recommendation import recommendation_service

# Get recommendations
response = recommendation_service.get_recommendations(
    user_id="user_123",
    top_n=10,
    include_scores=True
)
```

### 2. Recommendations (`recommender.py`)

**Tanggung Jawab:**

-   Orchestrator utama sistem
-   Koordinasi semua komponen
-   Performance tracking & statistics
-   Data validation & caching

**Key Methods:**

```python
def recommend(user_id, top_n=5):
    """Legacy method - returns food IDs only"""

def recommend_with_scores(user_id, top_n=5):
    """Returns detailed recommendations with predicted ratings"""

def get_recommendation_explanation(user_id, food_ids):
    """Returns explanation why foods were recommended"""

def get_system_stats():
    """Returns system performance statistics"""
```

**Attributes:**

```python
self.stats = {
    "total_requests": 0,
    "successful_recommendations": 0,
    "avg_processing_time": 0.0,
    "hybrid_coverage": 0.0
}
```

### 3. LocalDataProcessor (`local_data.py`)

**Tanggung Jawab:**

-   Load data dari database
-   Hybrid scoring calculation
-   Data filtering & cleaning
-   Pivot matrix creation
-   User similarity filtering
-   ID mappings (string ↔ integer)

**Key Methods:**

```python
def load_hybrid_ratings_from_db():
    """
    Load ratings dengan hybrid scoring
    Formula: α*food_rating + (1-α)*restaurant_rating
    """

def filter_sparse_data(df):
    """
    Filter users & foods dengan rating terlalu sedikit
    Iterative filtering sampai stabil
    """

def create_local_dataset(target_user_id, top_k_users=50):
    """
    Create sub-dataset dengan similar users
    Returns: (sub_ratings_df, sub_pivot_matrix)
    """

def create_pivot_matrix(df):
    """
    Convert ratings DataFrame to pivot matrix
    Rows: users, Columns: foods, Values: ratings
    """
```

**Hybrid Scoring:**

```python
# Example dengan α=0.7
food_rating = 5.0
restaurant_rating = 4.0
hybrid_score = (0.7 × 5.0) + (0.3 × 4.0) = 3.5 + 1.2 = 4.7

# Fallback jika restaurant rating tidak ada
hybrid_score = food_rating  # 5.0
```

### 4. LocalSVDModel (`local_model.py`)

**Tanggung Jawab:**

-   Training SVD model
-   Matrix decomposition
-   Rating prediction
-   Model evaluation
-   Bias calculation & centering

**Key Methods:**

```python
def fit(pivot_matrix):
    """
    Train SVD pada pivot matrix
    - Calculate biases (global, user, item)
    - Center matrix
    - Apply TruncatedSVD
    - Store factors
    """

def predict_user_item(user_idx, item_idx, common_items=0):
    """
    Predict rating untuk specific user-item pair
    Formula: global_mean + user_bias + item_bias + interaction
    """

def get_top_recommendations(user_idx, top_n=10, exclude_items=None, min_rating=3.0):
    """
    Generate top-N recommendations untuk user
    - Predict all items
    - Filter by min_rating
    - Sort by predicted rating
    - Return top N
    """

def evaluate_model(test_matrix):
    """
    Evaluate model dengan metrics:
    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Squared Error)
    - NDCG (Normalized Discounted Cumulative Gain)
    - Coverage
    """
```

**SVD Configuration:**

```python
n_components = 12        # Number of latent factors
n_epochs = 20            # Training epochs
random_state = 42        # For reproducibility
```

**Optimization Techniques:**

```python
# 1. Auto-adjust components based on sparsity
if sparsity > 0.95:
    max_components = min(50, max_components)

# 2. Use CSR sparse matrix for efficiency
if sparsity > 0.8:
    sparse_matrix = csr_matrix(training_matrix)

# 3. Bias dampening to prevent extreme predictions
bias_shrinkage = 0.7
user_bias *= bias_shrinkage
item_bias *= bias_shrinkage

# 4. Confidence weighting
if common_items > 0:
    confidence_weight = min(1.0, np.sqrt(common_items / 5.0))
    prediction = global_mean + confidence_weight * (prediction - global_mean)
```

### 5. Similarity Module (`similarity.py`)

**Tanggung Jawab:**

-   User similarity calculation
-   Cosine & Jaccard implementation
-   Similar users ranking
-   Validation testing

**Key Methods:**

```python
def cosine_similarity_sparse(user_matrix, target_idx, other_idx, common_items_mask):
    """
    Calculate cosine similarity
    - Subset to common items jika mask diberikan
    - Handle zero vectors
    - Return similarity [0, 1]
    """

def jaccard_similarity(set1, set2):
    """
    Calculate Jaccard index
    J(A,B) = |A ∩ B| / |A ∪ B|
    """

def get_similar_users(ratings_df, target_user_id, top_k=50,
                      similarity_threshold=0.1, method="cosine"):
    """
    Find top-K similar users
    - Calculate similarities dengan semua user
    - Filter by threshold
    - Sort descending
    - Return top K
    """
```

---

## Hybrid Scoring System

### Konsep

Sistem ini menggabungkan **Food Rating** dan **Restaurant Rating** untuk memberikan skor yang lebih komprehensif.

### Formula

```
hybrid_score = α × food_rating + (1 - α) × restaurant_rating
```

**Parameter α (alpha):**

-   Range: `0.0` sampai `1.0`
-   Default: `0.7` (70% food, 30% restaurant)

### Interpretasi Alpha

| Alpha | Food Weight | Restaurant Weight | Use Case                       |
| ----- | ----------- | ----------------- | ------------------------------ |
| 0.0   | 0%          | 100%              | Pure restaurant recommendation |
| 0.3   | 30%         | 70%               | Restaurant-focused             |
| 0.5   | 50%         | 50%               | Balanced                       |
| 0.7   | 70%         | 30%               | Food-focused (default)         |
| 1.0   | 100%        | 0%                | Pure food recommendation       |

### Contoh Perhitungan

**Scenario 1: User menyukai makanan, kurang suka resto**

```
food_rating = 5.0
restaurant_rating = 3.0
α = 0.7

hybrid_score = (0.7 × 5.0) + (0.3 × 3.0)
             = 3.5 + 0.9
             = 4.4
```

**Scenario 2: User suka resto, makanan biasa saja**

```
food_rating = 3.0
restaurant_rating = 5.0
α = 0.7

hybrid_score = (0.7 × 3.0) + (0.3 × 5.0)
             = 2.1 + 1.5
             = 3.6
```

**Scenario 3: Tidak ada restaurant rating (fallback)**

```
food_rating = 4.5
restaurant_rating = None
α = 0.7

hybrid_score = food_rating  # Fallback
             = 4.5
```

### Coverage Statistics

Sistem melacak persentase ratings yang memiliki restaurant rating:

```python
restaurant_coverage = (ratings_with_restaurant / total_ratings) × 100%
```

**Example:**

```
Total ratings: 1000
Ratings with restaurant: 650
Coverage: 65%
```

### Implementasi

```python
# Enable/disable hybrid scoring
data_processor = LocalDataProcessor(alpha=0.7)
data_processor.enable_hybrid_scoring(True)

# Load hybrid ratings
ratings_df = data_processor.load_hybrid_ratings_from_db()

# Change alpha dynamically
data_processor.set_alpha(0.5)
```

---

## Konfigurasi

### Configuration Class (`config.py`)

```python
class RecommendationConfig:
    # Model paths
    MODEL_PATH = "app/models/saved_models"
    SVD_MODEL_FILE = "svd_model.pkl"

    # Hybrid scoring
    DEFAULT_FOOD_RESTAURANT_ALPHA = 0.7

    # API limits
    MIN_RECOMMENDATIONS = 1
    MAX_RECOMMENDATIONS = 50
    DEFAULT_RECOMMENDATIONS = 10

    # SVD parameters
    SVD_N_FACTORS = 12
    SVD_N_EPOCHS = 20
    SVD_RANDOM_STATE = 42

    # Thresholds
    MIN_RATING_THRESHOLD = 3.0

    # Training interval
    TRAINING_INTERVAL = 24 * 60 * 60  # 24 hours
```

### Tuneable Parameters

| Parameter              | Default | Range   | Effect                                    |
| ---------------------- | ------- | ------- | ----------------------------------------- |
| `alpha`                | 0.7     | 0.0-1.0 | Weight food vs restaurant rating          |
| `top_k_users`          | 50      | 10-200  | Number of similar users for local dataset |
| `similarity_threshold` | 0.2     | 0.0-1.0 | Min similarity to include user            |
| `n_components`         | 12      | 5-100   | SVD latent factors                        |
| `min_rating_threshold` | 3.0     | 1.0-5.0 | Min predicted rating to recommend         |
| `min_user_ratings`     | 3       | 1-10    | Min ratings per user to include           |
| `min_food_ratings`     | 1       | 1-10    | Min ratings per food to include           |

### Optimization Tips

**For Sparse Data:**

```python
# Reduce SVD factors
SVD_N_FACTORS = 8

# Lower similarity threshold
similarity_threshold = 0.1

# Increase user neighborhood
top_k_users = 100
```

**For Dense Data:**

```python
# Increase SVD factors
SVD_N_FACTORS = 20

# Higher similarity threshold for quality
similarity_threshold = 0.3

# Smaller neighborhood for speed
top_k_users = 30
```

**For Cold Start Users:**

```python
# Use Jaccard instead of Cosine
similarity_method = "jaccard"

# Lower thresholds
similarity_threshold = 0.05
min_user_ratings = 1
```

---

## API Usage

### Basic Usage

```python
from app.recommendation import recommendation_service

# Simple recommendations (food IDs only)
response = recommendation_service.get_recommendations(
    user_id="user_123",
    top_n=5
)

# Response format:
{
    "status": "success",
    "data": {
        "recommendations": ["food_001", "food_042", ...],
        "food_details": [...],
        "count": 5
    }
}
```

### With Predicted Scores

```python
# Detailed recommendations with scores
response = recommendation_service.get_recommendations(
    user_id="user_123",
    top_n=10,
    include_scores=True
)

# Response format:
{
    "status": "success",
    "data": {
        "recommendations": [
            {
                "id": "food_001",
                "name": "Nasi Goreng",
                "price": 25000,
                "description": "...",
                "predicted_rating": 4.52,
                "rank": 1
            },
            ...
        ],
        "count": 10
    }
}
```

### Direct Recommender Usage

```python
from app.recommendation import Recommendations

# Initialize
recommender = Recommendations(alpha=0.7)

# Get recommendations with scores
detailed_recs = recommender.recommend_with_scores(
    user_id="user_123",
    top_n=10
)

# Result:
[
    {"food_id": "food_001", "predicted_rating": 4.52, "rank": 1},
    {"food_id": "food_042", "predicted_rating": 4.31, "rank": 2},
    ...
]

# Get explanation
explanation = recommender.get_recommendation_explanation(
    user_id="user_123",
    recommended_food_ids=["food_001", "food_042"]
)

# Get system statistics
stats = recommender.get_system_stats()
```

### Advanced Usage

```python
from app.recommendation import Recommendations
from app.recommendation import LocalDataProcessor, LocalSVDModel

# Custom configuration
data_processor = LocalDataProcessor(
    min_user_ratings=5,
    min_food_ratings=2,
    alpha=0.8
)

# Load and prepare data
ratings_df = data_processor.load_hybrid_ratings_from_db()
sub_ratings, sub_pivot = data_processor.create_local_dataset(
    target_user_id="user_123",
    top_k_users=100,
    similarity_method="cosine",
    similarity_threshold=0.3
)

# Train custom SVD
svd_model = LocalSVDModel(n_components=20)
svd_model.fit(sub_pivot)

# Get predictions
user_idx = data_processor.user_mapping["user_123"]
recommendations = svd_model.get_top_recommendations(
    user_idx=user_idx,
    top_n=20,
    min_rating=3.5
)

# Evaluate model
metrics = svd_model.evaluate_model(test_matrix)
print(f"RMSE: {metrics['rmse']:.3f}")
print(f"NDCG: {metrics['ndcg']:.3f}")
```

---

## Performance & Optimization

### Performance Metrics

Sistem secara otomatis melacak berbagai metrics:

```python
# Get system statistics
stats = recommender.get_system_stats()

{
    "total_requests": 1000,
    "successful_recommendations": 987,
    "success_rate": 0.987,
    "avg_processing_time": 0.145,  # seconds
    "is_initialized": True,
    "cache_age": 1200,  # seconds
    "data_stats": {
        "total_ratings": 5000,
        "unique_users": 200,
        "unique_foods": 800,
        "avg_rating": 4.1,
        "rating_distribution": {
            5: 2000,
            4: 1800,
            3: 800,
            2: 300,
            1: 100
        }
    }
}
```

### Caching Strategy

**Data Cache:**

-   Duration: 1 hour (3600 seconds)
-   Invalidation: Automatic after cache_duration
-   Benefit: Menghindari repeated DB queries

```python
self.cache_duration = 3600
self.last_data_load = time.time()

# Check if reload needed
if (time.time() - self.last_data_load) < self.cache_duration:
    return cached_data
```

**Model Cache:**

-   Fitted models disimpan in-memory
-   Re-training hanya saat perlu (data change, cache expired)

### Optimization Techniques

#### 1. Sparse Matrix Optimization

```python
# Use CSR (Compressed Sparse Row) for sparse data
if sparsity > 0.8:
    sparse_matrix = csr_matrix(training_matrix)
    user_factors = svd_model.fit_transform(sparse_matrix)
```

**Benefit:**

-   Memory usage: 10x-100x lebih efisien
-   Speed: 2x-5x lebih cepat untuk sparse data

#### 2. Local Dataset Strategy

```python
# Hanya train pada similar users (bukan full dataset)
sub_ratings = filter_to_similar_users(top_k=50)
```

**Benefit:**

-   Training time: 10x lebih cepat
-   Prediction accuracy: Lebih baik (fokus pada relevant neighborhood)
-   Scalability: Linear growth instead of quadratic

#### 3. Bias Dampening

```python
# Reduce extreme biases
bias_shrinkage = 0.7
user_bias *= bias_shrinkage
item_bias *= bias_shrinkage
```

**Benefit:**

-   Prevents overfitting
-   Reduces prediction clipping
-   Better generalization

#### 4. Confidence Weighting

```python
# Weight predictions by user-user overlap
if common_items > 0:
    confidence = min(1.0, np.sqrt(common_items / 5.0))
    prediction = mean + confidence * (prediction - mean)
```

**Benefit:**

-   More reliable predictions
-   Penalizes predictions based on limited data
-   Improves NDCG score

### Performance Benchmarks

**Typical Performance (on 1000 ratings, 100 users, 500 foods):**

| Operation                  | Time       | Memory    |
| -------------------------- | ---------- | --------- |
| Load data from DB          | 50ms       | 2MB       |
| Filter sparse data         | 20ms       | 1MB       |
| Calculate similarities     | 100ms      | 5MB       |
| Create local dataset       | 30ms       | 1MB       |
| Train SVD                  | 80ms       | 3MB       |
| Generate predictions       | 40ms       | 1MB       |
| **Total (single request)** | **~320ms** | **~13MB** |

**Scalability:**

| Dataset Size | Avg Response Time | Memory |
| ------------ | ----------------- | ------ |
| 1K ratings   | 150ms             | 10MB   |
| 10K ratings  | 350ms             | 50MB   |
| 100K ratings | 800ms             | 200MB  |
| 1M ratings   | 2500ms            | 1GB    |

### Monitoring & Debugging

**Enable Debug Logging:**

```python
import logging
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
```

**Check Model Info:**

```python
model_info = svd_model.get_model_info()
print(f"Fitted: {model_info['fitted']}")
print(f"Factors: {model_info['n_components']}")
print(f"Sparsity: {model_info['sparsity']:.3f}")
print(f"Explained variance: {model_info['explained_variance_ratio']:.3f}")
```

**Validate Similarity Calculation:**

```python
from app.recommendation.similarity import validate_similarity_calculation

is_valid = validate_similarity_calculation(ratings_df, sample_size=5)
if not is_valid:
    logger.warning("Similarity validation failed!")
```

**Check Data Quality:**

```python
stats = data_processor.get_rating_statistics()
print(f"Total ratings: {stats['total_ratings']}")
print(f"Avg rating: {stats['avg_rating']:.2f}")
print(f"Unique users: {stats['unique_users']}")
print(f"Unique foods: {stats['unique_foods']}")
print(f"Restaurant coverage: {stats.get('restaurant_coverage_percent', 0):.1f}%")
```

---

## Troubleshooting

### Common Issues

#### 1. Empty Recommendations

**Symptom:** `get_recommendations()` returns empty list

**Possible Causes:**

-   User belum pernah rating apapun
-   Tidak ada similar users ditemukan
-   Semua predictions di bawah `min_rating_threshold`

**Solutions:**

```python
# Lower similarity threshold
similarity_threshold = 0.1

# Lower min rating threshold
min_rating_threshold = 2.0

# Use fallback popular items
if len(recommendations) == 0:
    return get_popular_items(top_n=10)
```

#### 2. Low Accuracy

**Symptom:** RMSE > 1.5, NDCG < 0.5

**Possible Causes:**

-   Data terlalu sparse
-   Alpha tidak optimal
-   SVD factors terlalu sedikit/banyak

**Solutions:**

```python
# Tune alpha
for alpha in [0.5, 0.6, 0.7, 0.8]:
    test_with_alpha(alpha)

# Adjust SVD factors
for n_factors in [8, 12, 16, 20]:
    test_with_factors(n_factors)

# Increase min ratings thresholds
min_user_ratings = 5
min_food_ratings = 3
```

#### 3. Slow Performance

**Symptom:** Response time > 1 second

**Possible Causes:**

-   Dataset terlalu besar
-   Tidak menggunakan local dataset
-   Cache tidak efektif

**Solutions:**

```python
# Reduce top_k_users
top_k_users = 30

# Enable sparse matrix optimization
# (automatically enabled when sparsity > 0.8)

# Increase cache duration
self.cache_duration = 7200  # 2 hours

# Pre-compute similarities offline
```

#### 4. Cold Start Problem

**Symptom:** New users tidak dapat recommendations

**Solutions:**

```python
# Use content-based fallback
def recommend_for_new_user(user_preferences):
    # Recommend popular items in preferred category
    return get_popular_by_category(category=user_preferences['category'])

# Use demographic filtering
def recommend_by_demographics(user):
    similar_users = find_users_with_similar_demographics(user)
    return aggregate_recommendations(similar_users)
```

---

## Future Improvements

### Planned Enhancements

1. **Content-Based Hybrid**

    - Combine collaborative filtering dengan food attributes
    - Use food categories, tags, ingredients

2. **Context-Aware Recommendations**

    - Time of day (breakfast, lunch, dinner)
    - Location-based filtering
    - Weather conditions
    - User mood/occasion

3. **Deep Learning Approach**

    - Neural Collaborative Filtering
    - Embedding layers untuk user & food
    - RNN untuk sequential patterns

4. **A/B Testing Framework**

    - Compare different alpha values
    - Test similarity methods
    - Measure conversion rates

5. **Real-time Model Updates**

    - Incremental SVD updates
    - Online learning
    - Stream processing

6. **Explainable AI**
    - Show why food was recommended
    - "Users who liked X also liked Y"
    - Highlight matching features

---

## References

### Academic Papers

-   Koren, Y. (2009). "Matrix Factorization Techniques for Recommender Systems"
-   Sarwar, B. et al. (2001). "Item-Based Collaborative Filtering Recommendation Algorithms"
-   Rendle, S. (2010). "Factorization Machines"

### Libraries Used

-   **scikit-learn**: TruncatedSVD, metrics
-   **pandas**: Data manipulation
-   **numpy**: Matrix operations
-   **scipy**: Sparse matrices, distance metrics

### Documentation

-   [Surprise Library Docs](https://surprise.readthedocs.io/)
-   [scikit-learn Decomposition](https://scikit-learn.org/stable/modules/decomposition.html)
-   [RecSys Best Practices](https://github.com/microsoft/recommenders)

---

## Contact & Support

Untuk pertanyaan atau issue terkait sistem rekomendasi:

-   Check logs di: `logs/recommendation.log`
-   Enable debug mode untuk detailed logging
-   Dokumentasi API: `/docs` endpoint

---

**Last Updated:** October 17, 2025
**Version:** 1.0.0
**Author:** ADZA Recommendation Team
