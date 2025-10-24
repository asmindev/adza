# Output Summary - Calculation Details

## 📊 CALCULATION SUMMARY

### 1. Data Matrix Overview

Script sekarang menampilkan statistik lengkap dari User-Item Matrix:

```
📐 Data Matrix Overview
╭────────────────────────────────┬──────────────────────┬──────────────────────────────────────────╮
│ Metric                         │                Value │ Description                              │
├────────────────────────────────┼──────────────────────┼──────────────────────────────────────────┤
│ Total Users                    │                   68 │ Jumlah user dalam sistem                 │
│ Total Foods                    │                 3494 │ Jumlah makanan dalam sistem              │
│ Total Ratings                  │                  397 │ Jumlah rating yang diberikan             │
│ Matrix Size                    │            68 × 3494 │ Ukuran User-Item Matrix                  │
│ Possible Ratings               │              237,592 │ Total kemungkinan rating                 │
│ Sparsity                       │               99.83% │ Persentase cell kosong dalam matrix      │
╰────────────────────────────────┴──────────────────────┴──────────────────────────────────────────╯
```

**Key Insights:**

-   **Sparsity 99.83%**: Sangat sparse! Hanya 0.17% dari matrix yang terisi
-   **Matrix Size**: 68 × 3494 = 237,592 kemungkinan rating
-   **Actual Ratings**: Hanya 397 ratings yang ada (Cold start problem!)

### 2. Algorithm Configuration

Parameter-parameter yang digunakan sistem rekomendasi:

```
🔧 Algorithm Configuration:
   Similarity Method        Cosine Similarity     Metode untuk mencari similar users
   Similarity Threshold     0.2                   Minimum similarity score
   Top K Similar Users      50                    Jumlah similar users yang diambil
   SVD Latent Factors       Dynamic (3-4)         Jumlah faktor laten dalam SVD
   Min Rating Threshold     3.0                   Minimum predicted rating
   Hybrid Alpha             0.7                   70% food rating, 30% restaurant rating
```

**Parameter Explanation:**

-   **Cosine Similarity**: Mengukur kemiripan pola rating antar users
-   **Threshold 0.2**: Hanya ambil users dengan similarity > 0.2
-   **Top K = 50**: Maximum 50 similar users untuk efficiency
-   **SVD Factors**: Jumlah latent factors ditentukan dinamis (3-4)
-   **Min Threshold 3.0**: Hanya rekomendasikan items dengan predicted rating ≥ 3.0
-   **Alpha 0.7**: 70% bobot dari food rating, 30% dari restaurant rating

### 3. Calculation Steps

Pipeline algoritma dijelaskan secara detail:

```
⚙️ Calculation Steps:
╭─────────────────────────────────────────────── 📋 Algorithm Pipeline ───────────────────────────────────────────────╮
│                                                                                                                      │
│  1. Load Rating Matrix                                                                                               │
│     • Load semua ratings dari database                                                                               │
│     • Buat User-Item matrix (67 users × 35 foods)                                                                    │
│                                                                                                                      │
│  2. Calculate User Similarity                                                                                        │
│     • Hitung cosine similarity antar users                                                                           │
│     • Similarity = (A·B) / (||A|| × ||B||)                                                                           │
│     • Filter users dengan similarity > 0.2                                                                           │
│                                                                                                                      │
│  3. Create Local Dataset                                                                                             │
│     • Pilih top 50 similar users                                                                                     │
│     • Buat local matrix untuk efficiency                                                                             │
│     • Include hanya items yang relevan                                                                               │
│                                                                                                                      │
│  4. Apply SVD Decomposition                                                                                          │
│     • Matrix = U × Σ × V^T                                                                                           │
│     • U: User-Feature matrix                                                                                         │
│     • Σ: Singular values (diagonal)                                                                                  │
│     • V^T: Feature-Item matrix                                                                                       │
│                                                                                                                      │
│  5. Predict Ratings                                                                                                  │
│     • Reconstruct matrix: R̂ = U × Σ × V^T                                                                            │
│     • Filter predictions > 3.0                                                                                       │
│     • Rank by predicted rating                                                                                       │
│                                                                                                                      │
│  6. Generate Recommendations                                                                                         │
│     • Exclude already rated items                                                                                    │
│     • Return top N recommendations                                                                                   │
│     • Enrich with food details                                                                                       │
│                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### 4. Key Formulas

Formula matematika yang digunakan:

```
📐 Key Formulas:
                                                     ╷
  Formula                                            │ Description
╶────────────────────────────────────────────────────┼──────────────────────────────────────────╴
  Cosine Similarity:                                 │ Ukur kemiripan 2 user berdasarkan rating
    sim(u,v) = Σ(rᵤ·rᵥ) / (√Σrᵤ² × √Σrᵥ²)            │ Dot product / (magnitude u × magnitude v)
                                                     │
  SVD Decomposition:                                 │ Faktorisasi matrix menjadi 3 komponen
    R = U × Σ × Vᵀ                                   │ R: Rating matrix, U: User features
                                                     │
  Predicted Rating:                                  │ Rekonstruksi rating dari SVD
    r̂ᵤᵢ = Σₖ(Uᵤₖ × Σₖ × Vᵢₖ)                         │ Sum of user-feature × singular value ×
                                                     │ item-feature
