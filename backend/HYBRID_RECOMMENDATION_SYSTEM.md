# Sistem Rekomendasi Hybrid dengan Collaborative Filtering + SVD

## Overview

Sistem rekomendasi hybrid yang menggabungkan rating restaurant dan rating makanan menggunakan collaborative filtering dengan SVD (Singular Value Decomposition). Sistem ini didesain dengan pendekatan 4-step yang jelas dan menggunakan parameter alpha untuk mengontrol bobot antara kedua kriteria penilaian.

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                 Hybrid Recommendation System                │
├─────────────────────────────────────────────────────────────┤
│  1. Food Rating SVD Model    │  2. Restaurant Rating SVD Model │
│     (Collaborative Filtering)│     (Collaborative Filtering)   │
│                              │                                │
│  ┌─────────────────────────┐ │ ┌─────────────────────────────┐ │
│  │ User-Food Rating Matrix │ │ │ User-Restaurant Rating Matrix│ │
│  │ SVD(n_factors=100,      │ │ │ SVD(n_factors=100,          │ │
│  │     n_epochs=20)        │ │ │     n_epochs=20)            │ │
│  └─────────────────────────┘ │ └─────────────────────────────┘ │
│             │                │              │                 │
│             ▼                │              ▼                 │
│  ┌─────────────────────────┐ │ ┌─────────────────────────────┐ │
│  │   Food Score (0-1)      │ │ │  Restaurant Score (0-1)     │ │
│  └─────────────────────────┘ │ └─────────────────────────────┘ │
│                              │                                │
├─────────────────────────────────────────────────────────────┤
│                    Alpha Parameter Weighting                 │
│                                                             │
│    Hybrid Score = α × Food Score + (1-α) × Restaurant Score │
│                                                             │
│    α = 0.7 (default) → 70% food, 30% restaurant            │
│    α = 1.0           → 100% food, 0% restaurant            │
│    α = 0.0           → 0% food, 100% restaurant            │
└─────────────────────────────────────────────────────────────┘
```

## 4-Step Implementation

### Step 1: Import Modules

```python
def _import_modules(self):
    """Validasi dan import dependencies yang diperlukan"""
    - import surprise (untuk SVD)
    - import sklearn (untuk metrics)
    - import pandas (untuk data processing)
    - import numpy (untuk komputasi numerik)
```

### Step 2: Prepare Data

```python
def _prepare_data(self):
    """Persiapan dan pembersihan data rating"""
    - Ambil data FoodRating dari database
    - Ambil data RestaurantRating dari database
    - Konversi ke DataFrame pandas
    - Bersihkan data (hapus null, validasi range 1-5)
    - Log informasi data yang berhasil diproses
```

### Step 3: Train and Test Models

```python
def _train_and_test_models(self):
    """Pelatihan model SVD untuk kedua jenis rating"""
    - Buat dataset Surprise untuk food ratings
    - Buat dataset Surprise untuk restaurant ratings
    - Latih SVD model untuk food ratings
    - Latih SVD model untuk restaurant ratings
    - Konfigurasi: n_factors=100, n_epochs=20, random_state=42
```

### Step 4: Validate Models (RMSE & MAE)

```python
def _validate_models(self):
    """Validasi model menggunakan cross-validation"""
    - Cross-validation 5-fold untuk food model
    - Cross-validation 5-fold untuk restaurant model
    - Hitung RMSE (Root Mean Square Error)
    - Hitung MAE (Mean Absolute Error)
    - Return metrics dengan standard deviation
```

### Step 5: Predict (Bonus)

```python
def predict_hybrid_recommendations(self, user_id, limit=10):
    """Generate rekomendasi hybrid"""
    - Prediksi rating food untuk makanan yang belum di-rate user
    - Prediksi rating restaurant untuk restaurant makanan tersebut
    - Normalisasi kedua score ke range 0-1
    - Hitung hybrid score dengan parameter alpha
    - Urutkan berdasarkan hybrid score dan ambil top-N
```

## Key Features

### 1. **Hybrid Scoring dengan Alpha Parameter**

```python
# Normalisasi scores
food_normalized = (food_score - 1.0) / 4.0      # 1-5 → 0-1
restaurant_normalized = (restaurant_score - 1.0) / 4.0

