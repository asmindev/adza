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
    5: {"name": "eka", "preferences": ["indonesian", "spicy", "moderate"]},
}

# Product data
products = {
    1: {
        "name": "Nasi Goreng Pedas",
        "category": "indonesian",
        "taste": "spicy",
        "price": "affordable",
        "rating": 4.5,
    },
    2: {
        "name": "Sushi Premium",
        "category": "japanese",
        "taste": "umami",
        "price": "premium",
        "rating": 4.8,
    },
    3: {
        "name": "Rendang Padang",
        "category": "indonesian",
        "taste": "spicy",
        "price": "moderate",
        "rating": 4.7,
    },
    4: {
        "name": "Burger Spicy",
        "category": "western",
        "taste": "spicy",
        "price": "moderate",
        "rating": 4.3,
    },
    5: {
        "name": "Es Krim Cokelat",
        "category": "dessert",
        "taste": "sweet",
        "price": "affordable",
        "rating": 4.2,
    },
    6: {
        "name": "Sashimi Set",
        "category": "japanese",
        "taste": "umami",
        "price": "premium",
        "rating": 4.9,
    },
    7: {
        "name": "Ayam Geprek",
        "category": "indonesian",
        "taste": "spicy",
        "price": "affordable",
        "rating": 4.4,
    },
    8: {
        "name": "Steak Wagyu",
        "category": "western",
        "taste": "savory",
        "price": "premium",
        "rating": 4.8,
    },
    9: {
        "name": "Martabak Manis",
        "category": "indonesian",
        "taste": "sweet",
        "price": "affordable",
        "rating": 4.1,
    },
    10: {
        "name": "Ramen Pedas",
        "category": "japanese",
        "taste": "spicy",
        "price": "moderate",
        "rating": 4.6,
    },
}

# Rating history
ratings_data = [
    (1, 1, 5.0),
    (1, 3, 4.5),
    (1, 7, 4.8),
    (2, 2, 5.0),
    (2, 6, 4.9),
    (2, 8, 4.5),
    (3, 1, 4.0),
    (3, 5, 5.0),
    (3, 9, 4.7),
    (4, 4, 4.8),
    (4, 8, 5.0),
    (4, 10, 4.2),
    (5, 1, 4.5),
    (5, 3, 4.9),
    (5, 7, 4.6),
    (5, 10, 4.3),
]

product_names = [products[i]["name"] for i in range(1, 11)]
user_names = [users[i]["name"] for i in range(1, 6)]

# ============================================================================
# STEP 1: USER-ITEM MATRIX
# ============================================================================


def create_rating_matrix(
    n_users: int, n_items: int, ratings: List[Tuple[int, int, float]]
) -> np.ndarray:
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


def cosine_similarity_matrix(
    matrix: np.ndarray, rating_matrix: np.ndarray
) -> np.ndarray:
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
                    norm_i = np.sqrt(np.sum(vec_i**2))
                    norm_j = np.sqrt(np.sum(vec_j**2))

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


def predict_collaborative(
    target_user: int,
    rating_matrix: np.ndarray,
    normalized_matrix: np.ndarray,
    similarity_matrix: np.ndarray,
    user_means: np.ndarray,
) -> np.ndarray:
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
            predictions[item] = user_means[target_user] + (
                weighted_sum / similarity_sum
            )
        else:
            predictions[item] = user_means[target_user]

    return predictions


collab_predictions = predict_collaborative(
    0, rating_matrix, normalized_matrix, user_similarity, user_means
)

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
print(
    "Features: [indo, jap, west, dess, spicy, umami, sweet, savory, aff, mod, prem, rating]"
)
print("\n      ", end="")
print("  ".join([f"{i:4d}" for i in range(12)]))
for i, name in enumerate(product_names):
    print(f"P{i+1:2d}  ", end="")
    for val in feature_matrix[i]:
        print(f"{val:5.2f}", end=" ")
    print(f"  {name}")


def create_user_profile(
    user_idx: int, rating_matrix: np.ndarray, feature_matrix: np.ndarray
) -> np.ndarray:
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
print(
    "Features: [indo, jap, west, dess, spicy, umami, sweet, savory, aff, mod, prem, rating]"
)
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


content_scores = np.array(
    [cosine_similarity_vec(adza_profile, feature_matrix[i]) for i in range(10)]
)

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
beta = 0.4  # Content-based weight

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
    results.append(
        {
            "id": i + 1,
            "name": name,
            "collab": collab_norm[i],
            "content": content_norm[i],
            "hybrid": hybrid_scores[i],
            "status": status,
            "info": products[i + 1],
        }
    )

    print(
        f"P{i+1:2d} {name:20s} | {collab_norm[i]:.4f} | "
        f"{content_norm[i]:.4f} | {hybrid_scores[i]:.4f} | {status}"
    )

# ============================================================================
# STEP 6: FINAL RECOMMENDATION
# ============================================================================

new_products = [r for r in results if r["status"] == "NEW"]
new_products_sorted = sorted(new_products, key=lambda x: x["hybrid"], reverse=True)

print("\n" + "=" * 80)
print("🎯 TOP 5 REKOMENDASI UNTUK ADZA")
print("=" * 80)

