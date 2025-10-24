# 📊 Detailed SVD Calculation - Documentation

## Overview

Script `manual_svd_detailed.py` menampilkan perhitungan SVD (Singular Value Decomposition) secara detail dengan 4 langkah analisis untuk sistem rekomendasi makanan.

## Target User

-   **Username**: `adza`
-   **Fokus**: Menampilkan bagaimana SVD bekerja step-by-step

## 4 Steps Analysis

### 📊 STEP 1: 20 Users Similarity Analysis

**Tujuan**: Tampilkan 20 users yang memiliki pola rating mirip dengan user 'adza'

**Breakdown**:

-   **15 Most Similar Users**: Users dengan cosine similarity tertinggi
-   **5 Least Similar Users**: Users dengan cosine similarity terendah

**Metrics Displayed**:

-   User ID (truncated)
-   User Name
-   Common Items (jumlah items yang sama-sama di-rating)
-   Similarity Score (0.0 - 1.0)
-   Category (Most/Least Similar)
-   Visual Bar Chart

**Example Output**:

```
Rank #1: Ella         - Similarity: 0.9952 (4 common items)
Rank #2: Nisa         - Similarity: 0.9950 (4 common items)
Rank #3: Osin         - Similarity: 0.9944 (4 common items)
Rank #4: Anggi        - Similarity: 0.9926 (4 common items)
...
Rank #62-#66: Users with 0.0000 similarity (no common items)
```

**Statistics**:

-   Total users compared
-   Average similarity
-   Max/Min similarity
-   Standard deviation

---

### 🔢 STEP 2: Detailed Similarity Calculation

**Tujuan**: Tampilkan perhitungan cosine similarity detail untuk 20 users yang dipilih

**Formula**:

```
similarity(u,v) = (u·v) / (||u|| × ||v||)

Where:
- u·v      = Dot product (Σ rᵢ·rⱼ)
- ||u||    = Euclidean norm of vector u (√Σrᵢ²)
- ||v||    = Euclidean norm of vector v (√Σrⱼ²)
```

**Columns Displayed**:

1. **User**: Nama user
2. **Dot Product**: Hasil perkalian dot product vectors
3. **||Target||**: Magnitude vector target user (adza)
4. **||User||**: Magnitude vector user lain
5. **Similarity**: Hasil cosine similarity
6. **Formula**: Perhitungan dalam format readable

**Example**:

```
User: Ella
Dot Product: 77.67
||Target||: 8.91
||User||: 8.76
Similarity: 0.9952
Formula: 77.67/(8.91×8.76)
```

---

### 🔬 STEP 3: SVD Decomposition

**Tujuan**: Dekomposisi matrix rating menggunakan SVD

**Matrix Input**:

-   **Users**: 21 users (target + 20 selected)
-   **Items**: N foods yang pernah di-rating
-   **Sparsity**: Persentase cell kosong dalam matrix

**SVD Formula**:

```
R = U × Σ × Vᵀ

Where:
- R: Rating matrix (21 × N)
- U: User-Feature matrix (21 × k)
- Σ: Diagonal singular values matrix (k × k)
- Vᵀ: Feature-Item matrix (k × N)
- k: Number of latent factors (default: 10)
```

**Process**:

1. **Mean Centering**: Subtract user mean from ratings
2. **SVD Decomposition**: Apply scipy.sparse.linalg.svds
3. **Sorting**: Sort by singular values (descending)

**Output Tables**:

#### 3.1 Singular Values (Σ)

Displays:

-   Factor number (σ1, σ2, ..., σk)
-   Singular value
-   Variance percentage (individual)
-   Cumulative variance percentage
-   Visual bar chart

**Example**:

```
σ1: 2.083451  (32.87% variance)  ████████░░
σ2: 1.744263  (23.04% variance)  ██████░░░░
σ3: 1.318145  (13.16% variance)  ███░░░░░░░
...
Total: 100% cumulative variance
```

#### 3.2 User-Feature Matrix (U)

Shows first 10 users × first 5 factors:

```
User     | F1      | F2      | F3      | F4      | F5
------------------------------------------------------------
Adza     | 0.0000  | -0.0000 | -0.0000 | -0.0000 | -0.8295
Ella     | 0.0000  | 0.0000  | 0.0000  | 0.0000  | 0.2296
...
```

**Interpretation**:

-   Each row = user's latent features
-   Each column = latent factor strength
-   Values indicate how much user aligns with each factor

#### 3.3 Feature-Item Matrix (Vᵀ)

Shows first 5 factors × first 10 items:

```
Factor | Item1  | Item2  | Item3  | Item4  | Item5 ...
---------------------------------------------------------
F1     | -0.102 | -0.118 | 0.099  | 0.085  | 0.614 ...
F2     | 0.510  | 0.056  | -0.181 | -0.333 | 0.321 ...
...
```

**Interpretation**:

-   Each row = latent factor's item weights
-   Each column = item's feature representation
-   Values show item-feature relationships

#### 3.4 Matrix Reconstruction

```
R̂ = U × Σ × Vᵀ + user_means
```

