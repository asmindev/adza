# Dokumentasi Per File - Sistem Rekomendasi

## 📁 Struktur File

```
recommendation/
├── __init__.py          # Entry point & exports
├── config.py            # Konfigurasi & konstanta
├── service.py           # Public API layer
├── recommender.py       # Orchestrator utama
├── local_data.py        # Data processing & filtering
├── local_model.py       # SVD model & predictions
└── similarity.py        # User similarity calculations
```

---

## 1. `__init__.py`

### 📌 Fungsi Utama

**Entry point package** - Mengexpose komponen utama untuk digunakan aplikasi

### 🎯 Tugas

-   ✅ Import class utama dari submodules
-   ✅ Export public API untuk aplikasi
-   ✅ Menyediakan interface yang clean

### 📦 Exports

```python
Recommendations          # Main recommender class
RecommendationService    # Public API service
recommendation_service   # Singleton instance (ready to use)
```

### 💻 Usage

```python
from app.recommendation import recommendation_service
```

---

## 2. `config.py`

### 📌 Fungsi Utama

**Configuration management** - Centralized settings & constants

### 🎯 Tugas

-   ✅ Define path untuk model storage
-   ✅ Set parameter default (alpha, limits, thresholds)
-   ✅ Configure SVD hyperparameters
-   ✅ Initialize model directory

### ⚙️ Key Constants

| Constant                        | Value                     | Keterangan                       |
| ------------------------------- | ------------------------- | -------------------------------- |
| `MODEL_PATH`                    | `app/models/saved_models` | Folder simpan model              |
| `DEFAULT_FOOD_RESTAURANT_ALPHA` | `0.7`                     | Weight food (70%) vs resto (30%) |
| `MIN_RECOMMENDATIONS`           | `1`                       | Min jumlah rekomendasi           |
| `MAX_RECOMMENDATIONS`           | `50`                      | Max jumlah rekomendasi           |
| `SVD_N_FACTORS`                 | `12`                      | Latent factors SVD               |
| `SVD_N_EPOCHS`                  | `20`                      | Training epochs                  |
| `MIN_RATING_THRESHOLD`          | `3.0`                     | Min predicted rating             |
| `TRAINING_INTERVAL`             | `86400`                   | .l;.24 jam (seconds)             |

### 💻 Usage

```python
from app.recommendation.config import RecommendationConfig

RecommendationConfig.initialize()
alpha = RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA
```

---

## 3. `service.py`

### 📌 Fungsi Utama

**Public API Layer** - Interface antara aplikasi dan recommendation engine

### 🎯 Tugas

-   ✅ Validate input (user_id, top_n)
-   ✅ Check user existence di database
-   ✅ Call recommender engine
-   ✅ Query food details dari DB
-   ✅ Merge recommendations dengan food info
-   ✅ Format response JSON
-   ✅ Error handling

### 🔧 Main Method

```python
def get_recommendations(user_id, top_n=10, include_scores=False)
```

**Parameters:**

-   `user_id` (str): ID user yang mau dapat rekomendasi
-   `top_n` (int): Jumlah rekomendasi (1-50)
-   `include_scores` (bool): Include predicted rating atau tidak

**Returns:**

```python
{
  "status": "success",
  "data": {
    "recommendations": [...],  # List of foods dengan details
    "count": 10
  }
}
```

### 📊 Response Format

**Tanpa scores:**

```python
{
  "recommendations": ["food_id_1", "food_id_2", ...],
  "food_details": [{...}, {...}],
  "count": 5
}
```

**Dengan scores:**

```python
{
  "recommendations": [
    {
      "id": "food_001",
      "name": "Nasi Goreng",
      "price": 25000,
      "predicted_rating": 4.52,
      "rank": 1
    },
    ...
  ],
  "count": 5
}
```

### 💻 Usage

```python
from app.recommendation import recommendation_service

response = recommendation_service.get_recommendations(
    user_id="user_123",
    top_n=10,
    include_scores=True
)
```

---

## 4. `recommender.py`

### 📌 Fungsi Utama

**Orchestrator Utama** - Koordinasi semua komponen recommendation system

### 🎯 Tugas

-   ✅ Initialize data processor & SVD model
-   ✅ Load & validate data dari DB
-   ✅ Cache management (1 hour duration)
-   ✅ Coordinate similarity calculation
-   ✅ Coordinate local dataset creation
-   ✅ Coordinate SVD training
-   ✅ Generate predictions
-   ✅ Post-processing (ranking, filtering)
-   ✅ Performance tracking & statistics
-   ✅ Provide explanations

### 🔧 Key Methods

#### `recommend(user_id, top_n=5)`

**Legacy method** - Returns food IDs only

```python
Returns: ["food_001", "food_042", "food_087", ...]
```

#### `recommend_with_scores(user_id, top_n=5)`

