# 🎯 Quick Start - Detailed SVD Calculation

## Run Script

```bash
cd /home/labubu/Projects/adza/backend
python app/recommendation/manual_svd_detailed.py
```

## What You'll See

### 1. 20 Users Similarity (15 similar + 5 dissimilar)

```
Rank #1: Ella - 0.9952 similarity
Rank #2: Nisa - 0.9950 similarity
...
```

### 2. Detailed Calculations

```
Ella: 77.67/(8.91×8.76) = 0.9952
```

### 3. SVD Decomposition

```
Matrix: 21 × 27 (79.89% sparse)
σ1: 2.083 (32.87% variance)
σ2: 1.744 (23.04% variance)
...
```

### 4. Top 10 Recommendations

```
#1 NASI GORENG SEAFOOD - 4.55⭐
#2 BEEF BULGOGI - 4.51⭐
...
```

## Documentation

See `DETAILED_SVD_DOC.md` for complete guide.

## Compare with Production

-   **Production**: `manual_calculation_svd.py` (fast, optimized)
-   **Detailed**: `manual_svd_detailed.py` (educational, step-by-step)