# Hybrid scoring
hybrid_score = (alpha * food_normalized) + ((1 - alpha) * restaurant_normalized)
final_rating = 1.0 + (hybrid_score * 4.0)       # 0-1 → 1-5
```

### 2. **Robust Error Handling**

-   Validasi data setiap step
-   Fallback mechanisms
-   Comprehensive logging
-   Graceful degradation

### 3. **Comprehensive Validation**

-   RMSE dan MAE metrics
-   Cross-validation untuk kedua model
-   Standard deviation untuk confidence intervals
-   Performance benchmarking untuk berbagai alpha values

### 4. **Flexibility**

-   Configurable alpha parameter (0-1)
-   Adjustable SVD parameters
-   Customizable recommendation limits
-   Easy integration dengan existing codebase

## Usage Examples

### Basic Usage

```python
# Create and train system
system = HybridRecommendationSystem(alpha=0.7)
results = system.train_full_system()

# Generate recommendations
recommendations = system.predict_hybrid_recommendations(user_id="user123", limit=10)
```

### Alpha Parameter Testing

```python
# Test different weightings
for alpha in [0.3, 0.5, 0.7, 0.9]:
    system = HybridRecommendationSystem(alpha=alpha)
    system.train_full_system()
    # Compare performance metrics
```

### Integration dengan Existing Service

```python
# Compatibility wrapper
recommendations = RecommendationService.get_recommendations(
    user_id="user123",
    n=10,
    alpha=0.7
)
```

## Performance Metrics

Sistem menghasilkan metrics berikut untuk evaluasi:

### Food Model Validation

-   **RMSE**: Root Mean Square Error
-   **MAE**: Mean Absolute Error
-   **Standard Deviation**: Untuk confidence intervals

### Restaurant Model Validation

-   **RMSE**: Root Mean Square Error
-   **MAE**: Mean Absolute Error
-   **Standard Deviation**: Untuk confidence intervals

### Example Output

```
Food Model - RMSE: 0.8234 ± 0.0456
Food Model - MAE: 0.6234 ± 0.0345
Restaurant Model - RMSE: 0.7845 ± 0.0523
Restaurant Model - MAE: 0.5987 ± 0.0398
```

## File Structure

```
app/recommendation/
├── service.py                    # Main hybrid recommendation system
├── __init__.py                   # Package exports
└── config.py                     # Configuration parameters

test_hybrid_with_context.py       # Comprehensive test suite
alpha_benchmark_results.json      # Performance benchmarking results
```

## Configuration

### SVD Model Parameters

```python
n_factors = 100      # Jumlah faktor laten
n_epochs = 20        # Jumlah iterasi training
random_state = 42    # Untuk reproducibility
```

### Alpha Parameter Guidelines

-   **α = 0.7** (recommended): Balanced approach, prioritas pada food rating
-   **α = 0.9**: Heavy focus on food ratings
-   **α = 0.5**: Equal weighting
-   **α = 0.3**: Heavy focus on restaurant ratings

## Testing & Validation

### Run Tests

```bash
cd /home/labubu/Projects/adza/backend
source .venv/bin/activate
python test_hybrid_with_context.py
```

### Test Coverage

1. ✅ 4-step process validation
2. ✅ Different alpha parameter testing
3. ✅ Model validation with RMSE/MAE
4. ✅ User prediction testing
5. ✅ Performance benchmarking

## Advantages

1. **Rinkas tapi Powerful**: Implementasi concise dengan fitur lengkap
2. **Class-based Design**: OOP approach untuk maintainability
3. **Comprehensive Validation**: RMSE & MAE metrics dengan cross-validation
4. **Flexible Weighting**: Alpha parameter untuk fine-tuning
5. **Production Ready**: Error handling dan compatibility layer
6. **Well Documented**: Clear step-by-step process dan extensive documentation

## Future Enhancements

1. **Content-based Features**: Tambahkan food categories, price ranges
2. **Temporal Dynamics**: Considerate time-based preferences
3. **Cold Start Problem**: Handle new users/items
4. **Advanced Algorithms**: Matrix Factorization variants, Deep Learning
5. **Real-time Updates**: Incremental learning capabilities

## Dependencies

```txt
scikit-surprise==1.1.4    # SVD implementation
scikit-learn==1.4.0       # Metrics dan preprocessing
pandas==2.2.3             # Data manipulation
numpy==1.26.4             # Numerical computations
Flask-SQLAlchemy==3.1.1   # Database ORM
```

## Conclusion

Sistem rekomendasi hybrid ini berhasil mengimplementasikan 4-step process yang diminta dengan pendekatan yang ringkas namun powerful. Menggunakan class-based design untuk maintainability dan flexibility, serta dilengkapi dengan comprehensive validation menggunakan RMSE dan MAE metrics. Parameter alpha memungkinkan fine-tuning balance antara food ratings dan restaurant ratings sesuai kebutuhan bisnis.