**Modern method** - Returns detailed recommendations

```python
Returns: [
  {"food_id": "food_001", "predicted_rating": 4.52, "rank": 1},
  {"food_id": "food_042", "predicted_rating": 4.31, "rank": 2},
  ...
]
```

#### `get_recommendation_explanation(user_id, food_ids)`

**Explainability** - Why foods were recommended

```python
Returns: {
  "method": "collaborative_filtering_svd",
  "user_profile": {...},
  "model_info": {...}
}
```

#### `get_system_stats()`

**Monitoring** - System performance metrics

```python
Returns: {
  "total_requests": 1000,
  "successful_recommendations": 987,
  "success_rate": 0.987,
  "avg_processing_time": 0.145,
  "data_stats": {...}
}
```

### 📊 Statistics Tracking

```python
self.stats = {
    "total_requests": 0,
    "successful_recommendations": 0,
    "avg_processing_time": 0.0,
    "hybrid_coverage": 0.0
}
```

### 🔄 Process Flow

```
1. Load & validate data (dengan cache check)
2. Get user context (history, avg rating)
3. Create local dataset (similar users only)
4. Train SVD model on local data
5. Generate predictions
6. Filter & rank recommendations
7. Update statistics
8. Return results
```

### 💻 Usage

```python
from app.recommendation import Recommendations

recommender = Recommendations(alpha=0.7)
recs = recommender.recommend_with_scores(user_id="user_123", top_n=10)
stats = recommender.get_system_stats()
```

---

## 5. `local_data.py`

### 📌 Fungsi Utama

**Data Processing & Preparation** - Handle semua data manipulation

### 🎯 Tugas

-   ✅ Load ratings dari database (FoodRating + RestaurantRating)
-   ✅ Calculate hybrid scores (α*food + (1-α)*resto)
-   ✅ Filter sparse data (min ratings threshold)
-   ✅ Create pivot matrix (users × foods)
-   ✅ Find similar users (via Similarity module)
-   ✅ Create local sub-dataset
-   ✅ Generate ID mappings (string ↔ integer)
-   ✅ Provide data statistics

### 🔧 Key Methods

#### `load_hybrid_ratings_from_db()`

**Load & combine ratings**

```python
# Query FoodRating + Food (untuk dapat restaurant_id)
# Query RestaurantRating
# Match & calculate hybrid score
# Returns DataFrame: [user_id, food_id, rating, has_restaurant_rating]
```

**Hybrid Formula:**

```python
if restaurant_rating exists:
    score = (alpha × food_rating) + ((1-alpha) × restaurant_rating)
else:
    score = food_rating  # Fallback
```

#### `filter_sparse_data(df)`

**Remove low-quality data**

```python
# Filter users dengan ratings < min_user_ratings (default: 3)
# Filter foods dengan ratings < min_food_ratings (default: 1)
# Iterative filtering sampai stabil (max 5 iterations)
```

#### `create_pivot_matrix(df, binary=False)`

**Convert to matrix format**

```python
# Rows: user_id
# Columns: food_id
# Values: rating (or 1/0 if binary)
# Fill NaN dengan 0
```

#### `create_local_dataset(target_user_id, top_k_users=50, similarity_method="cosine", similarity_threshold=0.2)`

**Create sub-dataset for efficient training**

```python
1. Find similar users (call similarity.py)
2. Filter ratings to similar users only
3. Create sub-pivot matrix
4. Create ID mappings (for SVD)
Returns: (sub_ratings_df, sub_pivot_matrix)
```

#### `get_user_rated_foods(user_id)`

**Get user's rating history**

```python
Returns: ["food_001", "food_042", ...]  # Untuk exclude saat recommend
```

### 🔄 Attributes

```python
self.ratings_df = None              # Main ratings DataFrame
self.user_item_matrix = None        # Pivot matrix
self.user_mapping = {}              # user_id → integer index
self.food_mapping = {}              # food_id → integer index
self.reverse_user_mapping = {}      # integer → user_id
self.reverse_food_mapping = {}      # integer → food_id
self.alpha = 0.7                    # Hybrid scoring weight
self.use_hybrid_scoring = True      # Enable/disable hybrid
```

### 💻 Usage

```python
data_processor = LocalDataProcessor(alpha=0.7)
ratings_df = data_processor.load_hybrid_ratings_from_db()
sub_ratings, sub_pivot = data_processor.create_local_dataset(
    target_user_id="user_123",
    top_k_users=50
)
```

---

## 6. `local_model.py`

### 📌 Fungsi Utama

**SVD Model Training & Prediction** - Core machine learning component

### 🎯 Tugas

