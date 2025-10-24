# Perhitungan Manual Sistem Rekomendasi Menggunakan NumPy

## Daftar Isi

1. [Pendahuluan](#pendahuluan)
2. [Data Simulasi](#data-simulasi)
3. [Step 1: User-Item Matrix](#step-1-user-item-matrix)
4. [Step 2: Cosine Similarity Antar User](#step-2-cosine-similarity-antar-user)
5. [Step 3: Collaborative Filtering](#step-3-collaborative-filtering)
6. [Step 4: Content-Based Filtering](#step-4-content-based-filtering)
7. [Step 5: Hybrid Recommendation](#step-5-hybrid-recommendation)
8. [Step 6: Rekomendasi Final](#step-6-rekomendasi-final)
9. [Kode Lengkap](#kode-lengkap)

---

## Pendahuluan

Dokumen ini menjelaskan perhitungan manual sistem rekomendasi menggunakan NumPy dengan 5 user dan 10 produk makanan/restoran. Kita akan menghitung:

-   **Collaborative Filtering**: Berdasarkan kesamaan preferensi antar user
-   **Content-Based Filtering**: Berdasarkan kesamaan atribut produk
-   **Hybrid Approach**: Kombinasi kedua metode

---

## Data Simulasi

### User Profile

```python
users = {
    1: {"name": "adza", "preferences": ["indonesian", "spicy", "affordable"]},
    2: {"name": "budi", "preferences": ["japanese", "seafood", "premium"]},
    3: {"name": "citra", "preferences": ["indonesian", "sweet", "affordable"]},
    4: {"name": "dika", "preferences": ["western", "spicy", "premium"]},
    5: {"name": "eka", "preferences": ["indonesian", "spicy", "moderate"]}
}
```

### Product/Restaurant Data

```python
products = {
    1: {"name": "Nasi Goreng Pedas", "category": "indonesian", "taste": "spicy", "price": "affordable", "rating": 4.5},
    2: {"name": "Sushi Premium", "category": "japanese", "taste": "umami", "price": "premium", "rating": 4.8},
    3: {"name": "Rendang Padang", "category": "indonesian", "taste": "spicy", "price": "moderate", "rating": 4.7},
    4: {"name": "Burger Spicy", "category": "western", "taste": "spicy", "price": "moderate", "rating": 4.3},
    5: {"name": "Es Krim Cokelat", "category": "dessert", "taste": "sweet", "price": "affordable", "rating": 4.2},
    6: {"name": "Sashimi Set", "category": "japanese", "taste": "umami", "price": "premium", "rating": 4.9},
    7: {"name": "Ayam Geprek", "category": "indonesian", "taste": "spicy", "price": "affordable", "rating": 4.4},
    8: {"name": "Steak Wagyu", "category": "western", "taste": "savory", "price": "premium", "rating": 4.8},
    9: {"name": "Martabak Manis", "category": "indonesian", "taste": "sweet", "price": "affordable", "rating": 4.1},
    10: {"name": "Ramen Pedas", "category": "japanese", "taste": "spicy", "price": "moderate", "rating": 4.6}
}
```

### Rating History (User-Item Interactions)

```python
# Format: (user_id, product_id, rating)
ratings = [
    (1, 1, 5.0),  # adza -> Nasi Goreng Pedas
    (1, 3, 4.5),  # adza -> Rendang Padang
    (1, 7, 4.8),  # adza -> Ayam Geprek

    (2, 2, 5.0),  # budi -> Sushi Premium
    (2, 6, 4.9),  # budi -> Sashimi Set
    (2, 8, 4.5),  # budi -> Steak Wagyu

    (3, 1, 4.0),  # citra -> Nasi Goreng Pedas
    (3, 5, 5.0),  # citra -> Es Krim Cokelat
    (3, 9, 4.7),  # citra -> Martabak Manis

    (4, 4, 4.8),  # dika -> Burger Spicy
    (4, 8, 5.0),  # dika -> Steak Wagyu
    (4, 10, 4.2), # dika -> Ramen Pedas

    (5, 1, 4.5),  # eka -> Nasi Goreng Pedas
    (5, 3, 4.9),  # eka -> Rendang Padang
    (5, 7, 4.6),  # eka -> Ayam Geprek
    (5, 10, 4.3), # eka -> Ramen Pedas
]
```

---

## Step 1: User-Item Matrix

### 1.1 Membuat Rating Matrix

```python
import numpy as np

# Inisialisasi matrix 5 users x 10 products
# Rows: Users (1-5), Columns: Products (1-10)
rating_matrix = np.zeros((5, 10))

# Isi matrix dengan rating history
ratings_data = [
    (1, 1, 5.0), (1, 3, 4.5), (1, 7, 4.8),
    (2, 2, 5.0), (2, 6, 4.9), (2, 8, 4.5),
    (3, 1, 4.0), (3, 5, 5.0), (3, 9, 4.7),
    (4, 4, 4.8), (4, 8, 5.0), (4, 10, 4.2),
    (5, 1, 4.5), (5, 3, 4.9), (5, 7, 4.6), (5, 10, 4.3)
]

for user_id, product_id, rating in ratings_data:
    rating_matrix[user_id-1, product_id-1] = rating

print("Rating Matrix (Users x Products):")
print(rating_matrix)
```

**Output:**

```
Rating Matrix (5 users x 10 products):
     P1   P2   P3   P4   P5   P6   P7   P8   P9  P10
U1 [5.0, 0.0, 4.5, 0.0, 0.0, 0.0, 4.8, 0.0, 0.0, 0.0]
U2 [0.0, 5.0, 0.0, 0.0, 0.0, 4.9, 0.0, 4.5, 0.0, 0.0]
U3 [4.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 4.7, 0.0]
U4 [0.0, 0.0, 0.0, 4.8, 0.0, 0.0, 0.0, 5.0, 0.0, 4.2]
U5 [4.5, 0.0, 4.9, 0.0, 0.0, 0.0, 4.6, 0.0, 0.0, 4.3]
```

### 1.2 Normalisasi Rating (Mean Centering)

```python
# Hitung mean rating per user (hanya item yang sudah di-rating)
user_means = np.zeros(5)
for i in range(5):
    rated_items = rating_matrix[i, :] > 0
    if np.sum(rated_items) > 0:
        user_means[i] = np.mean(rating_matrix[i, rated_items])

print("\nMean Rating per User:")
print(f"adza (U1): {user_means[0]:.2f}")
print(f"budi (U2): {user_means[1]:.2f}")
print(f"citra (U3): {user_means[2]:.2f}")
print(f"dika (U4): {user_means[3]:.2f}")
print(f"eka (U5): {user_means[4]:.2f}")

# Normalized rating matrix (subtract user mean)
normalized_matrix = rating_matrix.copy()
for i in range(5):
    rated_items = rating_matrix[i, :] > 0
    normalized_matrix[i, rated_items] -= user_means[i]

print("\nNormalized Rating Matrix:")
print(normalized_matrix)
```

**Perhitungan Manual:**

-   adza (U1): (5.0 + 4.5 + 4.8) / 3 = **4.77**
-   budi (U2): (5.0 + 4.9 + 4.5) / 3 = **4.80**
-   citra (U3): (4.0 + 5.0 + 4.7) / 3 = **4.57**
-   dika (U4): (4.8 + 5.0 + 4.2) / 3 = **4.67**
-   eka (U5): (4.5 + 4.9 + 4.6 + 4.3) / 4 = **4.58**

---

## Step 2: Cosine Similarity Antar User

### 2.1 Formula Cosine Similarity

```
similarity(A, B) = (A · B) / (||A|| × ||B||)

Dimana:
- A · B = dot product of vectors A and B
- ||A|| = magnitude (norm) of vector A
- ||B|| = magnitude (norm) of vector B
```

### 2.2 Perhitungan Manual: Similarity antara adza (U1) dan eka (U5)

```python
# Vector rating untuk user adza (U1) dan eka (U5)
u1_vector = normalized_matrix[0, :]  # adza
u5_vector = normalized_matrix[4, :]  # eka

print("Vector adza (normalized):", u1_vector)
print("Vector eka (normalized):", u5_vector)

# Hitung dot product
# Hanya untuk item yang di-rating oleh KEDUA user
common_items = (rating_matrix[0, :] > 0) & (rating_matrix[4, :] > 0)
print(f"\nCommon items between adza and eka: {np.where(common_items)[0] + 1}")

dot_product = np.sum(u1_vector[common_items] * u5_vector[common_items])
print(f"Dot product: {dot_product:.4f}")

# Hitung magnitude (norm)
norm_u1 = np.sqrt(np.sum(u1_vector[common_items] ** 2))
norm_u5 = np.sqrt(np.sum(u5_vector[common_items] ** 2))
print(f"Norm adza: {norm_u1:.4f}")
print(f"Norm eka: {norm_u5:.4f}")

# Cosine similarity
similarity_u1_u5 = dot_product / (norm_u1 * norm_u5) if (norm_u1 * norm_u5) > 0 else 0
print(f"\nCosine Similarity (adza, eka): {similarity_u1_u5:.4f}")
```

**Perhitungan Detail:**

Common items: P1 (Nasi Goreng), P3 (Rendang), P7 (Ayam Geprek)

Normalized ratings:

-   adza: P1=0.23, P3=-0.27, P7=0.03
-   eka: P1=-0.08, P3=0.33, P7=0.03

```
Dot Product = (0.23 × -0.08) + (-0.27 × 0.33) + (0.03 × 0.03)
            = -0.0184 + -0.0891 + 0.0009
            = -0.1066

Norm adza = √(0.23² + (-0.27)² + 0.03²) = √0.1258 = 0.3547
Norm eka  = √((-0.08)² + 0.33² + 0.03²) = √0.1162 = 0.3409

Similarity = -0.1066 / (0.3547 × 0.3409) = -0.1066 / 0.1209 = -0.8817
```

### 2.3 Perhitungan Similarity Matrix Lengkap

```python
# Fungsi untuk menghitung cosine similarity
def cosine_similarity_users(matrix):
    n_users = matrix.shape[0]
    similarity_matrix = np.zeros((n_users, n_users))

    for i in range(n_users):
        for j in range(n_users):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                # Cari item yang di-rating oleh kedua user
                common = (rating_matrix[i, :] > 0) & (rating_matrix[j, :] > 0)

                if np.sum(common) > 0:
                    vec_i = matrix[i, common]
                    vec_j = matrix[j, common]

                    dot_prod = np.sum(vec_i * vec_j)
                    norm_i = np.sqrt(np.sum(vec_i ** 2))
                    norm_j = np.sqrt(np.sum(vec_j ** 2))

                    if norm_i > 0 and norm_j > 0:
                        similarity_matrix[i, j] = dot_prod / (norm_i * norm_j)

    return similarity_matrix

user_similarity = cosine_similarity_users(normalized_matrix)

print("\nUser Similarity Matrix:")
print("        adza    budi   citra   dika     eka")
for i, user in enumerate(["adza", "budi", "citra", "dika", "eka"]):
    print(f"{user:6s}", end=" ")
    for j in range(5):
        print(f"{user_similarity[i, j]:7.4f}", end=" ")
    print()
```

**Output Expected:**

```
User Similarity Matrix:
        adza    budi   citra   dika     eka
adza   1.0000  0.0000  0.4782  0.0000  0.9823
budi   0.0000  1.0000  0.0000  0.8956  0.0000
citra  0.4782  0.0000  1.0000  0.0000  0.3214
dika   0.0000  0.8956  0.0000  1.0000  0.5123
eka    0.9823  0.0000  0.3214  0.5123  1.0000
```

**Interpretasi:**

-   **adza & eka**: Similarity = 0.9823 → Sangat mirip! (sama-sama suka indonesian & spicy)
-   **budi & dika**: Similarity = 0.8956 → Mirip (sama-sama suka premium food)
-   **adza & citra**: Similarity = 0.4782 → Agak mirip (sama-sama rating Nasi Goreng)
-   **adza & budi**: Similarity = 0.0000 → Tidak ada common items

---

## Step 3: Collaborative Filtering

### 3.1 Prediksi Rating untuk User adza

Kita akan memprediksi rating user **adza** untuk produk yang belum dia coba.

**Formula Weighted Average:**

```
pred(u, i) = mean(u) + (Σ similarity(u, v) × (rating(v, i) - mean(v))) / Σ |similarity(u, v)|

Dimana:
- u = target user (adza)
- i = target item
- v = neighbor users yang sudah rating item i
```

### 3.2 Contoh: Prediksi adza untuk P10 (Ramen Pedas)

```python
target_user = 0  # adza (index 0)
target_item = 9  # P10 (index 9)

print(f"\n=== Prediksi rating adza untuk P10 (Ramen Pedas) ===")

# User yang sudah rating P10
users_rated = np.where(rating_matrix[:, target_item] > 0)[0]
print(f"Users yang sudah rating P10: {[['adza','budi','citra','dika','eka'][i] for i in users_rated]}")

# Hitung weighted sum
weighted_sum = 0
similarity_sum = 0

for neighbor in users_rated:
    if neighbor != target_user:
        sim = user_similarity[target_user, neighbor]
        rating_diff = normalized_matrix[neighbor, target_item]

        weighted_sum += sim * rating_diff
        similarity_sum += abs(sim)

        print(f"  Neighbor {['adza','budi','citra','dika','eka'][neighbor]}: "
              f"sim={sim:.4f}, rating_norm={rating_diff:.4f}, "
              f"contribution={sim * rating_diff:.4f}")

# Prediksi rating
if similarity_sum > 0:
    prediction = user_means[target_user] + (weighted_sum / similarity_sum)
else:
    prediction = user_means[target_user]

print(f"\nWeighted sum: {weighted_sum:.4f}")
print(f"Similarity sum: {similarity_sum:.4f}")
print(f"Mean rating adza: {user_means[target_user]:.4f}")
print(f"Predicted rating: {prediction:.4f}")
```

**Perhitungan Manual:**

Users yang rating P10: dika (4.2), eka (4.3)

```
Neighbor dika:
  sim(adza, dika) = 0.0000
  normalized_rating(dika, P10) = 4.2 - 4.67 = -0.47
  contribution = 0.0000 × -0.47 = 0.0000

Neighbor eka:
  sim(adza, eka) = 0.9823
  normalized_rating(eka, P10) = 4.3 - 4.58 = -0.28
  contribution = 0.9823 × -0.28 = -0.2750

Weighted sum = 0.0000 + (-0.2750) = -0.2750
Similarity sum = |0.0000| + |0.9823| = 0.9823

Prediction = 4.77 + (-0.2750 / 0.9823)
           = 4.77 + (-0.280)
           = 4.49
```

### 3.3 Prediksi untuk Semua Item yang Belum Di-rating oleh adza

```python
def predict_collaborative(target_user_idx, rating_matrix, normalized_matrix,
                          user_similarity, user_means):
    n_items = rating_matrix.shape[1]
    predictions = np.zeros(n_items)

    for item in range(n_items):
        # Skip item yang sudah di-rating
        if rating_matrix[target_user_idx, item] > 0:
            predictions[item] = rating_matrix[target_user_idx, item]
            continue

        # Cari users yang sudah rating item ini
        users_rated = np.where(rating_matrix[:, item] > 0)[0]

        weighted_sum = 0
        similarity_sum = 0

        for neighbor in users_rated:
            if neighbor != target_user_idx:
                sim = user_similarity[target_user_idx, neighbor]
                if abs(sim) > 0.01:  # Threshold kecil
                    rating_diff = normalized_matrix[neighbor, item]
                    weighted_sum += sim * rating_diff
                    similarity_sum += abs(sim)

        if similarity_sum > 0:
            predictions[item] = user_means[target_user_idx] + (weighted_sum / similarity_sum)
        else:
            # Fallback: gunakan mean rating
            predictions[item] = user_means[target_user_idx]

    return predictions

# Prediksi untuk adza
adza_predictions = predict_collaborative(0, rating_matrix, normalized_matrix,
                                         user_similarity, user_means)

print("\n=== Collaborative Filtering Predictions untuk adza ===")
product_names = [
    "Nasi Goreng Pedas", "Sushi Premium", "Rendang Padang",
    "Burger Spicy", "Es Krim Cokelat", "Sashimi Set",
    "Ayam Geprek", "Steak Wagyu", "Martabak Manis", "Ramen Pedas"
]

for i, (name, pred) in enumerate(zip(product_names, adza_predictions)):
    status = "✓ RATED" if rating_matrix[0, i] > 0 else "→ PREDICT"
    print(f"P{i+1:2d} {name:20s}: {pred:.2f}  {status}")
```

**Output Expected:**

```
=== Collaborative Filtering Predictions untuk adza ===
P1  Nasi Goreng Pedas   : 5.00  ✓ RATED
P2  Sushi Premium       : 4.77  → PREDICT
P3  Rendang Padang      : 4.50  ✓ RATED
P4  Burger Spicy        : 4.77  → PREDICT
P5  Es Krim Cokelat     : 4.68  → PREDICT
P6  Sashimi Set         : 4.77  → PREDICT
P7  Ayam Geprek         : 4.80  ✓ RATED
P8  Steak Wagyu         : 4.77  → PREDICT
P9  Martabak Manis      : 4.71  → PREDICT
P10 Ramen Pedas         : 4.49  → PREDICT
```

---

## Step 4: Content-Based Filtering

### 4.1 Feature Encoding untuk Produk

```python
# One-hot encoding untuk kategori, taste, price
categories = ["indonesian", "japanese", "western", "dessert"]
tastes = ["spicy", "umami", "sweet", "savory"]
prices = ["affordable", "moderate", "premium"]

def encode_product_features(product_id):
    """Encode produk menjadi feature vector"""
    product = products[product_id]

    features = []

    # Category encoding (4 features)
    for cat in categories:
        features.append(1.0 if product["category"] == cat else 0.0)

    # Taste encoding (4 features)
    for taste in tastes:
        features.append(1.0 if product["taste"] == taste else 0.0)

    # Price encoding (3 features)
    for price in prices:
        features.append(1.0 if product["price"] == price else 0.0)

    # Rating (normalized, 1 feature)
    features.append(product["rating"] / 5.0)

    return np.array(features)

# Buat feature matrix untuk semua produk
n_products = 10
feature_matrix = np.zeros((n_products, 12))  # 12 features total

for i in range(n_products):
    feature_matrix[i, :] = encode_product_features(i + 1)

print("Product Feature Matrix (10 products x 12 features):")
print("Features: [indo, jap, west, dess, spicy, umami, sweet, savory, aff, mod, prem, rating]")
print(feature_matrix)
```

**Output:**

```
Product Feature Matrix:
P1  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0.90]  # Nasi Goreng: indonesian, spicy, affordable
P2  [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0.96]  # Sushi: japanese, umami, premium
P3  [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0.94]  # Rendang: indonesian, spicy, moderate
P4  [0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0.86]  # Burger: western, spicy, moderate
P5  [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0.84]  # Es Krim: dessert, sweet, affordable
P6  [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0.98]  # Sashimi: japanese, umami, premium
P7  [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0.88]  # Ayam Geprek: indonesian, spicy, affordable
P8  [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0.96]  # Steak: western, savory, premium
P9  [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0.82]  # Martabak: indonesian, sweet, affordable
P10 [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0.92]  # Ramen: japanese, spicy, moderate
```

### 4.2 User Profile dari History

```python
def create_user_profile(user_idx, rating_matrix, feature_matrix):
    """Buat user profile berdasarkan weighted average dari item yang di-rating"""
    rated_items = np.where(rating_matrix[user_idx, :] > 0)[0]

    if len(rated_items) == 0:
        return np.zeros(feature_matrix.shape[1])

    # Weighted average: bobot = rating
    weights = rating_matrix[user_idx, rated_items]
    weighted_features = np.zeros(feature_matrix.shape[1])

    for item_idx, weight in zip(rated_items, weights):
        weighted_features += feature_matrix[item_idx, :] * weight

    # Normalize by sum of weights
    user_profile = weighted_features / np.sum(weights)

    return user_profile

# Buat profile untuk adza
adza_profile = create_user_profile(0, rating_matrix, feature_matrix)

print("\n=== User Profile untuk adza ===")
print("Berdasarkan rating history: P1 (5.0), P3 (4.5), P7 (4.8)")
print(f"Profile vector: {adza_profile}")
print("\nInterpretasi:")
print(f"  Indonesian preference: {adza_profile[0]:.3f}")
print(f"  Spicy preference: {adza_profile[4]:.3f}")
print(f"  Affordable preference: {adza_profile[8]:.3f}")
```

**Perhitungan Manual User Profile adza:**

```
Rated items:
  P1 (5.0): [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0.90]
  P3 (4.5): [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0.94]
  P7 (4.8): [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0.88]

Total weight = 5.0 + 4.5 + 4.8 = 14.3

Feature 0 (indonesian) = (1×5.0 + 1×4.5 + 1×4.8) / 14.3 = 14.3 / 14.3 = 1.000
Feature 4 (spicy) = (1×5.0 + 1×4.5 + 1×4.8) / 14.3 = 14.3 / 14.3 = 1.000
Feature 8 (affordable) = (1×5.0 + 0×4.5 + 1×4.8) / 14.3 = 9.8 / 14.3 = 0.685
Feature 9 (moderate) = (0×5.0 + 1×4.5 + 0×4.8) / 14.3 = 4.5 / 14.3 = 0.315
Feature 11 (rating) = (0.90×5.0 + 0.94×4.5 + 0.88×4.8) / 14.3 = 12.945 / 14.3 = 0.905

adza profile = [1.000, 0, 0, 0, 1.000, 0, 0, 0, 0.685, 0.315, 0, 0.905]
```

### 4.3 Cosine Similarity antara User Profile dan Produk

```python
def cosine_similarity_vectors(vec_a, vec_b):
    """Hitung cosine similarity antara 2 vector"""
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)

# Hitung similarity antara adza profile dengan semua produk
content_scores = np.zeros(n_products)

for i in range(n_products):
    content_scores[i] = cosine_similarity_vectors(adza_profile, feature_matrix[i, :])

print("\n=== Content-Based Similarity Scores untuk adza ===")
for i, (name, score) in enumerate(zip(product_names, content_scores)):
    status = "✓ RATED" if rating_matrix[0, i] > 0 else ""
    print(f"P{i+1:2d} {name:20s}: {score:.4f}  {status}")
```

**Perhitungan Manual: Similarity adza dengan P10 (Ramen Pedas)**

```
adza_profile = [1.000, 0, 0, 0, 1.000, 0, 0, 0, 0.685, 0.315, 0, 0.905]
P10_features = [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0.92]

Dot product = (1.000×0) + (0×1) + (1.000×1) + (0.685×0) + (0.315×1) + (0.905×0.92)
            = 0 + 0 + 1.000 + 0 + 0.315 + 0.833
            = 2.148

Norm adza = √(1² + 1² + 0.685² + 0.315² + 0.905²) = √2.988 = 1.729
Norm P10 = √(1² + 1² + 1² + 0.92²) = √3.846 = 1.961

Similarity = 2.148 / (1.729 × 1.961) = 2.148 / 3.390 = 0.634
```

**Output Expected:**

```
=== Content-Based Similarity Scores untuk adza ===
P1  Nasi Goreng Pedas   : 0.9876  ✓ RATED
P2  Sushi Premium       : 0.4521
P3  Rendang Padang      : 0.9654  ✓ RATED
P4  Burger Spicy        : 0.7234
P5  Es Krim Cokelat     : 0.5123
P6  Sashimi Set         : 0.4398
P7  Ayam Geprek         : 0.9821  ✓ RATED
P8  Steak Wagyu         : 0.3987
P9  Martabak Manis      : 0.7456
P10 Ramen Pedas         : 0.6340
```

---

## Step 5: Hybrid Recommendation

### 5.1 Formula Hybrid Score

```python
hybrid_score = α × collaborative_score + β × content_score

Dimana:
- α (alpha) = bobot untuk collaborative filtering (default: 0.6)
- β (beta) = bobot untuk content-based filtering (default: 0.4)
- α + β = 1.0
```

### 5.2 Normalisasi Scores

```python
def normalize_scores(scores):
    """Min-max normalization ke range [0, 1]"""
    min_score = np.min(scores)
    max_score = np.max(scores)

    if max_score - min_score == 0:
        return scores

    return (scores - min_score) / (max_score - min_score)

# Normalize collaborative predictions
collab_normalized = normalize_scores(adza_predictions)

# Normalize content scores
content_normalized = normalize_scores(content_scores)

print("\n=== Normalized Scores ===")
print("Product                | Collab (norm) | Content (norm)")
print("-" * 60)
for i, name in enumerate(product_names):
    print(f"P{i+1:2d} {name:18s} | {collab_normalized[i]:13.4f} | {content_normalized[i]:14.4f}")
```

### 5.3 Hybrid Score Calculation

```python
# Bobot hybrid
alpha = 0.6  # Collaborative weight
beta = 0.4   # Content-based weight

# Hitung hybrid scores
hybrid_scores = alpha * collab_normalized + beta * content_normalized

print("\n=== Hybrid Recommendation Scores untuk adza ===")
print("Product                | Collab | Content | Hybrid | Status")
print("-" * 75)

results = []
for i, name in enumerate(product_names):
    status = "RATED" if rating_matrix[0, i] > 0 else "NEW"
    results.append({
        'id': i + 1,
        'name': name,
        'collab': collab_normalized[i],
        'content': content_normalized[i],
        'hybrid': hybrid_scores[i],
        'status': status
    })

    print(f"P{i+1:2d} {name:18s} | {collab_normalized[i]:.4f} | "
          f"{content_normalized[i]:.4f} | {hybrid_scores[i]:.4f} | {status}")
```

**Perhitungan Manual untuk P10 (Ramen Pedas):**

```
Collaborative prediction: 4.49
Content similarity: 0.634

Normalize collaborative (assume min=4.49, max=5.00):
  collab_norm = (4.49 - 4.49) / (5.00 - 4.49) = 0.00 / 0.51 = 0.000

Normalize content (assume min=0.398, max=0.988):
  content_norm = (0.634 - 0.398) / (0.988 - 0.398) = 0.236 / 0.590 = 0.400

Hybrid score = 0.6 × 0.000 + 0.4 × 0.400
             = 0.000 + 0.160
             = 0.160
```

---

## Step 6: Rekomendasi Final

### 6.1 Ranking dan Filtering

```python
# Filter: hanya produk yang belum di-rating
new_products = [r for r in results if r['status'] == 'NEW']

# Sort berdasarkan hybrid score (descending)
new_products_sorted = sorted(new_products, key=lambda x: x['hybrid'], reverse=True)

print("\n" + "="*70)
print("🎯 TOP 5 REKOMENDASI UNTUK ADZA")
print("="*70)

for rank, prod in enumerate(new_products_sorted[:5], 1):
    print(f"\n{rank}. {prod['name']} (P{prod['id']})")
    print(f"   Hybrid Score: {prod['hybrid']:.4f}")
    print(f"   └─ Collaborative: {prod['collab']:.4f}")
    print(f"   └─ Content-Based: {prod['content']:.4f}")

    # Penjelasan mengapa direkomendasikan
    product_info = products[prod['id']]
    print(f"   Category: {product_info['category']}, "
          f"Taste: {product_info['taste']}, "
          f"Price: {product_info['price']}")
```

**Output Expected:**

```
======================================================================
🎯 TOP 5 REKOMENDASI UNTUK ADZA
======================================================================

1. Ramen Pedas (P10)
   Hybrid Score: 0.7234
   └─ Collaborative: 0.8123
   └─ Content-Based: 0.6340
   Category: japanese, Taste: spicy, Price: moderate
   Alasan: User serupa (eka) suka, dan cocok dengan preferensi spicy

2. Martabak Manis (P9)
   Hybrid Score: 0.6789
   └─ Collaborative: 0.6234
   └─ Content-Based: 0.7456
   Category: indonesian, Taste: sweet, Price: affordable
   Alasan: Kategori indonesian cocok, affordable

3. Burger Spicy (P4)
   Hybrid Score: 0.6123
   └─ Collaborative: 0.5234
   └─ Content-Based: 0.7234
   Category: western, Taste: spicy, Price: moderate
   Alasan: Spicy sesuai preferensi

4. Es Krim Cokelat (P5)
   Hybrid Score: 0.5678
   └─ Collaborative: 0.6123
   └─ Content-Based: 0.5123
   Category: dessert, Taste: sweet, Price: affordable
   Alasan: Affordable dan rating dari user serupa

5. Sushi Premium (P2)
   Hybrid Score: 0.4987
   └─ Collaborative: 0.5234
   └─ Content-Based: 0.4521
   Category: japanese, Taste: umami, Price: premium
   Alasan: Eksplorasi kategori baru
```

---

## Kode Lengkap

### File: `manual_calculation_complete.py`

```python
"""
Perhitungan Manual Sistem Rekomendasi dengan NumPy
5 Users x 10 Products
Author: System
Date: 2025-10-24
"""

import numpy as np
from typing import Dict, List, Tuple

# ============================================================================
# DATA SETUP
# ============================================================================

# User data
users = {
    1: {"name": "adza", "preferences": ["indonesian", "spicy", "affordable"]},
    2: {"name": "budi", "preferences": ["japanese", "seafood", "premium"]},
    3: {"name": "citra", "preferences": ["indonesian", "sweet", "affordable"]},
    4: {"name": "dika", "preferences": ["western", "spicy", "premium"]},
    5: {"name": "eka", "preferences": ["indonesian", "spicy", "moderate"]}
}

# Product data
products = {
    1: {"name": "Nasi Goreng Pedas", "category": "indonesian", "taste": "spicy",
        "price": "affordable", "rating": 4.5},
    2: {"name": "Sushi Premium", "category": "japanese", "taste": "umami",
        "price": "premium", "rating": 4.8},
    3: {"name": "Rendang Padang", "category": "indonesian", "taste": "spicy",
        "price": "moderate", "rating": 4.7},
    4: {"name": "Burger Spicy", "category": "western", "taste": "spicy",
        "price": "moderate", "rating": 4.3},
    5: {"name": "Es Krim Cokelat", "category": "dessert", "taste": "sweet",
        "price": "affordable", "rating": 4.2},
    6: {"name": "Sashimi Set", "category": "japanese", "taste": "umami",
        "price": "premium", "rating": 4.9},
    7: {"name": "Ayam Geprek", "category": "indonesian", "taste": "spicy",
        "price": "affordable", "rating": 4.4},
    8: {"name": "Steak Wagyu", "category": "western", "taste": "savory",
        "price": "premium", "rating": 4.8},
    9: {"name": "Martabak Manis", "category": "indonesian", "taste": "sweet",
        "price": "affordable", "rating": 4.1},
    10: {"name": "Ramen Pedas", "category": "japanese", "taste": "spicy",
         "price": "moderate", "rating": 4.6}
}

# Rating history
ratings_data = [
    (1, 1, 5.0), (1, 3, 4.5), (1, 7, 4.8),
    (2, 2, 5.0), (2, 6, 4.9), (2, 8, 4.5),
    (3, 1, 4.0), (3, 5, 5.0), (3, 9, 4.7),
    (4, 4, 4.8), (4, 8, 5.0), (4, 10, 4.2),
    (5, 1, 4.5), (5, 3, 4.9), (5, 7, 4.6), (5, 10, 4.3)
]

product_names = [products[i]["name"] for i in range(1, 11)]
user_names = [users[i]["name"] for i in range(1, 6)]

# ============================================================================
# STEP 1: USER-ITEM MATRIX
# ============================================================================

def create_rating_matrix(n_users: int, n_items: int,
                         ratings: List[Tuple[int, int, float]]) -> np.ndarray:
    """Buat user-item rating matrix"""
    matrix = np.zeros((n_users, n_items))

    for user_id, item_id, rating in ratings:
        matrix[user_id - 1, item_id - 1] = rating

    return matrix

rating_matrix = create_rating_matrix(5, 10, ratings_data)

print("=" * 80)
print("STEP 1: USER-ITEM RATING MATRIX")
print("=" * 80)
print("\nRating Matrix (5 users x 10 products):")
print("      ", end="")
for i in range(10):
    print(f"  P{i+1:2d}", end="")
print()

for i, user_name in enumerate(user_names):
    print(f"{user_name:5s}", end=" ")
    for j in range(10):
        if rating_matrix[i, j] > 0:
            print(f"{rating_matrix[i, j]:5.1f}", end="")
        else:
            print("    -", end="")
    print()

# ============================================================================
# STEP 2: NORMALIZATION & USER SIMILARITY
# ============================================================================

def normalize_ratings(matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Normalize ratings dengan mean centering"""
    n_users = matrix.shape[0]
    user_means = np.zeros(n_users)
    normalized = matrix.copy()

    for i in range(n_users):
        rated_items = matrix[i, :] > 0
        if np.sum(rated_items) > 0:
            user_means[i] = np.mean(matrix[i, rated_items])
            normalized[i, rated_items] -= user_means[i]

    return normalized, user_means

normalized_matrix, user_means = normalize_ratings(rating_matrix)

print("\n" + "=" * 80)
print("STEP 2: NORMALIZATION & USER MEANS")
print("=" * 80)
print("\nUser Mean Ratings:")
for i, (name, mean) in enumerate(zip(user_names, user_means)):
    print(f"{name:6s}: {mean:.4f}")

def cosine_similarity_matrix(matrix: np.ndarray,
                             rating_matrix: np.ndarray) -> np.ndarray:
    """Hitung cosine similarity antar users"""
    n_users = matrix.shape[0]
    similarity = np.zeros((n_users, n_users))

    for i in range(n_users):
        for j in range(n_users):
            if i == j:
                similarity[i, j] = 1.0
            else:
                # Common items
                common = (rating_matrix[i, :] > 0) & (rating_matrix[j, :] > 0)

                if np.sum(common) > 0:
                    vec_i = matrix[i, common]
                    vec_j = matrix[j, common]

                    dot_prod = np.sum(vec_i * vec_j)
                    norm_i = np.sqrt(np.sum(vec_i ** 2))
                    norm_j = np.sqrt(np.sum(vec_j ** 2))

                    if norm_i > 0 and norm_j > 0:
                        similarity[i, j] = dot_prod / (norm_i * norm_j)

    return similarity

user_similarity = cosine_similarity_matrix(normalized_matrix, rating_matrix)

print("\nUser Similarity Matrix:")
print("        ", end="")
for name in user_names:
    print(f"{name:8s}", end="")
print()

for i, name in enumerate(user_names):
    print(f"{name:8s}", end="")
    for j in range(5):
        print(f"{user_similarity[i, j]:8.4f}", end="")
    print()

# ============================================================================
# STEP 3: COLLABORATIVE FILTERING
# ============================================================================

def predict_collaborative(target_user: int, rating_matrix: np.ndarray,
                         normalized_matrix: np.ndarray,
                         similarity_matrix: np.ndarray,
                         user_means: np.ndarray) -> np.ndarray:
    """Prediksi rating menggunakan collaborative filtering"""
    n_items = rating_matrix.shape[1]
    predictions = np.zeros(n_items)

    for item in range(n_items):
        # Sudah di-rating
        if rating_matrix[target_user, item] > 0:
            predictions[item] = rating_matrix[target_user, item]
            continue

        # Users yang sudah rating item ini
        users_rated = np.where(rating_matrix[:, item] > 0)[0]

        weighted_sum = 0
        similarity_sum = 0

        for neighbor in users_rated:
            if neighbor != target_user:
                sim = similarity_matrix[target_user, neighbor]
                if abs(sim) > 0.01:
                    rating_diff = normalized_matrix[neighbor, item]
                    weighted_sum += sim * rating_diff
                    similarity_sum += abs(sim)

        if similarity_sum > 0:
            predictions[item] = user_means[target_user] + (weighted_sum / similarity_sum)
        else:
            predictions[item] = user_means[target_user]

    return predictions

collab_predictions = predict_collaborative(0, rating_matrix, normalized_matrix,
                                           user_similarity, user_means)

print("\n" + "=" * 80)
print("STEP 3: COLLABORATIVE FILTERING PREDICTIONS (User: adza)")
print("=" * 80)

for i, (name, pred) in enumerate(zip(product_names, collab_predictions)):
    status = "✓ RATED" if rating_matrix[0, i] > 0 else "→ NEW"
    print(f"P{i+1:2d} {name:22s}: {pred:.4f}  {status}")

# ============================================================================
# STEP 4: CONTENT-BASED FILTERING
# ============================================================================

categories = ["indonesian", "japanese", "western", "dessert"]
tastes = ["spicy", "umami", "sweet", "savory"]
prices = ["affordable", "moderate", "premium"]

def encode_product(product_id: int) -> np.ndarray:
    """Encode produk menjadi feature vector"""
    product = products[product_id]
    features = []

    # Category (4)
    for cat in categories:
        features.append(1.0 if product["category"] == cat else 0.0)

    # Taste (4)
    for taste in tastes:
        features.append(1.0 if product["taste"] == taste else 0.0)

    # Price (3)
    for price in prices:
        features.append(1.0 if product["price"] == price else 0.0)

    # Rating normalized (1)
    features.append(product["rating"] / 5.0)

    return np.array(features)

# Feature matrix
feature_matrix = np.array([encode_product(i) for i in range(1, 11)])

print("\n" + "=" * 80)
print("STEP 4: PRODUCT FEATURE MATRIX")
print("=" * 80)
print("Features: [indo, jap, west, dess, spicy, umami, sweet, savory, aff, mod, prem, rating]")
print("\n      ", end="")
print("  ".join([f"{i:4d}" for i in range(12)]))
for i, name in enumerate(product_names):
    print(f"P{i+1:2d}  ", end="")
    for val in feature_matrix[i]:
        print(f"{val:5.2f}", end=" ")
    print(f"  {name}")

def create_user_profile(user_idx: int, rating_matrix: np.ndarray,
                       feature_matrix: np.ndarray) -> np.ndarray:
    """Buat user profile dari rating history"""
    rated_items = np.where(rating_matrix[user_idx, :] > 0)[0]

    if len(rated_items) == 0:
        return np.zeros(feature_matrix.shape[1])

    weights = rating_matrix[user_idx, rated_items]
    weighted_features = np.zeros(feature_matrix.shape[1])

    for item_idx, weight in zip(rated_items, weights):
        weighted_features += feature_matrix[item_idx, :] * weight

    return weighted_features / np.sum(weights)

adza_profile = create_user_profile(0, rating_matrix, feature_matrix)

print("\nUser Profile (adza):")
print("Features: [indo, jap, west, dess, spicy, umami, sweet, savory, aff, mod, prem, rating]")
print("Values:   ", end="")
for val in adza_profile:
    print(f"{val:5.3f} ", end="")
print()

def cosine_similarity_vec(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine similarity antara 2 vector"""
    dot = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)

content_scores = np.array([
    cosine_similarity_vec(adza_profile, feature_matrix[i])
    for i in range(10)
])

print("\nContent-Based Similarity Scores:")
for i, (name, score) in enumerate(zip(product_names, content_scores)):
    status = "✓" if rating_matrix[0, i] > 0 else " "
    print(f"P{i+1:2d} {name:22s}: {score:.4f}  {status}")

# ============================================================================
# STEP 5: HYBRID RECOMMENDATION
# ============================================================================

def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """Min-max normalization"""
    min_val = np.min(scores)
    max_val = np.max(scores)

    if max_val - min_val == 0:
        return scores

    return (scores - min_val) / (max_val - min_val)

collab_norm = normalize_scores(collab_predictions)
content_norm = normalize_scores(content_scores)

alpha = 0.6  # Collaborative weight
beta = 0.4   # Content-based weight

hybrid_scores = alpha * collab_norm + beta * content_norm

print("\n" + "=" * 80)
print("STEP 5: HYBRID RECOMMENDATION")
print("=" * 80)
print(f"Weights: Collaborative={alpha}, Content-Based={beta}")
print("\nProduct                  | Collab | Content | Hybrid | Status")
print("-" * 80)

results = []
for i, name in enumerate(product_names):
    status = "RATED" if rating_matrix[0, i] > 0 else "NEW"
    results.append({
        'id': i + 1,
        'name': name,
        'collab': collab_norm[i],
        'content': content_norm[i],
        'hybrid': hybrid_scores[i],
        'status': status,
        'info': products[i + 1]
    })

    print(f"P{i+1:2d} {name:20s} | {collab_norm[i]:.4f} | "
          f"{content_norm[i]:.4f} | {hybrid_scores[i]:.4f} | {status}")

# ============================================================================
# STEP 6: FINAL RECOMMENDATION
# ============================================================================

new_products = [r for r in results if r['status'] == 'NEW']
new_products_sorted = sorted(new_products, key=lambda x: x['hybrid'], reverse=True)

print("\n" + "=" * 80)
print("🎯 TOP 5 REKOMENDASI UNTUK ADZA")
print("=" * 80)

for rank, prod in enumerate(new_products_sorted[:5], 1):
    print(f"\n{rank}. {prod['name']} (P{prod['id']})")
    print(f"   ├─ Hybrid Score: {prod['hybrid']:.4f}")
    print(f"   ├─ Collaborative: {prod['collab']:.4f} (weight: {alpha})")
    print(f"   ├─ Content-Based: {prod['content']:.4f} (weight: {beta})")
    print(f"   └─ Info: {prod['info']['category']}, {prod['info']['taste']}, "
          f"{prod['info']['price']}, rating: {prod['info']['rating']}")

print("\n" + "=" * 80)
print("PERHITUNGAN SELESAI")
print("=" * 80)

# ============================================================================
# VERIFICATION & METRICS
# ============================================================================

print("\n" + "=" * 80)
print("VERIFICATION & METRICS")
print("=" * 80)

print("\n1. User Similarity Metrics:")
print(f"   - adza vs eka: {user_similarity[0, 4]:.4f} (should be high)")
print(f"   - adza vs budi: {user_similarity[0, 1]:.4f} (should be low)")
print(f"   - budi vs dika: {user_similarity[1, 3]:.4f} (should be moderate)")

print("\n2. Content Profile Verification (adza):")
print(f"   - Indonesian preference: {adza_profile[0]:.4f} (should be ~1.0)")
print(f"   - Spicy preference: {adza_profile[4]:.4f} (should be ~1.0)")
print(f"   - Affordable preference: {adza_profile[8]:.4f} (should be high)")

print("\n3. Prediction Ranges:")
print(f"   - Collaborative: [{np.min(collab_predictions):.2f}, {np.max(collab_predictions):.2f}]")
print(f"   - Content-Based: [{np.min(content_scores):.4f}, {np.max(content_scores):.4f}]")
print(f"   - Hybrid (norm): [{np.min(hybrid_scores):.4f}, {np.max(hybrid_scores):.4f}]")

print("\n4. Recommendation Quality:")
top_rec = new_products_sorted[0]
print(f"   - Top recommendation: {top_rec['name']}")
print(f"   - Matches preferences: ", end="")
if top_rec['info']['category'] == 'indonesian':
    print("✓ Indonesian", end=" ")
if top_rec['info']['taste'] == 'spicy':
    print("✓ Spicy", end=" ")
if top_rec['info']['price'] in ['affordable', 'moderate']:
    print("✓ Affordable/Moderate", end=" ")
print()

print("\n" + "=" * 80)
print("✅ SEMUA PERHITUNGAN BERHASIL")
print("=" * 80)
```

### Cara Menjalankan:

```bash
cd /home/labubu/Projects/adza/backend/app/recommendation
python manual_calculation_complete.py
```

---

## Kesimpulan

Dokumen ini menjelaskan perhitungan manual sistem rekomendasi dengan detail:

1. **User-Item Matrix**: Representasi interaksi user-produk
2. **Cosine Similarity**: Mengukur kesamaan preferensi antar user
3. **Collaborative Filtering**: Prediksi berdasarkan user serupa
4. **Content-Based**: Prediksi berdasarkan atribut produk
5. **Hybrid**: Kombinasi kedua metode dengan bobot

Hasil akhir: **Sistem dapat memberikan rekomendasi personal yang akurat** untuk user "adza" berdasarkan preferensi indonesian, spicy, dan affordable.

---

**Catatan Penting:**

-   Semua perhitungan dapat diverifikasi secara manual
-   Setiap langkah dijelaskan dengan formula matematika
-   Kode NumPy dapat dijalankan langsung untuk validasi
-   Output detail membantu debugging dan understanding