```

**Formula Breakdown:**

#### Cosine Similarity

```
sim(u,v) = Σ(rᵤ·rᵥ) / (√Σrᵤ² × √Σrᵥ²)
```

-   **Numerator**: Dot product of user u and user v's ratings
-   **Denominator**: Product of magnitudes (L2 norms)
-   **Range**: -1 (opposite) to 1 (identical), 0 (perpendicular)
-   **Purpose**: Find users with similar rating patterns

#### SVD Decomposition

```
R = U × Σ × Vᵀ
```

-   **R**: Original rating matrix (users × items)
-   **U**: User-feature matrix (users × factors)
-   **Σ**: Singular values (diagonal matrix, factors × factors)
-   **Vᵀ**: Feature-item matrix (factors × items)
-   **Purpose**: Reduce dimensionality, capture latent features

#### Predicted Rating

```
r̂ᵤᵢ = Σₖ(Uᵤₖ × Σₖ × Vᵢₖ)
```

-   **r̂ᵤᵢ**: Predicted rating for user u on item i
-   **k**: Latent factor index (1 to K factors)
-   **Uᵤₖ**: User u's affinity for factor k
-   **Σₖ**: Importance of factor k
-   **Vᵢₖ**: Item i's value on factor k
-   **Purpose**: Predict missing ratings in matrix

## Interpretasi untuk User "adza"

### Data Matrix Analysis

```
Matrix Size: 68 × 3494
User "adza" has: 5 ratings
Sparsity: 99.83%
```

**Artinya:**

-   User "adza" baru memberikan 5 ratings dari 3494 makanan yang tersedia
-   Sistem harus memprediksi 3489 ratings yang belum ada
-   High sparsity menunjukkan cold start problem yang signifikan

### Similar Users Found

Dari logs:

```
Found 4 similar users for adza (threshold: 0.2, method: cosine)
Selected 5 similar users for adza using cosine
```

**Artinya:**

-   Sistem menemukan 4 users dengan similarity > 0.2
-   Total 5 users (termasuk adza) digunakan untuk local dataset
-   Local matrix: 5 users × 9 items (28 ratings)

### SVD Training Results

```
Training SVD on matrix: 5 users x 9 items, sparsity: 0.378
SVD training completed: 4 factors, explained variance ratio: 0.999
```

**Artinya:**

-   Local dataset jauh lebih dense (37.8% filled vs 0.17% global)
-   4 latent factors berhasil menjelaskan 99.9% variance
-   Model sangat akurat untuk local dataset ini

### Prediction Results

```
Filtered predictions (min_rating=3.0): 4 items
Generated 4 recommendations in 0.551s
```

**Artinya:**

-   Dari 9 items di local dataset, 5 sudah dirating user
-   4 items tersisa yang belum dirating
-   Semua 4 items memiliki predicted rating ≥ 3.0
-   Processing time sangat cepat (0.55 detik)

## Cara Membaca Output

### 1. Check Matrix Sparsity

-   **< 95%**: Good density, reliable recommendations
-   **95-99%**: Moderate sparsity, acceptable
-   **> 99%**: High sparsity, cold start problem! ⚠️

### 2. Check Similar Users

-   **> 10 users**: Excellent, strong collaborative signal
-   **5-10 users**: Good, sufficient for recommendations
-   **< 5 users**: Limited, may have quality issues ⚠️

### 3. Check SVD Explained Variance

-   **> 0.95**: Excellent model fit 🎯
-   **0.80-0.95**: Good model fit ✅
-   **< 0.80**: Poor fit, may need more factors ⚠️

### 4. Check Prediction Count

-   **= top_n**: Perfect, found enough recommendations ✅
-   **< top_n**: Limited options, need more data ⚠️
-   **= 0**: No recommendations possible! ❌

## Benefits of This Display

✅ **Transparency**: User dapat melihat proses di balik rekomendasi
✅ **Debugging**: Developer dapat identify issues dengan mudah
✅ **Education**: Menjelaskan konsep ML dengan visual yang jelas
✅ **Validation**: Memastikan algorithm bekerja dengan benar
✅ **Trust**: User lebih percaya dengan sistem yang transparent

## Potential Improvements

1. **Add Similarity Matrix Heatmap**: Visual representation of user similarities
2. **Show SVD Factors Interpretation**: Apa arti dari each latent factor
3. **Display Confidence Scores**: Seberapa yakin sistem dengan predictions
4. **Add Comparison Table**: Compare manual vs production results
5. **Export to Report**: Generate PDF/HTML report untuk dokumentasi

---

**Note**: Summary ini ditampilkan sebelum proses rekomendasi dimulai, memberikan context lengkap tentang data dan algorithm yang akan digunakan.