-   ✅ Prepare matrix (mean centering, bias calculation)
-   ✅ Train SVD model (TruncatedSVD)
-   ✅ Decompose matrix → user & item factors
-   ✅ Predict ratings untuk user-item pairs
-   ✅ Generate top-N recommendations
-   ✅ Evaluate model (MAE, RMSE, NDCG)
-   ✅ Handle sparse matrices efficiently

### 🔧 Key Methods

#### `fit(pivot_matrix)`

**Train SVD model**

```python
Process:
1. Calculate global_mean, user_means, item_means
2. Center matrix (subtract biases)
3. Apply TruncatedSVD (12 factors default)
4. Extract user_factors & item_factors
5. Calculate explained variance

Optimization:
- Auto-adjust components based on sparsity
- Use CSR sparse matrix if sparsity > 0.8
- Handle very sparse data (sparsity > 0.99)
```

#### `predict_user_item(user_idx, item_idx, common_items=0)`

**Predict single rating**

```python
Formula:
prediction = global_mean + user_bias + item_bias + interaction

Where:
- user_bias = (user_mean - global_mean) × 0.7  # dampening
- item_bias = (item_mean - global_mean) × 0.7  # dampening
- interaction = user_factors[user_idx] · item_factors[item_idx]
- confidence_weight applied if common_items > 0

Final: clip to [1.0, 5.0]
```

#### `get_top_recommendations(user_idx, top_n=10, exclude_items=None, min_rating=3.0)`

**Generate recommendations**

```python
1. Predict all items for user
2. Exclude already rated items
3. Filter by min_rating threshold
4. Sort by predicted rating (descending)
5. Return top N

Returns: [(item_idx, predicted_rating), ...]
```

#### `evaluate_model(test_matrix)`

**Model evaluation**

```python
Metrics:
- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)
- RMSE (Root MSE)
- NDCG@10 (Normalized Discounted Cumulative Gain)
- Coverage

Returns: {"mae": 0.65, "rmse": 0.83, "ndcg": 0.72, ...}
```

### 🔄 Attributes

```python
self.svd_model = None           # TruncatedSVD instance
self.is_fitted = False          # Training status
self.user_factors = None        # U matrix (users × k)
self.item_factors = None        # V^T matrix (k × items)
self.global_mean = 0.0          # Dataset average rating
self.user_means = None          # User bias array
self.item_means = None          # Item bias array
self.n_users = 0                # Number of users
self.n_items = 0                # Number of items
self.sparsity = 0.0             # 1 - (ratings / total_possible)
```

### ⚡ Optimizations

**1. Bias Dampening**

```python
# Reduce extreme biases by 30%
bias_shrinkage = 0.7
user_bias *= bias_shrinkage
item_bias *= bias_shrinkage
```

**2. Confidence Weighting**

```python
# Weight by user-user overlap
if common_items > 0:
    confidence = min(1.0, sqrt(common_items / 5.0))
    prediction = mean + confidence × (prediction - mean)
```

**3. Sparse Matrix**

```python
# Use CSR for efficiency
if sparsity > 0.8:
    sparse_matrix = csr_matrix(training_matrix)
```

### 💻 Usage

```python
svd_model = LocalSVDModel(n_components=12)
svd_model.fit(pivot_matrix)

# Predict single item
rating = svd_model.predict_user_item(user_idx=5, item_idx=10)

# Get recommendations
recs = svd_model.get_top_recommendations(
    user_idx=5,
    top_n=10,
    min_rating=3.0
)
```

---

## 7. `similarity.py`

### 📌 Fungsi Utama

**User Similarity Calculations** - Find users dengan selera mirip

### 🎯 Tugas

-   ✅ Calculate cosine similarity between users
-   ✅ Calculate jaccard similarity between users
-   ✅ Find top-K similar users
-   ✅ Filter by similarity threshold
-   ✅ Validate similarity calculations

### 🔧 Key Methods

#### `cosine_similarity_sparse(user_matrix, target_idx, other_idx, common_items_mask=None)`

**Cosine similarity calculation**

```python
Formula:
similarity = 1 - cosine_distance(vector1, vector2)

Process:
1. Extract user vectors from sparse matrix
2. Subset to common items (if mask provided)
3. Handle zero vectors
4. Calculate cosine distance
5. Convert to similarity [0, 1]

Focus: POLA RATING (angle between vectors)
```

**Example:**

```
User A: [5, 4, 0, 3, 0]
User B: [5, 5, 0, 4, 0]
Common items: [5,4,3] vs [5,5,4]
Cosine similarity = 0.98
```

#### `jaccard_similarity(set1, set2)`

**Jaccard index calculation**

```python
Formula:
J(A,B) = |A ∩ B| / |A ∪ B|

Process:
1. Calculate intersection size
2. Calculate union size
3. Return ratio [0, 1]

Focus: OVERLAP ITEMS yang di-rating
```

**Example:**