Reconstructed matrix contains predicted ratings for all user-item pairs.

---

### 🎯 STEP 4: Final Recommendations

**Tujuan**: Generate top 10 rekomendasi untuk user 'adza' dari hasil SVD

**Process**:

1. Extract target user's row from reconstructed matrix
2. Filter items NOT yet rated by user
3. Apply threshold (predicted rating ≥ 3.0)
4. Sort by predicted rating (descending)
5. Take top 10

**Recommendation Table**:

```
Rank | Food Name              | Price      | Predicted Rating | Stars
------------------------------------------------------------------------
#1   | NASI GORENG SEAFOOD    | Rp 35,000  | 4.55            | ⭐⭐⭐⭐⭐
#2   | BEEF BULGOGI           | Rp 37,850  | 4.51            | ⭐⭐⭐⭐⭐
#3   | Fire Chicken 8pcs      | Rp 224,000 | 4.50            | ⭐⭐⭐⭐⭐
...
```

**Statistics**:

-   Average predicted rating
-   Max predicted rating
-   Min predicted rating

---

## How to Run

### Basic Usage

```bash
cd /home/labubu/Projects/adza/backend
python app/recommendation/manual_svd_detailed.py
```

### View Specific Sections

```bash
# Step 1 only
python app/recommendation/manual_svd_detailed.py 2>&1 | grep -A 30 "STEP 1"

# Step 2 only
python app/recommendation/manual_svd_detailed.py 2>&1 | grep -A 25 "STEP 2"

# Step 3 only
python app/recommendation/manual_svd_detailed.py 2>&1 | grep -A 50 "STEP 3"

# Step 4 only
python app/recommendation/manual_svd_detailed.py 2>&1 | grep -A 20 "STEP 4"
```

### Save Output to File

```bash
python app/recommendation/manual_svd_detailed.py > svd_output.txt 2>&1
```

---

## Technical Details

### Dependencies

-   `numpy`: Matrix operations
-   `scipy.sparse.linalg.svds`: SVD decomposition
-   `rich`: Beautiful terminal output
-   `Flask`: App context for database access
-   `SQLAlchemy`: Database queries

### Database Models Used

-   `User`: User information
-   `Food`: Food items
-   `FoodRating`: User-food ratings

### Key Parameters

-   **k_factors**: 10 (number of latent factors for SVD)
-   **min_rating_threshold**: 3.0 (minimum predicted rating)
-   **top_n_recommendations**: 10

### Performance Considerations

-   **Matrix Sparsity**: ~79.89% (most cells are empty)
-   **Computational Complexity**: O(k × m × n) where:
    -   k = number of factors
    -   m = number of users
    -   n = number of items
-   **Memory Usage**: Scales with number of users × items

---

## Understanding the Results

### High Similarity (> 0.9)

-   Users have very similar rating patterns
-   Strong indicators for collaborative filtering
-   High confidence in recommendations

### Medium Similarity (0.5 - 0.9)

-   Some overlap in preferences
-   Moderate confidence in recommendations
-   May need more data points

### Low Similarity (< 0.5)

-   Different rating patterns
-   Low confidence for recommendations
-   Consider content-based filtering

### Zero Similarity (0.0)

-   No common rated items
-   Cannot calculate cosine similarity
-   Need cold-start handling

---

## Advantages of This Approach

1. **Transparency**: Shows every calculation step
2. **Educational**: Learn how SVD works
3. **Debuggable**: Easy to spot issues in data/algorithm
4. **Visual**: Rich tables and charts
5. **Comprehensive**: Covers entire pipeline

---

## Comparison with Production System

| Feature        | Production System    | Detailed Script           |
| -------------- | -------------------- | ------------------------- |
| Speed          | Fast (optimized)     | Slower (detailed)         |
| Output         | Final results only   | Step-by-step              |
| Visualization  | Minimal              | Rich tables               |
| Users Analyzed | Top K similar        | 15 similar + 5 dissimilar |
| Matrix Display | Hidden               | Visible (U, Σ, Vᵀ)        |
| Purpose        | Real recommendations | Learning & debugging      |

---

## Troubleshooting

### Issue: "User not found"

**Solution**: Check username spelling, ensure user exists in database

### Issue: "Not enough users to compare"

**Solution**: Need at least 20 users in database

### Issue: "SVD decomposition failed"

**Solution**:

-   Check matrix has enough non-zero values
-   Reduce k_factors parameter
-   Ensure data quality

### Issue: "No recommendations generated"

**Solution**:

-   Lower min_rating_threshold
-   Check if user has rated items
-   Verify SVD reconstruction

---

## Future Enhancements

-   [ ] Add confidence intervals for predictions
-   [ ] Show feature interpretations
-   [ ] Include precision@k and recall@k metrics
-   [ ] Add A/B test comparison with production
-   [ ] Export results to JSON/CSV
-   [ ] Add user-item interaction heatmap
-   [ ] Include temporal analysis

---

**Created**: October 24, 2025
**Author**: Recommendation System Team
**Version**: 1.0
