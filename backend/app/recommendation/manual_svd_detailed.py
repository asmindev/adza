"""
Detailed SVD Calculation with Step-by-Step Analysis
====================================================
Script ini menampilkan perhitungan SVD secara detail:
1. 20 users (15 paling mirip + 5 paling tidak mirip) dengan user 'adza'
2. Perhitungan cosine similarity detail dalam tabel
3. SVD decomposition (U × Σ × V^T) dengan visualisasi matrix
4. Hasil rekomendasi final

Author: Recommendation System Team
Date: October 24, 2025
"""

import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scipy.sparse.linalg import svds
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.rule import Rule

# Import models
from app.modules.user.models import User
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from app.extensions import db

# Rich Console
console = Console()


# ============================================================================
# STEP 1: DISPLAY 20 USERS (15 SIMILAR + 5 DISSIMILAR)
# ============================================================================


def display_20_users_similarity(target_user_id):
    """
    Tampilkan users yang mirip dengan target user (similarity > 0)
    """
    console.rule("[bold cyan]📊 STEP 1: SIMILAR USERS ANALYSIS", style="cyan")

    # Get all users and their ratings
    all_users = User.query.filter_by(role="user").all()
    target_user = db.session.get(User, target_user_id)

    if not target_user:
        console.print("[red]❌ Target user not found[/red]")
        return None, None, None

    # Build rating vectors for all users
    all_foods = Food.query.all()
    food_ids = [f.id for f in all_foods]

    console.print(
        f"\n[cyan]Building rating matrix for {len(all_users)} users and {len(food_ids)} foods...[/cyan]"
    )

    # Create rating vectors
    user_vectors = {}
    for user in all_users:
        ratings = FoodRating.query.filter_by(user_id=user.id).all()
        vector = np.zeros(len(food_ids))
        for rating in ratings:
            if rating.food_id in food_ids:
                idx = food_ids.index(rating.food_id)
                vector[idx] = rating.rating
        user_vectors[user.id] = {
            "vector": vector,
            "name": user.name,
            "username": user.username,
            "num_ratings": len(ratings),
        }

    # Calculate cosine similarity with target user
    target_vector = user_vectors[target_user_id]["vector"]
    similarities = []

    for user_id, data in user_vectors.items():
        if user_id == target_user_id:
            continue

        user_vector = data["vector"]

        # Find common rated items
        common_mask = (target_vector > 0) & (user_vector > 0)
        common_count = np.sum(common_mask)

        if common_count > 0:
            # Cosine similarity calculation
            dot_product = np.dot(target_vector[common_mask], user_vector[common_mask])
            norm_target = np.linalg.norm(target_vector[common_mask])
            norm_user = np.linalg.norm(user_vector[common_mask])

            if norm_target > 0 and norm_user > 0:
                similarity = dot_product / (norm_target * norm_user)
            else:
                similarity = 0.0
        else:
            similarity = 0.0
            dot_product = 0
            norm_target = 0
            norm_user = 0

        similarities.append(
            {
                "user_id": user_id,
                "name": data["name"],
                "username": data["username"],
                "similarity": similarity,
                "common_items": common_count,
                "num_ratings": data["num_ratings"],
                "dot_product": dot_product,
                "norm_target": norm_target,
                "norm_user": norm_user,
            }
        )

    # Sort by similarity
    similarities.sort(key=lambda x: x["similarity"], reverse=True)

    # Filter only similar users (similarity > 0)
    similar_users = [s for s in similarities if s["similarity"] > 0]

    console.print(
        f"[green]✓[/green] Calculated similarity for {len(similarities)} users"
    )
    console.print(
        f"[green]✓[/green] Found {len(similar_users)} similar users (similarity > 0)\n"
    )

    if len(similar_users) == 0:
        console.print(
            "[yellow]⚠️  No similar users found (no common rated items)[/yellow]"
        )
        return None, target_vector, user_vectors

    # Display table
    table = Table(
        title=f"🎯 Similar Users with {target_user.name} (@{target_user.username})",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Rank", justify="center", style="cyan", width=6)
    table.add_column("User ID", justify="left", style="yellow", width=12)
    table.add_column("Name", justify="left", style="white", width=20)
    table.add_column("Common Items", justify="center", style="magenta", width=13)
    table.add_column("Similarity", justify="right", style="green", width=12)
    table.add_column("Visual", justify="left", width=25)

    for idx, user_data in enumerate(similar_users, 1):
        similarity = user_data["similarity"]

        rank_str = f"#{idx}"

        # Visual bar
        bar_length = int(similarity * 25) if similarity > 0 else 0
        bar = "█" * bar_length + "░" * (25 - bar_length)

        # Color based on similarity
        if similarity >= 0.8:
            sim_style = "bold green"
        elif similarity >= 0.5:
            sim_style = "green"
        elif similarity >= 0.2:
            sim_style = "yellow"
        else:
            sim_style = "red"

        table.add_row(
            rank_str,
            user_data["user_id"][:12] + "...",
            user_data["name"][:20],
            str(user_data["common_items"]),
            f"[{sim_style}]{similarity:.4f}[/{sim_style}]",
            f"[{sim_style}]{bar}[/{sim_style}]",
        )

    console.print(table)

    # Display statistics
    console.print("\n[bold cyan]📈 Similarity Statistics:[/bold cyan]")
    sim_values = [u["similarity"] for u in similar_users]
    console.print(f"  • Total similar users: {len(similar_users)}")
    console.print(f"  • Average similarity: {np.mean(sim_values):.4f}")
    console.print(f"  • Max similarity: {np.max(sim_values):.4f}")
    console.print(f"  • Min similarity: {np.min(sim_values):.4f}")
    console.print(f"  • Std deviation: {np.std(sim_values):.4f}\n")

    return similar_users, target_vector, user_vectors


# ============================================================================
# STEP 2: DETAILED SIMILARITY CALCULATION
# ============================================================================


def display_detailed_similarity_calculation(similar_users, target_user_id):
    """
    Tampilkan perhitungan cosine similarity detail untuk similar users
    """
    console.rule("[bold cyan]🔢 STEP 2: DETAILED SIMILARITY CALCULATION", style="cyan")

    table = Table(
        title="Detailed Cosine Similarity Calculation",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("User", justify="left", style="cyan", width=15)
    table.add_column(
        "Dot Product\n(Σ rᵢ·rⱼ)", justify="right", style="yellow", width=15
    )
    table.add_column("||Target||\n(√Σrᵢ²)", justify="right", style="green", width=15)
    table.add_column("||User||\n(√Σrⱼ²)", justify="right", style="green", width=15)
    table.add_column(
        "Similarity\n(cosine)", justify="right", style="bold white", width=15
    )
    table.add_column("Formula", justify="left", style="blue", width=25)

    for user_data in similar_users:
        dot = user_data["dot_product"]
        norm_t = user_data["norm_target"]
        norm_u = user_data["norm_user"]
        sim = user_data["similarity"]

        if norm_t > 0 and norm_u > 0:
            formula = f"{dot:.2f}/({norm_t:.2f}×{norm_u:.2f})"
        else:
            formula = "N/A"

        table.add_row(
            user_data["name"][:15],
            f"{dot:.4f}",
            f"{norm_t:.4f}",
            f"{norm_u:.4f}",
            f"{sim:.4f}",
            formula,
        )

    console.print(table)
    console.print(
        "\n[italic]Formula: similarity(u,v) = (u·v) / (||u|| × ||v||)[/italic]\n"
    )


# ============================================================================
# STEP 2.5: USER RATING MATRIX VISUALIZATION
# ============================================================================


def display_user_rating_matrix(similar_users, target_user_id, user_vectors):
    """
    Display rating matrix showing which foods each user has rated
    """
    console.rule("[bold cyan]📊 USER-ITEM RATING MATRIX", style="cyan")

    # Build user list
    all_user_ids = [target_user_id] + [u["user_id"] for u in similar_users]

    # Get all foods that have been rated by these users
    rated_food_ids = set()
    for user_id in all_user_ids:
        vector = user_vectors[user_id]["vector"]
        rated_food_ids.update(np.where(vector > 0)[0])

    rated_food_ids = sorted(list(rated_food_ids))

    # Get food details
    all_foods = Food.query.all()
    food_dict = {f.id: f for f in all_foods}
    food_id_list = [f.id for f in all_foods]

    console.print(
        f"\n[cyan]Displaying rating matrix for {len(all_user_ids)} users × {len(rated_food_ids)} foods...[/cyan]\n"
    )

    # Create rating matrix table
    rating_table = Table(
        title="🍽️ User-Item Rating Matrix",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )

    rating_table.add_column(
        "User", justify="left", style="cyan", width=15, no_wrap=True
    )

    # Add food columns (show food names)
    food_names = []
    for food_idx in rated_food_ids:
        food_id = food_id_list[food_idx]
        food = food_dict.get(food_id)
        if food:
            food_name = food.name[:12]  # Truncate long names
            food_names.append(food_name)
            rating_table.add_column(
                food_name, justify="center", style="white", width=13
            )
        else:
            food_names.append("Unknown")
            rating_table.add_column(
                "Unknown", justify="center", style="white", width=13
            )

    # Add rows for each user
    for user_id in all_user_ids:
        user = db.session.get(User, user_id)
        user_name = user.name[:15] if user else "Unknown"

        # Mark target user
        if user_id == target_user_id:
            user_display = f"[bold yellow]{user_name} (TARGET)[/bold yellow]"
        else:
            user_display = user_name

        row_data = [user_display]

        # Get ratings for this user
        user_full_vector = user_vectors[user_id]["vector"]

        for food_idx in rated_food_ids:
            rating = user_full_vector[food_idx]
            if rating > 0:
                # Color code ratings: high=green, medium=yellow, low=red
                if rating >= 4.5:
                    row_data.append(f"[bold green]{rating:.1f}[/bold green]")
                elif rating >= 4.0:
                    row_data.append(f"[green]{rating:.1f}[/green]")
                elif rating >= 3.5:
                    row_data.append(f"[yellow]{rating:.1f}[/yellow]")
                else:
                    row_data.append(f"[red]{rating:.1f}[/red]")
            else:
                row_data.append("[dim]-[/dim]")

        rating_table.add_row(*row_data)

    console.print(rating_table)

    # Statistics
    console.print("\n[bold cyan]📈 Matrix Statistics:[/bold cyan]")

    total_cells = len(all_user_ids) * len(rated_food_ids)
    filled_cells = 0

    for user_id in all_user_ids:
        user_full_vector = user_vectors[user_id]["vector"]
        for food_idx in rated_food_ids:
            if user_full_vector[food_idx] > 0:
                filled_cells += 1

    sparsity = 1 - (filled_cells / total_cells) if total_cells > 0 else 0

    console.print(
        f"  • Matrix size: [bold]{len(all_user_ids)} users × {len(rated_food_ids)} foods[/bold]"
    )
    console.print(f"  • Total cells: [bold]{total_cells}[/bold]")
    console.print(f"  • Filled cells: [bold green]{filled_cells}[/bold green]")
    console.print(f"  • Empty cells: [bold red]{total_cells - filled_cells}[/bold red]")
    console.print(f"  • Sparsity: [bold]{sparsity*100:.2f}%[/bold]")
    console.print(f"  • Density: [bold green]{(1-sparsity)*100:.2f}%[/bold green]\n")

    # Rating distribution per user
    console.print("[bold cyan]📊 Rating Distribution per User:[/bold cyan]\n")

    dist_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")

    dist_table.add_column("User", justify="left", style="cyan", width=15)
    dist_table.add_column("Items Rated", justify="center", style="green", width=12)
    dist_table.add_column("Avg Rating", justify="center", style="yellow", width=12)
    dist_table.add_column("Min", justify="center", style="red", width=8)
    dist_table.add_column("Max", justify="center", style="green", width=8)
    dist_table.add_column("Rating Range", justify="left", style="blue", width=30)

    for user_id in all_user_ids:
        user = db.session.get(User, user_id)
        user_name = user.name[:15] if user else "Unknown"

        if user_id == target_user_id:
            user_display = f"[bold]{user_name} *[/bold]"
        else:
            user_display = user_name

        user_full_vector = user_vectors[user_id]["vector"]
        user_ratings = []

        for food_idx in rated_food_ids:
            rating = user_full_vector[food_idx]
            if rating > 0:
                user_ratings.append(rating)

        if user_ratings:
            avg_rating = np.mean(user_ratings)
            min_rating = np.min(user_ratings)
            max_rating = np.max(user_ratings)

            # Visual bar
            bar_length = int((avg_rating / 5.0) * 20)
            visual_bar = "█" * bar_length + "░" * (20 - bar_length)

            dist_table.add_row(
                user_display,
                str(len(user_ratings)),
                f"{avg_rating:.2f}",
                f"{min_rating:.1f}",
                f"{max_rating:.1f}",
                visual_bar,
            )
        else:
            dist_table.add_row(
                user_display, "0", "-", "-", "-", "[dim]No ratings[/dim]"
            )

    console.print(dist_table)
    console.print("[dim]* = Target user[/dim]\n")


# ============================================================================
# STEP 3: SVD DECOMPOSITION
# ============================================================================


def perform_svd_on_selected_users(
    similar_users, target_user_id, target_vector, user_vectors
):
    """
    Perform SVD decomposition on similar users + target user
    """
    console.rule("[bold cyan]🔬 STEP 3: SVD DECOMPOSITION", style="cyan")

    # Build matrix for similar users + target
    all_user_ids = [target_user_id] + [u["user_id"] for u in similar_users]
    num_users = len(all_user_ids)

    # Get all foods that have been rated by these users
    rated_food_ids = set()
    for user_id in all_user_ids:
        vector = user_vectors[user_id]["vector"]
        rated_food_ids.update(np.where(vector > 0)[0])

    rated_food_ids = sorted(list(rated_food_ids))

    console.print(
        f"\n[cyan]Building matrix for {num_users} users × {len(rated_food_ids)} foods...[/cyan]"
    )

    # Build rating matrix
    rating_matrix = np.zeros((num_users, len(rated_food_ids)))
    for i, user_id in enumerate(all_user_ids):
        full_vector = user_vectors[user_id]["vector"]
        for j, food_idx in enumerate(rated_food_ids):
            rating_matrix[i, j] = full_vector[food_idx]

    console.print(f"[green]✓[/green] Matrix shape: {rating_matrix.shape}")
    console.print(
        f"[green]✓[/green] Sparsity: {np.sum(rating_matrix == 0) / rating_matrix.size * 100:.2f}%\n"
    )

    # Mean centering
    user_means = np.zeros(num_users)
    for i in range(num_users):
        rated_mask = rating_matrix[i, :] > 0
        if np.sum(rated_mask) > 0:
            user_means[i] = np.mean(rating_matrix[i, rated_mask])

    centered_matrix = rating_matrix.copy()
    for i in range(num_users):
        mask = rating_matrix[i, :] > 0
        centered_matrix[i, mask] -= user_means[i]

    # Perform SVD
    n_factors = min(10, min(centered_matrix.shape) - 1)

    console.print(
        f"[cyan]Performing SVD decomposition with k={n_factors} factors...[/cyan]"
    )

    U, sigma, Vt = svds(centered_matrix, k=n_factors)

    # Sort by singular values (descending)
    idx = np.argsort(sigma)[::-1]
    sigma = sigma[idx]
    U = U[:, idx]
    Vt = Vt[idx, :]

    console.print(f"[green]✓[/green] SVD completed\n")

    # Display SVD matrices
    console.print("[bold cyan]📊 SVD Decomposition Results:[/bold cyan]\n")

    # Singular values table
    table = Table(
        title="Singular Values (Σ)",
        box=box.DOUBLE,
        show_header=True,
        header_style="bold yellow",
    )

    table.add_column("Factor", justify="center", style="cyan", width=10)
    table.add_column("Singular Value", justify="right", style="green", width=18)
    table.add_column("Variance %", justify="right", style="magenta", width=15)
    table.add_column("Cumulative %", justify="right", style="blue", width=15)
    table.add_column("Visual", justify="left", width=30)

    total_variance = np.sum(sigma**2)
    cumulative = 0

    for i, s in enumerate(sigma):
        variance_pct = (s**2 / total_variance) * 100
        cumulative += variance_pct

        bar_length = int(variance_pct / 100 * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)

        table.add_row(
            f"σ{i+1}", f"{s:.6f}", f"{variance_pct:.2f}%", f"{cumulative:.2f}%", bar
        )

    console.print(table)

    # U matrix (User-Feature) sample
    console.print(
        f"\n[bold cyan]User-Feature Matrix (U) - Shape: {U.shape}[/bold cyan]"
    )
    u_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    u_table.add_column("User", justify="left", style="yellow", width=15)

    for i in range(min(5, n_factors)):
        u_table.add_column(f"F{i+1}", justify="right", style="green", width=12)

    for i in range(min(10, num_users)):
        user_id = all_user_ids[i]
        user_name = user_vectors[user_id]["name"][:15]
        row = [user_name]
        for j in range(min(5, n_factors)):
            row.append(f"{U[i, j]:.4f}")
        u_table.add_row(*row)

    if num_users > 10:
        u_table.add_row("...", *["..."] * min(5, n_factors))

    console.print(u_table)

    # Vt matrix (Feature-Item) sample
    console.print(
        f"\n[bold cyan]Feature-Item Matrix (Vᵀ) - Shape: {Vt.shape}[/bold cyan]"
    )
    vt_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    vt_table.add_column("Factor", justify="left", style="yellow", width=10)

    for i in range(min(10, len(rated_food_ids))):
        vt_table.add_column(f"Item{i+1}", justify="right", style="green", width=10)

    for i in range(min(5, n_factors)):
        row = [f"F{i+1}"]
        for j in range(min(10, len(rated_food_ids))):
            row.append(f"{Vt[i, j]:.3f}")
        vt_table.add_row(*row)

    if n_factors > 5:
        vt_table.add_row("...", *["..."] * min(10, len(rated_food_ids)))

    console.print(vt_table)

    # Reconstruction
    console.print(f"\n[cyan]📐 Matrix Reconstruction: R ≈ U × Σ × Vᵀ[/cyan]")

    sigma_matrix = np.diag(sigma)
    reconstructed = np.dot(U, np.dot(sigma_matrix, Vt))

    # Add back user means
    for i in range(num_users):
        reconstructed[i, :] += user_means[i]

    console.print(
        f"[green]✓[/green] Reconstructed matrix shape: {reconstructed.shape}\n"
    )

    return (
        reconstructed,
        all_user_ids,
        rated_food_ids,
        user_vectors,
        sigma_matrix,
        U,
        rating_matrix,
    )


# ============================================================================
# STEP 4: FINAL RECOMMENDATIONS
# ============================================================================


def display_final_recommendations(
    reconstructed, all_user_ids, rated_food_ids, user_vectors, target_user_id
):
    """
    Generate and display recommendations from SVD results
    """
    console.rule("[bold cyan]🎯 STEP 4: FINAL RECOMMENDATIONS", style="cyan")

    # Get target user index
    target_idx = all_user_ids.index(target_user_id)
    target_user = db.session.get(User, target_user_id)

    # Get predictions for target user
    target_predictions = reconstructed[target_idx, :]

    # Get foods
    all_foods = Food.query.all()
    food_dict = {f.id: f for f in all_foods}

    # Map food indices to food IDs
    food_id_list = [f.id for f in all_foods]

    # Get items user hasn't rated
    target_full_vector = user_vectors[target_user_id]["vector"]

    recommendations = []
    for j, food_idx in enumerate(rated_food_ids):
        # Check if user hasn't rated this item
        if target_full_vector[food_idx] == 0:
            predicted_rating = max(1.0, min(5.0, target_predictions[j]))

            if predicted_rating >= 3.0:  # Minimum threshold
                food_id = food_id_list[food_idx]
                food = food_dict.get(food_id)
                if food:
                    recommendations.append(
                        {
                            "food_id": food_id,
                            "name": food.name,
                            "predicted_rating": predicted_rating,
                            "price": food.price if hasattr(food, "price") else 0,
                        }
                    )

    # Sort by predicted rating
    recommendations.sort(key=lambda x: x["predicted_rating"], reverse=True)
    top_10 = recommendations[:10]

    console.print(
        f"\n[green]✓[/green] Generated {len(recommendations)} recommendations"
    )
    console.print(f"[green]✓[/green] Showing top 10\n")

    # Display recommendations table
    table = Table(
        title=f"🍽️ Top 10 Recommendations for {target_user.name}",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold green",
    )

    table.add_column("Rank", justify="center", style="cyan", width=8)
    table.add_column("Food Name", justify="left", style="white", width=35)
    table.add_column("Price", justify="right", style="yellow", width=15)
    table.add_column("Predicted Rating", justify="right", style="green", width=18)
    table.add_column("Stars", justify="center", style="yellow", width=15)

    for idx, rec in enumerate(top_10, 1):
        stars = "⭐" * int(round(rec["predicted_rating"]))

        table.add_row(
            f"#{idx}",
            rec["name"][:35],
            f"Rp {rec['price']:,}",
            f"{rec['predicted_rating']:.2f}",
            stars,
        )

    console.print(table)

    # Statistics
    if top_10:
        console.print("\n[bold cyan]📊 Recommendation Statistics:[/bold cyan]")
        pred_ratings = [r["predicted_rating"] for r in top_10]
        console.print(f"  • Average predicted rating: {np.mean(pred_ratings):.2f}")
        console.print(f"  • Max predicted rating: {np.max(pred_ratings):.2f}")
        console.print(f"  • Min predicted rating: {np.min(pred_ratings):.2f}\n")


# ============================================================================
# STEP 5: MODEL EVALUATION METRICS
# ============================================================================


def calculate_evaluation_metrics(
    reconstructed,
    original_matrix,
    all_user_ids,
    rated_food_ids,
    user_vectors,
    target_user_id,
    sigma,
    U,
):
    """
    Calculate evaluation metrics:
    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Square Error)
    - NDCG (Normalized Discounted Cumulative Gain)
    - Explained Variance Ratio
    """

    console.rule("[bold cyan]📊 STEP 5: MODEL EVALUATION METRICS", style="cyan")

    # Get all actual ratings from the original matrix
    actual_ratings = []
    predicted_ratings = []

    console.print("\n[cyan]Calculating error metrics on known ratings...[/cyan]")

    for user_idx, user_id in enumerate(all_user_ids):
        user_full_vector = user_vectors[user_id]["vector"]

        for food_idx_in_matrix, food_idx_global in enumerate(rated_food_ids):
            actual = user_full_vector[food_idx_global]

            if actual > 0:  # Only evaluate on known ratings
                predicted = reconstructed[user_idx, food_idx_in_matrix]
                predicted = max(1.0, min(5.0, predicted))  # Clip to [1, 5]

                actual_ratings.append(actual)
                predicted_ratings.append(predicted)

    actual_ratings = np.array(actual_ratings)
    predicted_ratings = np.array(predicted_ratings)

    console.print(
        f"[green]✓[/green] Evaluating on {len(actual_ratings)} known ratings\n"
    )

    # ========================================================================
    # Display Sample Predictions (first 10 for visualization)
    # ========================================================================
    console.print("[bold cyan]📋 Sample Predictions (First 10):[/bold cyan]\n")

    sample_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")

    sample_table.add_column("No.", justify="center", style="cyan", width=6)
    sample_table.add_column("Actual Rating", justify="right", style="yellow", width=15)
    sample_table.add_column(
        "Predicted Rating", justify="right", style="green", width=18
    )
    sample_table.add_column("Error (|y-ŷ|)", justify="right", style="red", width=15)
    sample_table.add_column("Squared Error", justify="right", style="red", width=18)

    sample_size = min(10, len(actual_ratings))
    for i in range(len(actual_ratings)):
        error = abs(actual_ratings[i] - predicted_ratings[i])
        squared_error = (actual_ratings[i] - predicted_ratings[i]) ** 2

        sample_table.add_row(
            f"{i+1}",
            f"{actual_ratings[i]:.2f}",
            f"{predicted_ratings[i]:.4f}",
            f"{error:.4f}",
            f"{squared_error:.6f}",
        )

    console.print(sample_table)

    if len(actual_ratings) > 10:
        console.print(f"[dim]... and {len(actual_ratings) - 10} more ratings[/dim]\n")
    else:
        console.print()

    # ========================================================================
    # 1. MAE (Mean Absolute Error)
    # ========================================================================
    console.print(
        "[bold yellow]🔢 Calculating MAE (Mean Absolute Error):[/bold yellow]\n"
    )

    errors = np.abs(actual_ratings - predicted_ratings)
    mae = np.mean(errors)

    console.print(f"  Step 1: Calculate absolute errors")
    console.print(f"          |yᵢ - ŷᵢ| for each rating")
    console.print(f"          Errors: {errors[:5].tolist()} ... (showing first 5)")
    console.print(f"\n  Step 2: Sum all absolute errors")
    console.print(f"          Σ|yᵢ - ŷᵢ| = {np.sum(errors):.4f}")
    console.print(f"\n  Step 3: Divide by number of ratings")
    console.print(f"          MAE = Σ|yᵢ - ŷᵢ| / n")
    console.print(f"          MAE = {np.sum(errors):.4f} / {len(errors)}")
    console.print(f"          [bold green]MAE = {mae:.4f}[/bold green]\n")

    # ========================================================================
    # 2. RMSE (Root Mean Square Error)
    # ========================================================================
    console.print(
        "[bold yellow]🔢 Calculating RMSE (Root Mean Square Error):[/bold yellow]\n"
    )

    squared_errors = (actual_ratings - predicted_ratings) ** 2
    mse = np.mean(squared_errors)
    rmse = np.sqrt(mse)

    console.print(f"  Step 1: Calculate squared errors")
    console.print(f"          (yᵢ - ŷᵢ)² for each rating")
    console.print(
        f"          Squared errors: {squared_errors[:5].tolist()} ... (showing first 5)"
    )
    console.print(f"\n  Step 2: Sum all squared errors")
    console.print(f"          Σ(yᵢ - ŷᵢ)² = {np.sum(squared_errors):.6f}")
    console.print(f"\n  Step 3: Divide by number of ratings (MSE)")
    console.print(f"          MSE = Σ(yᵢ - ŷᵢ)² / n")
    console.print(
        f"          MSE = {np.sum(squared_errors):.6f} / {len(squared_errors)}"
    )
    console.print(f"          MSE = {mse:.6f}")
    console.print(f"\n  Step 4: Take square root")
    console.print(f"          RMSE = √MSE")
    console.print(f"          RMSE = √{mse:.6f}")
    console.print(f"          [bold green]RMSE = {rmse:.4f}[/bold green]\n")

    # ========================================================================
    # 3. Explained Variance Ratio
    # ========================================================================
    console.print(
        "[bold yellow]🔢 Calculating Explained Variance Ratio:[/bold yellow]\n"
    )

    # Variance explained by the singular values
    singular_values = np.diag(sigma)

    console.print(f"  Step 1: Get singular values from Σ matrix")
    console.print(f"          σ = {singular_values.tolist()}")

    console.print(f"\n  Step 2: Square each singular value")
    squared_sv = singular_values**2
    console.print(f"          σ² = {squared_sv.tolist()}")

    console.print(f"\n  Step 3: Calculate total variance")
    total_variance = np.sum(squared_sv)
    console.print(f"          Total variance = Σ(σᵢ²)")
    console.print(f"          Total variance = {total_variance:.6f}")

    console.print(f"\n  Step 4: Calculate variance explained by each factor")
    explained_variance = squared_sv / total_variance
    console.print(f"          Variance ratios = σᵢ² / Total")
    for i, var in enumerate(explained_variance, 1):
        console.print(
            f"          Factor {i}: {squared_sv[i-1]:.6f} / {total_variance:.6f} = {var:.6f} ({var*100:.2f}%)"
        )

    console.print(f"\n  Step 5: Calculate cumulative variance")
    cumulative_variance = np.cumsum(explained_variance)
    for i, cum_var in enumerate(cumulative_variance, 1):
        console.print(f"          Up to Factor {i}: {cum_var:.6f} ({cum_var*100:.2f}%)")

    explained_variance_ratio = (
        cumulative_variance[-1] if len(cumulative_variance) > 0 else 0.0
    )
    console.print(
        f"\n  [bold green]Explained Variance Ratio = {explained_variance_ratio:.4f} ({explained_variance_ratio*100:.2f}%)[/bold green]\n"
    )

    # ========================================================================
    # 4. NDCG (Normalized Discounted Cumulative Gain)
    # ========================================================================
    console.print(
        "[bold yellow]🔢 Calculating NDCG (Normalized Discounted Cumulative Gain):[/bold yellow]\n"
    )

    # Calculate NDCG for target user's recommendations
    target_idx = all_user_ids.index(target_user_id)
    target_predictions = reconstructed[target_idx, :]
    target_full_vector = user_vectors[target_user_id]["vector"]

    # Get items user has rated (for testing)
    user_rated_items = []
    for j, food_idx in enumerate(rated_food_ids):
        actual = target_full_vector[food_idx]
        if actual > 0:
            predicted = max(1.0, min(5.0, target_predictions[j]))
            user_rated_items.append({"actual": actual, "predicted": predicted})

    # Calculate DCG and IDCG
    if user_rated_items:
        console.print(f"  Target user has {len(user_rated_items)} rated items\n")

        # Sort by predicted rating (descending)
        sorted_items = sorted(
            user_rated_items, key=lambda x: x["predicted"], reverse=True
        )

        console.print(f"  Step 1: Sort items by predicted rating (descending)")
        ndcg_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        ndcg_table.add_column("Rank (i)", justify="center", style="cyan", width=10)
        ndcg_table.add_column("Predicted", justify="right", style="green", width=12)
        ndcg_table.add_column("Actual (rel)", justify="right", style="yellow", width=14)
        ndcg_table.add_column("2^rel - 1", justify="right", style="blue", width=12)
        ndcg_table.add_column("log₂(i+1)", justify="right", style="magenta", width=12)
        ndcg_table.add_column(
            "DCG contribution", justify="right", style="white", width=18
        )

        # DCG: Discounted Cumulative Gain
        dcg = 0.0
        dcg_contributions = []
        for i, item in enumerate(sorted_items, 1):
            relevance = item["actual"]
            gain = 2**relevance - 1
            discount = np.log2(i + 1)
            contribution = gain / discount
            dcg += contribution
            dcg_contributions.append(contribution)

            ndcg_table.add_row(
                f"{i}",
                f"{item['predicted']:.2f}",
                f"{relevance:.2f}",
                f"{gain:.2f}",
                f"{discount:.4f}",
                f"{contribution:.4f}",
            )

        console.print(ndcg_table)
        console.print(f"\n  [bold]DCG = Σ[(2^relᵢ - 1) / log₂(i+1)][/bold]")
        console.print(
            f"  DCG = {' + '.join([f'{c:.4f}' for c in dcg_contributions[:5]])} ..."
        )
        console.print(f"  [bold green]DCG = {dcg:.4f}[/bold green]\n")

        # IDCG: Ideal DCG (sort by actual rating)
        console.print(f"  Step 2: Sort items by actual rating (ideal ranking)")
        ideal_sorted = sorted(user_rated_items, key=lambda x: x["actual"], reverse=True)

        idcg_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        idcg_table.add_column("Rank (i)", justify="center", style="cyan", width=10)
        idcg_table.add_column("Actual (rel)", justify="right", style="yellow", width=14)
        idcg_table.add_column("2^rel - 1", justify="right", style="blue", width=12)
        idcg_table.add_column("log₂(i+1)", justify="right", style="magenta", width=12)
        idcg_table.add_column(
            "IDCG contribution", justify="right", style="white", width=18
        )

        idcg = 0.0
        idcg_contributions = []
        for i, item in enumerate(ideal_sorted, 1):
            relevance = item["actual"]
            gain = 2**relevance - 1
            discount = np.log2(i + 1)
            contribution = gain / discount
            idcg += contribution
            idcg_contributions.append(contribution)

            idcg_table.add_row(
                f"{i}",
                f"{relevance:.2f}",
                f"{gain:.2f}",
                f"{discount:.4f}",
                f"{contribution:.4f}",
            )

        console.print(idcg_table)
        console.print(
            f"\n  [bold]IDCG = Σ[(2^relᵢ - 1) / log₂(i+1)] (ideal ranking)[/bold]"
        )
        console.print(
            f"  IDCG = {' + '.join([f'{c:.4f}' for c in idcg_contributions[:5]])} ..."
        )
        console.print(f"  [bold green]IDCG = {idcg:.4f}[/bold green]\n")

        # NDCG
        console.print(f"  Step 3: Calculate NDCG")
        console.print(f"          NDCG = DCG / IDCG")
        console.print(f"          NDCG = {dcg:.4f} / {idcg:.4f}")
        ndcg = dcg / idcg if idcg > 0 else 0.0
        console.print(f"          [bold green]NDCG = {ndcg:.4f}[/bold green]\n")
    else:
        ndcg = 0.0
        console.print(f"  [yellow]No rated items found for target user[/yellow]\n")

    # ========================================================================
    # Display Final Results Summary (at the end)
    # ========================================================================

    display_final_evaluation_summary(
        mae,
        rmse,
        ndcg,
        explained_variance_ratio,
        singular_values,
        explained_variance,
        cumulative_variance,
        actual_ratings,
        predicted_ratings,
    )

    return {
        "mae": mae,
        "rmse": rmse,
        "ndcg": ndcg,
        "explained_variance_ratio": explained_variance_ratio,
        "n_ratings": len(actual_ratings),
    }


def display_final_evaluation_summary(
    mae,
    rmse,
    ndcg,
    explained_variance_ratio,
    singular_values,
    explained_variance,
    cumulative_variance,
    actual_ratings,
    predicted_ratings,
):
    """
    Display final evaluation results summary at the end
    """

    console.rule("[bold green]📊 FINAL EVALUATION RESULTS", style="green")
    console.print()

    # Create metrics table
    metrics_table = Table(
        title="🎯 Model Evaluation Metrics",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold magenta",
    )

    metrics_table.add_column("Metric", justify="left", style="cyan", width=30)
    metrics_table.add_column("Value", justify="right", style="green", width=15)
    metrics_table.add_column("Interpretation", justify="left", style="yellow", width=45)

    # MAE
    mae_quality = (
        "Excellent ✅"
        if mae < 0.5
        else (
            "Good ✓"
            if mae < 0.75
            else "Fair ⚠️" if mae < 1.0 else "Needs Improvement ❌"
        )
    )
    metrics_table.add_row(
        "MAE (Mean Absolute Error)",
        f"{mae:.4f}",
        f"{mae_quality} - Avg error magnitude",
    )

    # RMSE
    rmse_quality = (
        "Excellent ✅"
        if rmse < 0.6
        else (
            "Good ✓"
            if rmse < 0.9
            else "Fair ⚠️" if rmse < 1.2 else "Needs Improvement ❌"
        )
    )
    metrics_table.add_row(
        "RMSE (Root Mean Square Error)",
        f"{rmse:.4f}",
        f"{rmse_quality} - Penalizes large errors",
    )

    # NDCG
    ndcg_quality = (
        "Excellent ✅"
        if ndcg > 0.9
        else (
            "Good ✓"
            if ndcg > 0.8
            else "Fair ⚠️" if ndcg > 0.7 else "Needs Improvement ❌"
        )
    )
    metrics_table.add_row(
        "NDCG (Normalized DCG)",
        f"{ndcg:.4f}",
        f"{ndcg_quality} - Ranking quality (0-1)",
    )

    # Explained Variance
    var_quality = (
        "Excellent ✅"
        if explained_variance_ratio > 0.95
        else (
            "Good ✓"
            if explained_variance_ratio > 0.85
            else "Fair ⚠️" if explained_variance_ratio > 0.75 else "Needs Improvement ❌"
        )
    )
    metrics_table.add_row(
        "Explained Variance Ratio",
        f"{explained_variance_ratio:.4f}",
        f"{var_quality} - Variance captured by model",
    )

    console.print(metrics_table)

    # Detailed Explanation
    console.print("\n[bold cyan]📖 Metric Explanations:[/bold cyan]\n")

    explanation_panel = Panel(
        f"""[yellow]MAE (Mean Absolute Error):[/yellow]
  • Formula: MAE = (1/n) × Σ|yᵢ - ŷᵢ|
  • Value: [bold green]{mae:.4f}[/bold green]
  • Interpretation: Average difference between actual and predicted ratings
  • Lower is better (0 = perfect predictions)
  • Current result: {mae_quality}

[yellow]RMSE (Root Mean Square Error):[/yellow]
  • Formula: RMSE = √[(1/n) × Σ(yᵢ - ŷᵢ)²]
  • Value: [bold green]{rmse:.4f}[/bold green]
  • Interpretation: Emphasizes larger errors more than MAE
  • Lower is better (0 = perfect predictions)
  • Current result: {rmse_quality}

[yellow]NDCG (Normalized Discounted Cumulative Gain):[/yellow]
  • Formula: NDCG = DCG / IDCG
  • Value: [bold green]{ndcg:.4f}[/bold green]
  • Interpretation: Measures ranking quality (how well we rank items)
  • Range: 0 (worst) to 1 (perfect ranking)
  • Current result: {ndcg_quality}

[yellow]Explained Variance Ratio:[/yellow]
  • Formula: Σ(σᵢ²) / Σ(all σ²)
  • Value: [bold green]{explained_variance_ratio:.4f}[/bold green]
  • Interpretation: Proportion of variance captured by latent factors
  • Range: 0 (captures nothing) to 1 (captures everything)
  • Current result: {var_quality}""",
        title="📊 Detailed Metric Interpretation",
        border_style="blue",
        padding=(1, 2),
    )

    console.print(explanation_panel)

    # Singular Values Breakdown
    console.print("\n[bold cyan]🔢 Singular Values Breakdown:[/bold cyan]\n")

    sv_table = Table(box=box.ROUNDED, show_header=True, header_style="bold yellow")

    sv_table.add_column("Factor", justify="center", style="cyan", width=10)
    sv_table.add_column("Singular Value (σ)", justify="right", style="green", width=20)
    sv_table.add_column("Variance %", justify="right", style="blue", width=15)
    sv_table.add_column("Cumulative %", justify="right", style="magenta", width=15)
    sv_table.add_column("Visual", justify="left", style="cyan", width=30)

    for i, (sv, var_pct, cum_var) in enumerate(
        zip(singular_values, explained_variance, cumulative_variance), 1
    ):
        bar_length = int(var_pct * 30)
        visual_bar = "█" * bar_length + "░" * (30 - bar_length)

        sv_table.add_row(
            f"σ{i}",
            f"{sv:.6f}",
            f"{var_pct*100:.2f}%",
            f"{cum_var*100:.2f}%",
            visual_bar,
        )

    console.print(sv_table)

    # Summary statistics
    console.print("\n[bold cyan]📈 Summary Statistics:[/bold cyan]")
    console.print(
        f"  • Total known ratings evaluated: [bold]{len(actual_ratings)}[/bold]"
    )
    console.print(
        f"  • Actual rating range: [bold]{actual_ratings.min():.1f} - {actual_ratings.max():.1f}[/bold]"
    )
    console.print(
        f"  • Predicted rating range: [bold]{predicted_ratings.min():.2f} - {predicted_ratings.max():.2f}[/bold]"
    )
    console.print(f"  • Number of latent factors: [bold]{len(singular_values)}[/bold]")
    console.print(
        f"  • Variance explained by top factor: [bold]{explained_variance[0]*100:.2f}%[/bold]\n"
    )


# ============================================================================
# MAIN FUNCTION
# ============================================================================


def main():
    """Main execution function - Detailed SVD Calculation"""

    console.print("\n[bold white on blue]" + " " * 100 + "[/bold white on blue]")
    console.print(
        "[bold white on blue]  DETAILED SVD CALCULATION - RECOMMENDATION SYSTEM"
        + " " * 47
        + "[/bold white on blue]"
    )
    console.print(
        "[bold white on blue]  Manual SVD Decomposition with Step-by-Step Analysis"
        + " " * 42
        + "[/bold white on blue]"
    )
    console.print("[bold white on blue]" + " " * 100 + "[/bold white on blue]")

    try:
        # Initialize Flask app context
        from app import create_app

        app = create_app()

        with app.app_context():
            # Find user "adza" in database
            target_username = "adza"

            console.print(f"\n[cyan]🔍 Searching for user: {target_username}...[/cyan]")

            user = User.query.filter_by(username=target_username).first()

            if not user:
                console.print(
                    f"\n[bold red]❌ User '{target_username}' not found in database![/bold red]"
                )
                console.print("\n[yellow]Available users (first 10):[/yellow]")
                users = User.query.limit(10).all()
                for idx, u in enumerate(users, 1):
                    console.print(f"  {idx}. {u.name} (@{u.username})")
                return

            console.print(
                f"[green]✓[/green] Found user: [bold]{user.name}[/bold] (@{user.username})\n"
            )

            # STEP 1: Show similar users only (similarity > 0)
            similar_users, target_vector, user_vectors = display_20_users_similarity(
                user.id
            )

            if not similar_users:
                console.print(
                    "[yellow]⚠️  Cannot proceed without similar users[/yellow]"
                )
                return

            # STEP 2: Show detailed similarity calculation
            display_detailed_similarity_calculation(similar_users, user.id)

            # STEP 2.5: Display user-item rating matrix
            display_user_rating_matrix(similar_users, user.id, user_vectors)

            # STEP 3: Perform SVD and show decomposition
            (
                reconstructed,
                all_user_ids,
                rated_food_ids,
                user_vectors,
                sigma,
                U,
                original_matrix,
            ) = perform_svd_on_selected_users(
                similar_users, user.id, target_vector, user_vectors
            )

            # STEP 4: Generate and display recommendations
            display_final_recommendations(
                reconstructed, all_user_ids, rated_food_ids, user_vectors, user.id
            )

            # STEP 5: Calculate and display evaluation metrics
            metrics = calculate_evaluation_metrics(
                reconstructed,
                original_matrix,
                all_user_ids,
                rated_food_ids,
                user_vectors,
                user.id,
                sigma,
                U,
            )

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/red]")
        return

    console.print("\n[bold white on green]" + " " * 100 + "[/bold white on green]")
    console.print(
        "[bold white on green]  ✅ DETAILED CALCULATION COMPLETE"
        + " " * 64
        + "[/bold white on green]"
    )
    console.print("[bold white on green]" + " " * 100 + "[/bold white on green]\n")


if __name__ == "__main__":
    main()