```
User A rated: {food1, food2, food3, food5}
User B rated: {food1, food2, food4, food6}
Intersection: {food1, food2} = 2
Union: {food1, food2, food3, food4, food5, food6} = 6
Jaccard = 2/6 = 0.33
```

#### `calculate_user_similarities(ratings_df, target_user_id, method="cosine", min_common_items=2)`

**Calculate with all users**

```python
Methods:
- "cosine": Calculate cosine similarity (default)
- "jaccard": Calculate jaccard similarity

Process:
1. Get target user's ratings
2. For each other user:
   - Check min common items
   - Calculate similarity
   - Store if > 0
3. Return dict: {user_id: similarity_score}
```

#### `get_similar_users(ratings_df, target_user_id, top_k=50, similarity_threshold=0.1, method="cosine")`

**Find top-K similar users**

```python
Process:
1. Calculate similarities dengan semua user
2. Filter by threshold
3. Sort descending by similarity
4. Take top K
5. Always include target user

Returns: [(user_id, similarity_score), ...]
```

#### `validate_similarity_calculation(ratings_df, sample_size=5)`

**Test & validate**

```python
Process:
1. Sample random users
2. Test cosine similarity
3. Test jaccard similarity
4. Test SVD on sample
5. Log results

Returns: True if all tests pass
```

### 📊 Method Comparison

| Aspect         | Cosine      | Jaccard      |
| -------------- | ----------- | ------------ |
| **Focus**      | Pola rating | Item overlap |
| **Speed**      | Medium      | Fast         |
| **Accuracy**   | High        | Medium       |
| **Use Case**   | Main method | Cold start   |
| **Min Common** | 2 items     | 2 items      |
| **Default**    | ✅ Yes      | ❌ No        |

### 💻 Usage

```python
from app.recommendation.similarity import get_similar_users

# Find similar users
similar_users = get_similar_users(
    ratings_df=df,
    target_user_id="user_123",
    top_k=50,
    similarity_threshold=0.2,
    method="cosine"
)

# Result: [("user_456", 0.85), ("user_789", 0.78), ...]
```

---

## 🔄 Alur Kerja Antar File

```
1. API Request
   └─> service.py: get_recommendations()

2. Validation & Setup
   └─> service.py: validate user, top_n
       └─> recommender.py: recommend_with_scores()

3. Data Loading
   └─> recommender.py: _load_and_validate_data()
       └─> local_data.py: load_hybrid_ratings_from_db()
           └─> Database query + hybrid scoring

4. Find Similar Users
   └─> local_data.py: create_local_dataset()
       └─> similarity.py: get_similar_users()
           └─> Calculate cosine similarity

5. Prepare Training Data
   └─> local_data.py: create_pivot_matrix()
       └─> local_data.py: create_id_mappings()

6. Train Model
   └─> local_model.py: fit(pivot_matrix)
       └─> TruncatedSVD + bias calculation

7. Generate Predictions
   └─> local_model.py: get_top_recommendations()
       └─> local_model.py: predict_user_item()

8. Post-Processing
   └─> recommender.py: convert indices to IDs
       └─> recommender.py: add ranks & scores

9. Enrich Results
   └─> service.py: _get_food_details()
       └─> Database query for food info

10. Return Response
    └─> service.py: success_response()
```

---

## 📊 Dependencies Antar File

```
config.py (standalone)
   ↓
   ├─> service.py (uses config)
   ├─> recommender.py (uses config)
   ├─> local_data.py (uses config)
   └─> local_model.py (uses config)

similarity.py (standalone helper)
   ↓
   └─> local_data.py (uses similarity)

local_data.py + similarity.py
   ↓
   └─> recommender.py (uses both)

local_model.py (standalone ML)
   ↓
   └─> recommender.py (uses model)

recommender.py (aggregator)
   ↓
   └─> service.py (public API)

service.py (entry point)
   ↓
   └─> __init__.py (exports)
```

---

## 🎯 Tugas Masing-Masing File (Ringkasan)

| File             | Primary Role        | Key Responsibility                                   |
| ---------------- | ------------------- | ---------------------------------------------------- |
| `__init__.py`    | **Entry Point**     | Export public interfaces                             |
| `config.py`      | **Configuration**   | Centralized settings & constants                     |
| `service.py`     | **Public API**      | Validate input, query DB, format response            |
| `recommender.py` | **Orchestrator**    | Coordinate all components, manage cache, track stats |
| `local_data.py`  | **Data Processor**  | Load, filter, transform, pivot data                  |
| `local_model.py` | **ML Engine**       | Train SVD, predict ratings, evaluate                 |
| `similarity.py`  | **Similarity Calc** | Find similar users via cosine/jaccard                |

---

**Summary:** Setiap file punya tanggung jawab spesifik dan bekerja sama untuk menghasilkan rekomendasi yang akurat dan efisien! 🚀
