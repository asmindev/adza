# Manual Testing Script - Production Recommendation System

## Overview

Script `manual_calculation_svd.py` telah diperbarui untuk menggunakan sistem rekomendasi production yang sudah ada, namun dengan tampilan Rich Console yang indah untuk memudahkan pengujian manual.

## Fitur Utama

### 1. **Production Recommendation System**

-   ✅ Menggunakan `RecommendationService` dan `Recommendations` class yang sudah ada
-   ✅ Implementasi SVD Collaborative Filtering yang sudah teruji
-   ✅ Hybrid scoring dengan alpha=0.7 (70% food rating, 30% restaurant rating)
-   ✅ Local dataset dengan similar users (cosine similarity)
-   ✅ Automatic data quality validation

### 2. **Beautiful Rich Console Display**

-   📊 **Rating History Table** - Menampilkan 10 rating terakhir user
-   ⭐ **Recommendations Table** - Top 10 rekomendasi dengan predicted rating
-   🎯 **User Panel** - Informasi user yang sedang diuji
-   📈 **Statistics Panel** - Average predicted rating dan prediction range
-   🎨 **Rich Formatting** - Tabel dengan box style (ROUNDED & DOUBLE), warna, dan emoji

### 3. **Fokus pada User "adza"**

-   Script otomatis mencari user dengan username "adza"
-   Menampilkan rating history lengkap dari user tersebut
-   Menampilkan rekomendasi khusus untuk user "adza"

## Cara Menjalankan

```bash
cd /home/labubu/Projects/adza/backend
python app/recommendation/manual_calculation_svd.py
```

## Output yang Dihasilkan

### 1. Header

```
SISTEM REKOMENDASI MAKANAN - PRODUCTION SYSTEM TESTING
SVD Collaborative Filtering with Rich Console Display
```

### 2. User Search

```
🔍 Searching for user: adza...
✓ Found user: Adza (@adza)
```

### 3. Rating History

```
📊 User's Rating History:
╭────────────────────────────────┬──────────────────────┬───────────┬────────────────╮
│ Food Name                      │ Restaurant           │     Price │     Rating     │
├────────────────────────────────┼──────────────────────┼───────────┼────────────────┤
│ Martabak Kornet Rica Rica Telu │ N/A                  │ Rp 62,500 │  4.4 ⭐⭐⭐⭐  │
│ KEJU KETAN                     │ N/A                  │ Rp 82,000 │  3.9 ⭐⭐⭐⭐  │
│ ...                            │ ...                  │       ... │       ...      │
╰────────────────────────────────┴──────────────────────┴───────────┴────────────────╯
```

### 4. Recommendations

```
⭐ RECOMMENDED ITEMS:
╔════════╦═════════════════════════════════════╦════════════════════════╦══════════════╦══════════════╦════════════╗
║  Rank  ║ Food Name                           ║ Restaurant             ║        Price ║ Pred. Rating ║   Stars    ║
╠════════╬═════════════════════════════════════╬════════════════════════╬══════════════╬══════════════╬════════════╣
║   #1   ║ Mie Ayam Pangsit Bakso              ║ N/A                    ║    Rp 35,000 ║     4.55     ║ ⭐⭐⭐⭐⭐ ║
║   #2   ║ BEEF BULGOGI                        ║ N/A                    ║    Rp 37,850 ║     4.55     ║ ⭐⭐⭐⭐⭐ ║
║   #3   ║ NASI GORENG SEAFOOD                 ║ N/A                    ║    Rp 35,000 ║     4.37     ║  ⭐⭐⭐⭐  ║
║   #4   ║ Mie Goreng Bakso + Telur            ║ N/A                    ║    Rp 23,000 ║     4.20     ║  ⭐⭐⭐⭐  ║
╚════════╩═════════════════════════════════════╩════════════════════════╩══════════════╩══════════════╩════════════╝
```

### 5. Statistics

```
📈 RECOMMENDATION STATISTICS:
  • Average Predicted Rating: 4.42
  • Prediction Range: 4.20 - 4.55
  • Method: SVD Collaborative Filtering (Production)
```

## Hasil Testing untuk User "adza"

Berdasarkan output terbaru:

### Rating History (5 items):

