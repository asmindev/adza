# 📚 Dokumentasi Pengujian Model SVD

Kumpulan dokumentasi dan tools untuk pengujian evaluasi model SVD recommendation system.

---

## 📂 File-File yang Tersedia

### 1. **test_model_evaluation.py** 🧪

Script utama untuk menjalankan full evaluation model SVD dengan train-test split.

**Fitur:**

-   Load data dari database
-   Create user-item matrix
-   Train-test split (80/20) per-user
-   Train SVD model dengan 12 latent factors
-   Evaluate dengan metrik: MAE, RMSE, NDCG@10, Coverage
-   Sample predictions & recommendations

**Cara menjalankan:**

```bash
source .venv/bin/activate
python simulate/test_model_evaluation.py
```

---

### 2. **debug_predictions.py** 🔍

Script untuk debugging detail prediksi model.

**Fitur:**

-   Analisis user/item factors
-   Breakdown calculation prediksi
-   Check bias values
-   Detailed prediction breakdown

**Cara menjalankan:**

```bash
python simulate/debug_predictions.py
```

---

### 3. **ringkasan_alur_pengujian.py** 📋

Ringkasan text-based alur pengujian model (8 steps).

**Isi:**

-   Overview pengujian
-   Step-by-step explanation
-   Metrik evaluasi
-   Technical improvements
-   Hasil akhir

**Cara menjalankan:**

```bash
python simulate/ringkasan_alur_pengujian.py
```

---

### 4. **diagram_alur_visual.py** 🎨

Diagram visual ASCII art untuk alur pengujian.

**Isi:**

-   Flowchart visual
-   Formula prediksi
-   Perbandingan bias dampening
-   Interpretasi metrik

**Cara menjalankan:**

```bash
python simulate/diagram_alur_visual.py
```

---

### 5. **ALUR_PENGUJIAN_MODEL.md** 📖

Dokumentasi lengkap dalam format Markdown.

**Isi:**

-   Diagram alur detail
-   Penjelasan setiap step
-   Formula matematika
-   Key concepts
-   Best practices

**Cara membaca:**

```bash
cat simulate/ALUR_PENGUJIAN_MODEL.md
# atau buka di text editor/VS Code
```

---

## 🔄 Alur Pengujian (Ringkas)

```
DATABASE → Load Data → Pivot Matrix → Train/Test Split
    ↓
Train SVD → Predict Test → Evaluate Metrics → Results
```

### 8 Steps Detail:

1. **Load Data** - Load 397 ratings dari database
2. **Create Matrix** - Transform ke user-item matrix (67×35)
3. **Train-Test Split** - Split 80/20 per-user
4. **Train SVD** - Fit model dengan 12 latent factors
5. **Evaluate** - Calculate MAE, RMSE, NDCG
6. **Interpret** - Analisis quality metrics
7. **Sample Predictions** - Verify dengan sample user
8. **Recommendations** - Generate top-10 recommendations

---

## 📊 Hasil Evaluasi

```
┌─────────────────────────────────────────────┐
│  MODEL PERFORMANCE SUMMARY                  │
├─────────────────────────────────────────────┤
│  MAE:     0.365  ⭐⭐⭐⭐⭐  (Excellent)        │
│  RMSE:    0.450  ⭐⭐⭐⭐⭐  (Excellent)        │
│  NDCG@10: 0.984  ⭐⭐⭐⭐⭐  (Excellent)        │
│                                             │
│  Dataset: 67 users × 35 items               │
│  Sparsity: 83.1%                            │
│  Split: 322 train / 75 test                 │
│  Model: SVD with 12 factors                 │
│                                             │
│  Status: ✅ PRODUCTION READY                │
└─────────────────────────────────────────────┘
```

---

## 🎯 Key Metrics

### MAE (Mean Absolute Error)

-   **Formula:** `mean(|predicted - actual|)`
-   **Result:** 0.365 bintang
-   **Artinya:** Model rata-rata meleset 0.37 bintang
-   **Threshold:** < 0.5 = Excellent ⭐⭐⭐⭐⭐

### RMSE (Root Mean Squared Error)

-   **Formula:** `sqrt(mean((predicted - actual)²))`
-   **Result:** 0.450 bintang
-   **Artinya:** Penalize error besar, nilai konsisten
-   **Threshold:** < 0.7 = Excellent ⭐⭐⭐⭐⭐

### NDCG@10 (Normalized DCG)

-   **Formula:** `DCG@10 / IDCG@10`
-   **Result:** 0.984 (98.4%)
-   **Artinya:** Ranking quality hampir sempurna!
-   **Threshold:** > 0.8 = Excellent ⭐⭐⭐⭐⭐

---

## 🔧 Technical Improvements

### 1. Bias Dampening (Shrinkage)

```python
# Problem: bias terlalu besar → prediksi > 5.0
user_bias *= 0.7  # Kurangi 30%
item_bias *= 0.7  # Kurangi 30%
```

**Hasil:**

-   ❌ Sebelum: Semua prediksi 5.000 (overfitting)
-   ✅ Sesudah: Variasi 4.659-4.965 (realistic)

### 2. CSR Sparse Matrix

```python
if sparsity > 0.8:
    sparse_matrix = csr_matrix(training_matrix)
    user_factors = svd_model.fit_transform(sparse_matrix)
```

**Benefit:**

-   Hemat memori (hanya simpan non-zero)
-   Lebih cepat untuk data sparse

### 3. Per-User Train-Test Split

-   Setiap user berkontribusi ke test set
-   Evaluasi lebih representative
-   Model generalize ke semua user

---

## 🚀 Quick Start

```bash
# 1. Aktifkan virtual environment
cd /home/labubu/Projects/adza/backend
source .venv/bin/activate

# 2. Jalankan full evaluation
python simulate/test_model_evaluation.py

# 3. Lihat ringkasan
python simulate/ringkasan_alur_pengujian.py

# 4. Lihat diagram visual
python simulate/diagram_alur_visual.py

# 5. Debug detail (jika perlu)
python simulate/debug_predictions.py
```

---

## 📝 Catatan Penting

### Formula Prediksi Akhir:

```python
prediction = global_mean
           + (user_bias × 0.7)      # dampening
           + (item_bias × 0.7)      # dampening
           + dot(user_vector, item_vector)

# Clipped to [1.0, 5.0]
```

### Kapan Model Perlu Re-evaluasi?

-   ✅ Ada data baru (ratings bertambah signifikan)
-   ✅ Performance drop di production
-   ✅ Perubahan pada algoritma
-   ✅ Tuning hyperparameters

---

## 📞 Support

Jika ada pertanyaan atau masalah:

1. Cek dokumentasi lengkap: `ALUR_PENGUJIAN_MODEL.md`
2. Run debug script: `debug_predictions.py`
3. Review logs di `backend/logs/recommendation.log`

---

## ✅ Checklist Before Production

-   [x] Model trained successfully
-   [x] Evaluation metrics excellent (MAE < 0.5, NDCG > 0.8)
-   [x] No overfitting (bias dampening works)
-   [x] Efficient for sparse data (CSR optimization)
-   [x] Sample predictions verified
-   [x] Recommendations diverse (not all 5.0)

**Status: 🎉 READY FOR PRODUCTION!**