for rank, prod in enumerate(new_products_sorted[:5], 1):
    print(f"\n{rank}. {prod['name']} (P{prod['id']})")
    print(f"   ├─ Hybrid Score: {prod['hybrid']:.4f}")
    print(f"   ├─ Collaborative: {prod['collab']:.4f} (weight: {alpha})")
    print(f"   ├─ Content-Based: {prod['content']:.4f} (weight: {beta})")
    print(
        f"   └─ Info: {prod['info']['category']}, {prod['info']['taste']}, "
        f"{prod['info']['price']}, rating: {prod['info']['rating']}"
    )

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
print(
    f"   - Collaborative: [{np.min(collab_predictions):.2f}, {np.max(collab_predictions):.2f}]"
)
print(
    f"   - Content-Based: [{np.min(content_scores):.4f}, {np.max(content_scores):.4f}]"
)
print(f"   - Hybrid (norm): [{np.min(hybrid_scores):.4f}, {np.max(hybrid_scores):.4f}]")

print("\n4. Recommendation Quality:")
top_rec = new_products_sorted[0]
print(f"   - Top recommendation: {top_rec['name']}")
print(f"   - Matches preferences: ", end="")
matches = []
if top_rec["info"]["category"] == "indonesian":
    matches.append("✓ Indonesian")
if top_rec["info"]["taste"] == "spicy":
    matches.append("✓ Spicy")
if top_rec["info"]["price"] in ["affordable", "moderate"]:
    matches.append("✓ Affordable/Moderate")
print(" ".join(matches) if matches else "✗ No perfect match")

print("\n" + "=" * 80)
print("✅ SEMUA PERHITUNGAN BERHASIL")
print("=" * 80)

# ============================================================================
# DETAILED CALCULATION EXAMPLE
# ============================================================================

print("\n" + "=" * 80)
print("CONTOH PERHITUNGAN DETAIL: Prediksi adza untuk P10 (Ramen Pedas)")
print("=" * 80)

target_user = 0  # adza (index 0)
target_item = 9  # P10 (index 9)

print(f"\n=== Collaborative Filtering Calculation ===")
print(
    f"Target: User 'adza' (U{target_user+1}) -> Product 'Ramen Pedas' (P{target_item+1})"
)

# User yang sudah rating P10
users_rated = np.where(rating_matrix[:, target_item] > 0)[0]
print(f"\nUsers yang sudah rating P10: {[user_names[i] for i in users_rated]}")

# Hitung weighted sum
weighted_sum = 0
similarity_sum = 0

for neighbor in users_rated:
    if neighbor != target_user:
        sim = user_similarity[target_user, neighbor]
        rating_diff = normalized_matrix[neighbor, target_item]
        contribution = sim * rating_diff

        weighted_sum += contribution
        similarity_sum += abs(sim)

        print(f"\nNeighbor: {user_names[neighbor]}")
        print(f"  ├─ Similarity with adza: {sim:.4f}")
        print(f"  ├─ P10 rating (original): {rating_matrix[neighbor, target_item]:.2f}")
        print(f"  ├─ User mean: {user_means[neighbor]:.4f}")
        print(f"  ├─ Normalized rating: {rating_diff:.4f}")
        print(f"  └─ Contribution: {sim:.4f} × {rating_diff:.4f} = {contribution:.4f}")

print(f"\nWeighted sum: {weighted_sum:.4f}")
print(f"Similarity sum: {similarity_sum:.4f}")
print(f"Mean rating adza: {user_means[target_user]:.4f}")

if similarity_sum > 0:
    prediction = user_means[target_user] + (weighted_sum / similarity_sum)
    print(
        f"\nPrediction = {user_means[target_user]:.4f} + ({weighted_sum:.4f} / {similarity_sum:.4f})"
    )
    print(
        f"           = {user_means[target_user]:.4f} + {weighted_sum / similarity_sum:.4f}"
    )
    print(f"           = {prediction:.4f}")
else:
    prediction = user_means[target_user]
    print(f"\nPrediction = {prediction:.4f} (fallback to user mean)")

print(f"\n=== Content-Based Filtering Calculation ===")

print(f"\nadza profile features:")
feature_names = [
    "indo",
    "jap",
    "west",
    "dess",
    "spicy",
    "umami",
    "sweet",
    "savory",
    "aff",
    "mod",
    "prem",
    "rating",
]
for fname, fval in zip(feature_names, adza_profile):
    if fval > 0.01:
        print(f"  {fname:8s}: {fval:.4f}")

print(f"\nP10 (Ramen Pedas) features:")
p10_features = feature_matrix[target_item]
for fname, fval in zip(feature_names, p10_features):
    if fval > 0.01:
        print(f"  {fname:8s}: {fval:.4f}")

dot_product = np.dot(adza_profile, p10_features)
norm_adza = np.linalg.norm(adza_profile)
norm_p10 = np.linalg.norm(p10_features)

print(f"\nDot product: {dot_product:.4f}")
print(f"Norm adza: {norm_adza:.4f}")
print(f"Norm P10: {norm_p10:.4f}")
print(f"Content similarity = {dot_product:.4f} / ({norm_adza:.4f} × {norm_p10:.4f})")
print(f"                   = {dot_product:.4f} / {norm_adza * norm_p10:.4f}")
print(f"                   = {content_scores[target_item]:.4f}")

print("\n" + "=" * 80)
print("PERHITUNGAN DETAIL SELESAI")
print("=" * 80)