1. **Martabak Kornet Rica Rica Telur** - Rating: 4.4 ⭐⭐⭐⭐
2. **KEJU KETAN** - Rating: 3.9 ⭐⭐⭐⭐
3. **Nasi + Udang + Sayur + Sambal** - Rating: 4.8 ⭐⭐⭐⭐⭐
4. **Nasi Biasa Ayam Bakar+tempe+so** - Rating: 4.8 ⭐⭐⭐⭐⭐
5. **Martabak Kornet Tripel chesee** - Rating: 4.8 ⭐⭐⭐⭐⭐

### Top 4 Recommendations:

1. **Mie Ayam Pangsit Bakso** - Predicted: 4.55 ⭐⭐⭐⭐⭐ (Rp 35,000)
2. **BEEF BULGOGI** - Predicted: 4.55 ⭐⭐⭐⭐⭐ (Rp 37,850)
3. **NASI GORENG SEAFOOD** - Predicted: 4.37 ⭐⭐⭐⭐ (Rp 35,000)
4. **Mie Goreng Bakso + Telur** - Predicted: 4.20 ⭐⭐⭐⭐ (Rp 23,000)

### Statistics:

-   **Average Predicted Rating**: 4.42
-   **Prediction Range**: 4.20 - 4.55
-   **Method**: SVD Collaborative Filtering (Production)

## Technical Details

### Dependencies

-   **Flask**: Web framework dengan app context
-   **SQLAlchemy**: Database ORM
-   **Rich**: Terminal UI library untuk beautiful output
-   **Production Services**:
    -   `RecommendationService`: Main recommendation service
    -   `Recommendations`: Core recommendation engine
    -   `LocalDataProcessor`: Data processing dengan hybrid scoring
    -   `LocalSVDModel`: SVD model implementation
    -   `similarity`: Cosine & Jaccard similarity calculations

### Database Models Used

-   `User`: User information
-   `Food`: Food details (name, price, restaurant_name)
-   `FoodRating`: User ratings

### Recommendation Algorithm

1. **Load Ratings**: 397 ratings dari 67 users untuk 35 foods (sparsity: 83.07%)
2. **Find Similar Users**: Cosine similarity dengan threshold 0.2
3. **Create Local Dataset**: 5 similar users × 9 foods matrix
4. **Train SVD Model**: 4 latent factors, variance: 99.9%
5. **Predict Ratings**: Min threshold 3.0
6. **Filter & Rank**: Top N recommendations dengan predicted ratings
7. **Enrich Details**: Add food details dari database

## Perubahan dari Versi Sebelumnya

### ❌ **Removed**

-   Manual SVD calculation dengan scipy.sparse.linalg.svds
-   Manual cosine similarity calculation
-   Manual rating matrix creation
-   Database connection dengan SQLAlchemy engine
-   Hybrid recommendation calculation
-   Multiple user display

### ✅ **Added**

-   Integration dengan production `RecommendationService`
-   Flask app context initialization
-   Production recommendation enrichment
-   Fokus pada single user ("adza")
-   Simplified error handling
-   Better logging dari production system

## Keunggulan Pendekatan Baru

1. **Consistency** ✅

    - Menggunakan exact same algorithm dengan production API
    - Hasil yang sama dengan yang dilihat user di aplikasi

2. **Maintainability** ✅

    - Tidak perlu maintain duplicate code
    - Update di production otomatis tercermin di testing script

3. **Reliability** ✅

    - Production code sudah teruji dengan baik
    - Include validation, error handling, dan logging

4. **Visualization** ✅

    - Beautiful Rich Console display tetap dipertahankan
    - Mudah dibaca dan dipahami untuk testing manual

5. **Performance** ✅
    - Optimized dengan caching (1 hour cache duration)
    - Local dataset approach untuk speed
    - Efficient similarity calculations

## Future Improvements

Potential enhancements:

1. Add command-line arguments untuk specify user
2. Compare recommendations dengan different similarity methods
3. Show explanation untuk each recommendation
4. Export results to JSON/CSV
5. Batch testing untuk multiple users
6. Visualization dengan matplotlib/plotly

## Troubleshooting

### Issue: User not found

**Solution**: Check username di database, atau modify `target_username` variable

### Issue: No recommendations generated

**Possible causes**:

-   User belum punya rating
-   Tidak ada similar users
-   SVD training gagal
-   Database connection error

**Solution**: Check logs untuk detail error message

### Issue: Import errors

**Solution**: Pastikan running dari backend directory dan Flask app properly configured

## Contact

Untuk pertanyaan atau issue, hubungi development team.

---

**Last Updated**: 2025-10-24
**Version**: 2.0 (Production Integration)
**Author**: Development Team
