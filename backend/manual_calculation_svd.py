"""
Manual Calculation - Production Recommendation System with Rich Display
========================================================================
Script ini menggunakan sistem rekomendasi production yang sudah ada,
namun dengan tampilan Rich Console yang indah untuk memudahkan testing manual.

Fitur:
1. Menggunakan production recommendation service (SVD Collaborative Filtering)
2. Menampilkan rating history user dengan tabel Rich
3. Menampilkan top 10 rekomendasi dengan predicted rating
4. Fokus pada user "adza" untuk pengujian

Data diambil langsung dari database MySQL.
"""

import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.rule import Rule

# Import production recommendation system
from app.recommendation.service import RecommendationService
from app.recommendation.recommender import Recommendations
from app.extensions import db
from app.modules.user.models import User
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating

# Rich Console for beautiful output
console = Console()

import numpy as np
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from scipy.sparse.linalg import svds
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.rule import Rule

# Load environment variables
load_dotenv()

# Initialize Rich Console
console = Console()

# ============================================================================
# DATABASE CONNECTION
# ============================================================================


def get_database_connection():
    """Create database connection"""
    database_uri = os.getenv(
        "DATABASE_URI", "mysql://root:zett@localhost/food_recommendation"
    )
    engine = create_engine(database_uri)
    return engine


# ============================================================================
# DATA LOADING FROM DATABASE
# ============================================================================


def load_data_from_db(limit_users=None, limit_foods=None):
    """Load users, foods, and ratings from database"""
    engine = get_database_connection()

    console.rule("[bold cyan]LOADING DATA FROM DATABASE", style="cyan")

    # Load Users
    user_query = """
        SELECT id, name, username, email
        FROM users
        WHERE role = 'user'
    """
    if limit_users:
        user_query += f" LIMIT {limit_users}"

    with engine.connect() as conn:
        users_result = conn.execute(text(user_query))
        users = [dict(row._mapping) for row in users_result]

    console.print(f"\n[green]✓[/green] Loaded [bold]{len(users)}[/bold] users")

    # Load Foods
    food_query = """
        SELECT f.id, f.name, f.price, r.name as restaurant_name
        FROM foods f
        LEFT JOIN restaurants r ON f.restaurant_id = r.id
    """
    if limit_foods:
        food_query += f" LIMIT {limit_foods}"

    with engine.connect() as conn:
        foods_result = conn.execute(text(food_query))
        foods = [dict(row._mapping) for row in foods_result]

    console.print(f"[green]✓[/green] Loaded [bold]{len(foods)}[/bold] foods")

    # Load Ratings
    rating_query = """
        SELECT user_id, food_id, rating, created_at
        FROM food_ratings
        ORDER BY created_at DESC
    """

    with engine.connect() as conn:
        ratings_result = conn.execute(text(rating_query))
        ratings = [dict(row._mapping) for row in ratings_result]

    console.print(f"[green]✓[/green] Loaded [bold]{len(ratings)}[/bold] ratings")
    console.print(f"[green]✓[/green] Created index mappings")

    # Create mappings
    user_id_to_idx = {user["id"]: idx for idx, user in enumerate(users)}
    food_id_to_idx = {food["id"]: idx for idx, food in enumerate(foods)}

    idx_to_user_id = {idx: user["id"] for idx, user in enumerate(users)}
    idx_to_food_id = {idx: food["id"] for idx, food in enumerate(foods)}

    return {
        "users": users,
        "foods": foods,
        "ratings": ratings,
        "user_id_to_idx": user_id_to_idx,
        "food_id_to_idx": food_id_to_idx,
        "idx_to_user_id": idx_to_user_id,
        "idx_to_food_id": idx_to_food_id,
    }


# ============================================================================
# STEP 1: USER-ITEM MATRIX
# ============================================================================


def create_rating_matrix(data):
    """Create user-item rating matrix from database data"""
    n_users = len(data["users"])
    n_foods = len(data["foods"])

    # Initialize matrix
    rating_matrix = np.zeros((n_users, n_foods))

    # Fill matrix with ratings
    for rating in data["ratings"]:
        user_id = rating["user_id"]
        food_id = rating["food_id"]

        if user_id in data["user_id_to_idx"] and food_id in data["food_id_to_idx"]:
            user_idx = data["user_id_to_idx"][user_id]
            food_idx = data["food_id_to_idx"][food_id]
            rating_matrix[user_idx, food_idx] = rating["rating"]

    return rating_matrix


def display_rating_matrix(rating_matrix, data, max_display=10):
    """Display rating matrix in table format"""
    console.rule("[bold cyan]STEP 1: USER-ITEM RATING MATRIX", style="cyan")

    n_users, n_foods = rating_matrix.shape
    console.print(
        f"\n[yellow]Matrix Shape:[/yellow] [bold]{n_users}[/bold] users × [bold]{n_foods}[/bold] foods"
    )

    # Calculate statistics
    total_ratings = np.count_nonzero(rating_matrix)
    sparsity = 1 - (total_ratings / (n_users * n_foods))

    console.print(f"[yellow]Total Ratings:[/yellow] [bold]{total_ratings}[/bold]")
    console.print(f"[yellow]Sparsity:[/yellow] [bold]{sparsity:.2%}[/bold]")
    console.print(
        f"[yellow]Average Rating:[/yellow] [bold]{np.mean(rating_matrix[rating_matrix > 0]):.2f}[/bold]"
    )

    # Display sample of matrix
    console.print(
        f"\n[bold]Sample Matrix[/bold] (first {min(max_display, n_users)} users × first {min(max_display, n_foods)} foods):"
    )

    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("User", style="cyan", no_wrap=True)

    for j in range(min(max_display, n_foods)):
        table.add_column(f"F{j+1}", justify="center", style="white")

    for i in range(min(max_display, n_users)):
        user_name = data["users"][i]["name"][:15]
        row_data = [f"U{i+1}: {user_name}"]
        for j in range(min(max_display, n_foods)):
            val = rating_matrix[i, j]
            if val > 0:
                row_data.append(f"[green]{val:.1f}[/green]")
            else:
                row_data.append("[dim]-[/dim]")
        table.add_row(*row_data)

    console.print(table)

    # User statistics
    console.print("\n[bold]User Statistics:[/bold]")
    stats_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
    stats_table.add_column("ID", style="cyan")
    stats_table.add_column("Name", style="yellow")
    stats_table.add_column("Rated Items", justify="center", style="green")
    stats_table.add_column("Avg Rating", justify="center", style="blue")

    for i in range(min(5, n_users)):
        rated_count = np.count_nonzero(rating_matrix[i, :])
        avg_rating = (
            np.mean(rating_matrix[i, rating_matrix[i, :] > 0]) if rated_count > 0 else 0
        )
        stats_table.add_row(
            f"U{i+1}",
            data["users"][i]["name"][:20],
            str(rated_count),
            f"{avg_rating:.2f}",
        )

    console.print(stats_table)


# ============================================================================
# STEP 2: COSINE SIMILARITY
# ============================================================================


def normalize_ratings(matrix):
    """Normalize ratings with mean centering"""
    n_users = matrix.shape[0]
    user_means = np.zeros(n_users)
    normalized = matrix.copy()

    for i in range(n_users):
        rated_items = matrix[i, :] > 0
        if np.sum(rated_items) > 0:
            user_means[i] = np.mean(matrix[i, rated_items])
            normalized[i, rated_items] -= user_means[i]

    return normalized, user_means


def calculate_user_similarity(normalized_matrix, rating_matrix):
    """Calculate cosine similarity between users"""
    n_users = normalized_matrix.shape[0]
    similarity_matrix = np.zeros((n_users, n_users))

    for i in range(n_users):
        for j in range(n_users):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                # Common items
                common = (rating_matrix[i, :] > 0) & (rating_matrix[j, :] > 0)

                if np.sum(common) > 0:
                    vec_i = normalized_matrix[i, common]
                    vec_j = normalized_matrix[j, common]

                    dot_prod = np.sum(vec_i * vec_j)
                    norm_i = np.sqrt(np.sum(vec_i**2))
                    norm_j = np.sqrt(np.sum(vec_j**2))

                    if norm_i > 0 and norm_j > 0:
                        similarity_matrix[i, j] = dot_prod / (norm_i * norm_j)

    return similarity_matrix


def display_user_similarity(similarity_matrix, data, max_display=10):
    """Display user similarity matrix"""
    console.rule(
        "[bold cyan]STEP 2: USER SIMILARITY MATRIX (Cosine Similarity)", style="cyan"
    )

    n_users = similarity_matrix.shape[0]
    console.print(
        f"\n[yellow]Similarity Matrix Shape:[/yellow] [bold]{n_users} × {n_users}[/bold]"
    )

    # Display sample
    console.print(
        f"\n[bold]Sample Similarity Matrix[/bold] (first {min(max_display, n_users)} users):"
    )

    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("User", style="cyan", no_wrap=True)

    for j in range(min(max_display, n_users)):
        table.add_column(f"U{j+1}", justify="center", style="white")

    for i in range(min(max_display, n_users)):
        user_name = data["users"][i]["name"][:15]
        row_data = [f"U{i+1}: {user_name}"]
        for j in range(min(max_display, n_users)):
            sim = similarity_matrix[i, j]
            if i == j:
                row_data.append(f"[bold green]{sim:.3f}[/bold green]")
            elif sim > 0.5:
                row_data.append(f"[green]{sim:.3f}[/green]")
            elif sim > 0:
                row_data.append(f"[yellow]{sim:.3f}[/yellow]")
            elif sim < 0:
                row_data.append(f"[red]{sim:.3f}[/red]")
            else:
                row_data.append(f"[dim]{sim:.3f}[/dim]")
        table.add_row(*row_data)

    console.print(table)

    # Find top similar pairs
    console.print("\n[bold]Top 5 Similar User Pairs:[/bold]")
    similar_pairs = []
    for i in range(n_users):
        for j in range(i + 1, n_users):
            if similarity_matrix[i, j] > 0.01:
                similar_pairs.append((i, j, similarity_matrix[i, j]))

    similar_pairs.sort(key=lambda x: x[2], reverse=True)

    if similar_pairs:
        pair_table = Table(
            show_header=True, header_style="bold magenta", box=box.SIMPLE
        )
        pair_table.add_column("User 1", style="cyan")
        pair_table.add_column("User 2", style="cyan")
        pair_table.add_column("Similarity", justify="center", style="green")

        for i, j, sim in similar_pairs[:5]:
            pair_table.add_row(
                data["users"][i]["name"][:20],
                data["users"][j]["name"][:20],
                f"{sim:.4f}",
            )

        console.print(pair_table)
    else:
        console.print("[yellow]No similar users found with similarity > 0.01[/yellow]")


# ============================================================================
# STEP 3: COLLABORATIVE FILTERING with SVD
# ============================================================================


def collaborative_filtering_svd(rating_matrix, n_factors=20):
    """
    Apply SVD (Singular Value Decomposition) for collaborative filtering

    SVD decomposes matrix R into:
    R ≈ U × Σ × V^T

    Where:
    - U: User feature matrix (n_users × n_factors)
    - Σ: Singular values (diagonal matrix)
    - V^T: Item feature matrix (n_factors × n_items)
    """

    # Replace zeros with user mean for better SVD
    matrix_for_svd = rating_matrix.copy()
    user_means = np.zeros(rating_matrix.shape[0])

    for i in range(rating_matrix.shape[0]):
        rated = rating_matrix[i, :] > 0
        if np.sum(rated) > 0:
            user_means[i] = np.mean(rating_matrix[i, rated])
            # Fill zeros with user mean
            matrix_for_svd[i, ~rated] = user_means[i]

    # Apply SVD
    # n_factors should be less than min(n_users, n_items)
    k = min(n_factors, min(rating_matrix.shape) - 1)

    console.rule("[bold cyan]STEP 3: COLLABORATIVE FILTERING with SVD", style="cyan")
    console.print(
        f"\n[yellow]Applying SVD with[/yellow] [bold]{k}[/bold] [yellow]latent factors...[/yellow]"
    )

    U, sigma, Vt = svds(matrix_for_svd, k=k)

    # Convert sigma to diagonal matrix
    sigma = np.diag(sigma)

    # Reconstruct the matrix
    predicted_ratings = np.dot(np.dot(U, sigma), Vt)

    console.print(f"[green]✓[/green] SVD decomposition completed")
    console.print(f"  [cyan]•[/cyan] U (User features): [bold]{U.shape}[/bold]")
    console.print(f"  [cyan]•[/cyan] Σ (Singular values): [bold]{sigma.shape}[/bold]")
    console.print(f"  [cyan]•[/cyan] V^T (Item features): [bold]{Vt.shape}[/bold]")

    # Calculate reconstruction error
    mask = rating_matrix > 0
    original_ratings = rating_matrix[mask]
    predicted_on_known = predicted_ratings[mask]
    rmse = np.sqrt(np.mean((original_ratings - predicted_on_known) ** 2))

    console.print(
        f"\n[yellow]Reconstruction RMSE on known ratings:[/yellow] [bold]{rmse:.4f}[/bold]"
    )

    return predicted_ratings, U, sigma, Vt


# ============================================================================
# STEP 4: FINAL RANKING & RECOMMENDATIONS
# ============================================================================


def get_recommendations_from_production(user_id, top_n=10):
    """Get recommendations using production recommendation service with calculation details."""
    console.print(
        "\n[bold cyan]🎯 Getting Recommendations from Production System...[/bold cyan]"
    )

    try:
        # Initialize production recommendation service
        from app.recommendation.recommender import Recommendations
        from app.recommendation.local_data import LocalDataProcessor

        recommendation_service = RecommendationService()

        # Also initialize recommender directly to get calculation details
        recommender = Recommendations()

        # Load data first
        if not recommender._load_and_validate_data():
            console.print("[bold red]❌ Failed to load data[/bold red]")
            return [], None, None

        # Get recommendations with scores
        # Note: service returns tuple (response_dict, status_code)
        response, status_code = recommendation_service.get_recommendations(
            user_id=user_id, top_n=top_n, include_scores=True
        )

        if status_code != 200:
            console.print(
                f"[bold red]❌ Error: {response.get('message', 'Unknown error')}[/bold red]"
            )
            return [], None, None

        data = response.get("data", {})
        recommendations = data.get("recommendations", [])

        if not recommendations:
            console.print(
                f"[bold red]❌ No recommendations found for user {user_id}![/bold red]"
            )
            return [], None, None

        console.print(
            f"[green]✓ Got {len(recommendations)} recommendations from production system[/green]"
        )

        # Get calculation details (similarity and SVD info)
        # Note: SVD model is now fitted after recommendation process
        calculation_details = get_calculation_details(user_id, recommendation_service.recommender)

        return recommendations, calculation_details.get('similarity_matrix'), calculation_details.get('svd_info')

    except Exception as e:
        console.print(
            f"[bold red]❌ Error getting recommendations: {str(e)}[/bold red]"
        )
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/red]")
        return [], None, None


def get_calculation_details(user_id, recommender):
    """Extract calculation details from recommender for display."""
    details = {
        'similarity_matrix': None,
        'svd_info': None
    }

    try:
        from app.recommendation.similarity import get_similar_users

        # Get similar users with scores
        similar_users = get_similar_users(
            recommender.data_processor.ratings_df,
            user_id,
            top_k=10,
            similarity_threshold=0.1,
            method="cosine"
        )

        details['similarity_matrix'] = similar_users

        # Get SVD info from last trained model
        if recommender.svd_model and recommender.svd_model.is_fitted:
            svd_info = recommender.svd_model.get_model_info()
            details['svd_info'] = svd_info

    except Exception as e:
        console.print(f"[yellow]⚠️ Could not extract calculation details: {str(e)}[/yellow]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")

    return details


def display_cosine_similarity_table(similarity_matrix, target_user_id):
    """Display cosine similarity calculation results in a table."""
    if not similarity_matrix or len(similarity_matrix) == 0:
        console.print("[yellow]⚠️ No similarity data available[/yellow]")
        return

    console.rule("[bold cyan]📐 COSINE SIMILARITY RESULTS", style="cyan")

    # Create similarity table
    sim_table = Table(
        title=f"Top Similar Users for {target_user_id[:8]}...",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )

    sim_table.add_column("Rank", style="cyan", justify="center", width=6)
    sim_table.add_column("User ID", style="yellow", width=30)
    sim_table.add_column("Similarity Score", style="green", justify="right", width=18)
    sim_table.add_column("Similarity %", style="blue", justify="right", width=15)
    sim_table.add_column("Visual", style="cyan", width=30)

    for idx, (user_id, score) in enumerate(similarity_matrix[:10], 1):
        percentage = score * 100
        # Create visual bar
        bar_length = int(score * 20)
        visual_bar = "█" * bar_length + "░" * (20 - bar_length)

        sim_table.add_row(
            f"#{idx}",
            f"{user_id[:30]}",
            f"{score:.4f}",
            f"{percentage:.2f}%",
            visual_bar
        )

    console.print(sim_table)

    # Summary statistics
    scores = [score for _, score in similarity_matrix[:10]]
    if scores:
        avg_similarity = sum(scores) / len(scores)
        max_similarity = max(scores)
        min_similarity = min(scores)

        stats_text = f"""
[bold]Cosine Similarity Statistics:[/bold]
• Total Similar Users Found: [cyan]{len(similarity_matrix)}[/cyan]
• Average Similarity (Top 10): [green]{avg_similarity:.4f}[/green] ({avg_similarity*100:.2f}%)
• Highest Similarity: [green]{max_similarity:.4f}[/green] ({max_similarity*100:.2f}%)
• Lowest Similarity (Top 10): [yellow]{min_similarity:.4f}[/yellow] ({min_similarity*100:.2f}%)

[dim]Note: Similarity ranges from 0 (no similarity) to 1 (identical patterns)[/dim]
        """

        console.print(Panel(stats_text, title="📊 Similarity Statistics", border_style="blue"))

    console.print()


def display_svd_results(svd_info):
    """Display SVD decomposition results."""
    if not svd_info:
        console.print("[yellow]⚠️ No SVD information available[/yellow]")
        return

    console.rule("[bold cyan]🔢 SVD DECOMPOSITION RESULTS", style="cyan")

    # SVD Model Info Table
    svd_table = Table(
        title="SVD Model Information",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )

    svd_table.add_column("Parameter", style="cyan", width=30)
    svd_table.add_column("Value", style="yellow", justify="right", width=20)
    svd_table.add_column("Description", style="dim", width=40)

    # Extract info
    n_factors = svd_info.get("n_factors", 0)
    n_users = svd_info.get("n_users", 0)
    n_items = svd_info.get("n_items", 0)
    sparsity = svd_info.get("sparsity", 0)
    explained_variance = svd_info.get("explained_variance_ratio", 0)

    svd_table.add_row(
        "Number of Factors (k)",
        str(n_factors),
        "Latent factors dalam dekomposisi"
    )
    svd_table.add_row(
        "Users in Matrix",
        str(n_users),
        "Jumlah users dalam local dataset"
    )
    svd_table.add_row(
        "Items in Matrix",
        str(n_items),
        "Jumlah items dalam local dataset"
    )
    svd_table.add_row(
        "Matrix Sparsity",
        f"{sparsity:.2%}",
        "Persentase cell kosong"
    )
    svd_table.add_row(
        "Explained Variance",
        f"{explained_variance:.4f}",
        "Variance yang dijelaskan model"
    )
    svd_table.add_row(
        "Model Quality",
        "Excellent ✅" if explained_variance > 0.95 else "Good ✓" if explained_variance > 0.80 else "Fair ⚠️",
        "Kualitas fit model"
    )

    console.print(svd_table)

    # Singular Values Info (if available)
    singular_values = svd_info.get("singular_values", [])
    if singular_values and len(singular_values) > 0:
        console.print("\n[bold]📊 Singular Values (Σ):[/bold]")

        sv_table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold yellow"
        )
        sv_table.add_column("Factor", style="cyan", justify="center", width=10)
        sv_table.add_column("Singular Value", style="green", justify="right", width=20)
        sv_table.add_column("Variance %", style="blue", justify="right", width=15)
        sv_table.add_column("Cumulative %", style="magenta", justify="right", width=15)
        sv_table.add_column("Visual", style="cyan", width=30)

        total_variance = sum(singular_values)
        cumulative = 0

        for i, sv in enumerate(singular_values, 1):
            variance_pct = (sv / total_variance * 100) if total_variance > 0 else 0
            cumulative += variance_pct

            # Visual bar
            bar_length = int(variance_pct / 100 * 20)
            visual_bar = "█" * bar_length + "░" * (20 - bar_length)

            sv_table.add_row(
                f"Factor {i}",
                f"{sv:.4f}",
                f"{variance_pct:.2f}%",
                f"{cumulative:.2f}%",
                visual_bar
            )

        console.print(sv_table)

    # SVD Formula Reminder
    formula_text = """
[bold cyan]SVD Decomposition Formula:[/bold cyan]
R = U × Σ × V^T

Where:
• [cyan]U[/cyan]: User-Feature matrix ([green]{users} × {factors}[/green])
• [cyan]Σ[/cyan]: Diagonal matrix of singular values ([green]{factors} × {factors}[/green])
• [cyan]V^T[/cyan]: Feature-Item matrix ([green]{factors} × {items}[/green])
• [cyan]R[/cyan]: Reconstructed rating matrix ([green]{users} × {items}[/green])

[dim]Model captures {variance:.1%} of the variance in {factors} latent factors[/dim]
    """.format(
        users=n_users,
        items=n_items,
        factors=n_factors,
        variance=explained_variance
    )

    console.print(Panel(formula_text, title="📐 SVD Formula", border_style="green"))
    console.print()


def display_calculation_summary():
    """Display summary of matrix, cosine similarity, and SVD calculations"""
    console.rule("[bold cyan]📊 CALCULATION SUMMARY", style="cyan")

    try:
        # Get database statistics
        from app.modules.rating.models import FoodRating
        from app.modules.food.models import Food
        from app.modules.user.models import User

        total_users = User.query.count()
        total_foods = Food.query.count()
        total_ratings = FoodRating.query.count()

        # Calculate sparsity
        total_possible = total_users * total_foods
        sparsity = 1 - (total_ratings / total_possible) if total_possible > 0 else 0

        # Create summary table
        summary_table = Table(
            title="📐 Data Matrix Overview",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )

        summary_table.add_column("Metric", style="cyan", width=30)
        summary_table.add_column("Value", style="yellow", justify="right", width=20)
        summary_table.add_column("Description", style="dim", width=40)

        summary_table.add_row(
            "Total Users",
            str(total_users),
            "Jumlah user dalam sistem"
        )
        summary_table.add_row(
            "Total Foods",
            str(total_foods),
            "Jumlah makanan dalam sistem"
        )
        summary_table.add_row(
            "Total Ratings",
            str(total_ratings),
            "Jumlah rating yang diberikan"
        )
        summary_table.add_row(
            "Matrix Size",
            f"{total_users} × {total_foods}",
            "Ukuran User-Item Matrix"
        )
        summary_table.add_row(
            "Possible Ratings",
            f"{total_possible:,}",
            "Total kemungkinan rating"
        )
        summary_table.add_row(
            "Sparsity",
            f"{sparsity*100:.2f}%",
            "Persentase cell kosong dalam matrix"
        )

        console.print(summary_table)

        # SVD & Similarity Configuration
        console.print("\n[bold]🔧 Algorithm Configuration:[/bold]")

        config_table = Table(
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 2)
        )
        config_table.add_column("Parameter", style="cyan")
        config_table.add_column("Value", style="green")
        config_table.add_column("Description", style="dim")

        config_table.add_row(
            "Similarity Method",
            "Cosine Similarity",
            "Metode untuk mencari similar users"
        )
        config_table.add_row(
            "Similarity Threshold",
            "0.2",
            "Minimum similarity score"
        )
        config_table.add_row(
            "Top K Similar Users",
            "50",
            "Jumlah similar users yang diambil"
        )
        config_table.add_row(
            "SVD Latent Factors",
            "Dynamic (3-4)",
            "Jumlah faktor laten dalam SVD"
        )
        config_table.add_row(
            "Min Rating Threshold",
            "3.0",
            "Minimum predicted rating"
        )
        config_table.add_row(
            "Hybrid Alpha",
            "0.7",
            "70% food rating, 30% restaurant rating"
        )

        console.print(config_table)

        # Calculation Steps
        console.print("\n[bold]⚙️ Calculation Steps:[/bold]")

        steps_panel = Panel(
            """[cyan]1. Load Rating Matrix[/cyan]
   • Load semua ratings dari database
   • Buat User-Item matrix (67 users × 35 foods)

[cyan]2. Calculate User Similarity[/cyan]
   • Hitung cosine similarity antar users
   • Similarity = (A·B) / (||A|| × ||B||)
   • Filter users dengan similarity > 0.2

[cyan]3. Create Local Dataset[/cyan]
   • Pilih top 50 similar users
   • Buat local matrix untuk efficiency
   • Include hanya items yang relevan

[cyan]4. Apply SVD Decomposition[/cyan]
   • Matrix = U × Σ × V^T
   • U: User-Feature matrix
   • Σ: Singular values (diagonal)
   • V^T: Feature-Item matrix

[cyan]5. Predict Ratings[/cyan]
   • Reconstruct matrix: R̂ = U × Σ × V^T
   • Filter predictions > 3.0
   • Rank by predicted rating

[cyan]6. Generate Recommendations[/cyan]
   • Exclude already rated items
   • Return top N recommendations
   • Enrich with food details""",
            title="📋 Algorithm Pipeline",
            border_style="blue",
            padding=(1, 2)
        )

        console.print(steps_panel)

        # Mathematical formulas
        console.print("\n[bold]📐 Key Formulas:[/bold]")

        formulas_table = Table(
            box=box.MINIMAL,
            show_header=True,
            header_style="bold yellow"
        )
        formulas_table.add_column("Formula", style="cyan", width=50)
        formulas_table.add_column("Description", style="dim", width=40)

        formulas_table.add_row(
            "Cosine Similarity:",
            "Ukur kemiripan 2 user berdasarkan rating pattern"
        )
        formulas_table.add_row(
            "  sim(u,v) = Σ(rᵤ·rᵥ) / (√Σrᵤ² × √Σrᵥ²)",
            "Dot product / (magnitude u × magnitude v)"
        )
        formulas_table.add_row(
            "",
            ""
        )
        formulas_table.add_row(
            "SVD Decomposition:",
            "Faktorisasi matrix menjadi 3 komponen"
        )
        formulas_table.add_row(
            "  R = U × Σ × Vᵀ",
            "R: Rating matrix, U: User features"
        )
        formulas_table.add_row(
            "",
            ""
        )
        formulas_table.add_row(
            "Predicted Rating:",
            "Rekonstruksi rating dari SVD"
        )
        formulas_table.add_row(
            "  r̂ᵤᵢ = Σₖ(Uᵤₖ × Σₖ × Vᵢₖ)",
            "Sum of user-feature × singular value × item-feature"
        )

        console.print(formulas_table)

        console.print("\n")

    except Exception as e:
        console.print(f"[yellow]⚠️ Could not display calculation summary: {str(e)}[/yellow]")


def display_recommendations(
    user_name, user_username, recommendations, user_ratings_data
):
    """Display recommendations for a user with Rich Console"""
    console.rule("[bold cyan]🎉 FINAL RECOMMENDATIONS", style="cyan")

    # Create panel for user info
    user_info = f"[bold yellow]{user_name}[/bold yellow] [dim](@{user_username})[/dim]"
    console.print(
        Panel(user_info, title="🎯 TOP RECOMMENDATIONS FOR", border_style="cyan")
    )

    # Display user's rating history
    console.print("\n[bold]📊 User's Rating History:[/bold]")

    history_table = Table(
        show_header=True, header_style="bold magenta", box=box.ROUNDED
    )
    history_table.add_column("Food Name", style="yellow", no_wrap=False, width=30)
    history_table.add_column("Restaurant", style="cyan", width=20)
    history_table.add_column("Price", justify="right", style="green")
    history_table.add_column("Rating", justify="center", style="blue")

    if user_ratings_data:
        for rating_data in user_ratings_data[:10]:  # Show max 10
            food_name = rating_data.get("food_name", "N/A")
            restaurant_name = rating_data.get("restaurant_name", "N/A") or "N/A"
            price = rating_data.get("price", 0)
            rating = rating_data.get("rating", 0.0)

            price_str = f"Rp {price:,.0f}" if price else "N/A"
            stars = "⭐" * int(round(rating))

            history_table.add_row(
                food_name[:30],
                restaurant_name[:20],
                price_str,
                f"{rating:.1f} {stars}",
            )

        console.print(history_table)
        if len(user_ratings_data) > 10:
            console.print(
                f"[dim](Showing 10 of {len(user_ratings_data)} rated items)[/dim]"
            )
    else:
        console.print("[yellow]No rating history found.[/yellow]")

    # Display recommendations
    console.print("\n[bold]⭐ RECOMMENDED ITEMS:[/bold]")

    rec_table = Table(show_header=True, header_style="bold magenta", box=box.DOUBLE)
    rec_table.add_column("Rank", justify="center", style="cyan", width=6)
    rec_table.add_column("Food Name", style="yellow", no_wrap=False, width=35)
    rec_table.add_column("Restaurant", style="cyan", width=22)
    rec_table.add_column("Price", justify="right", style="green", width=12)
    rec_table.add_column("Pred. Rating", justify="center", style="blue", width=12)
    rec_table.add_column("Stars", justify="center", style="yellow", width=10)

    for rec in recommendations:
        rank = rec.get("rank", 0)
        food_name = rec.get("food_name", "Unknown")
        restaurant_name = rec.get("restaurant_name", "N/A") or "N/A"
        price = rec.get("price", 0)
        pred_rating = rec.get("predicted_rating", 0.0)

        price_str = f"Rp {price:,.0f}" if price else "N/A"
        stars = "⭐" * int(round(pred_rating))

        rec_table.add_row(
            f"#{rank}",
            food_name[:35],
            restaurant_name[:22],
            price_str,
            f"{pred_rating:.2f}",
            stars,
        )

    console.print(rec_table)

    # Statistics
    if recommendations:
        console.print("\n[bold]📈 RECOMMENDATION STATISTICS:[/bold]")
        avg_pred = sum(r.get("predicted_rating", 0.0) for r in recommendations) / len(
            recommendations
        )
        min_pred = min(r.get("predicted_rating", 0.0) for r in recommendations)
        max_pred = max(r.get("predicted_rating", 0.0) for r in recommendations)

        console.print(
            f"  [cyan]•[/cyan] Average Predicted Rating: [bold]{avg_pred:.2f}[/bold]"
        )
        console.print(
            f"  [cyan]•[/cyan] Prediction Range: [bold]{min_pred:.2f}[/bold] - [bold]{max_pred:.2f}[/bold]"
        )
        console.print(
            f"  [cyan]•[/cyan] Method: [bold yellow]SVD Collaborative Filtering (Production)[/bold yellow]"
        )


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Main execution function - Uses Production Recommendation System"""

    console.print("\n[bold white on blue]" + " " * 100 + "[/bold white on blue]")
    console.print(
        "[bold white on blue]  SISTEM REKOMENDASI MAKANAN - PRODUCTION SYSTEM TESTING"
        + " " * 40
        + "[/bold white on blue]"
    )
    console.print(
        "[bold white on blue]  SVD Collaborative Filtering with Rich Console Display"
        + " " * 43
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
                f"[green]✓[/green] Found user: [bold]{user.name}[/bold] (@{user.username})"
            )

            # Get user's rating history
            console.print(f"\n[cyan]📊 Loading rating history...[/cyan]")

            user_ratings = FoodRating.query.filter_by(user_id=user.id).all()

            user_ratings_data = []
            for rating in user_ratings:
                food = Food.query.get(rating.food_id)
                if food:
                    user_ratings_data.append(
                        {
                            "food_name": food.name,
                            "restaurant_name": (
                                food.restaurant_name
                                if hasattr(food, "restaurant_name")
                                else "N/A"
                            ),
                            "price": food.price if hasattr(food, "price") else 0,
                            "rating": rating.rating,
                        }
                    )

            console.print(f"[green]✓[/green] Loaded {len(user_ratings_data)} ratings")

            # Display calculation summary before getting recommendations
            display_calculation_summary()

            # Get recommendations from production system with calculation details
            recommendations, similarity_matrix, svd_info = get_recommendations_from_production(user.id, top_n=10)

            if not recommendations:
                console.print("\n[bold red]❌ No recommendations generated![/bold red]")
                return

            # Display Cosine Similarity Results
            if similarity_matrix:
                display_cosine_similarity_table(similarity_matrix, user.id)

            # Display SVD Results
            if svd_info:
                display_svd_results(svd_info)

            # Format recommendations for display
            # Production service already enriches with food details
            console.print(f"\n[cyan]� Formatting recommendations...[/cyan]")

            formatted_recommendations = []
            for rec in recommendations:
                formatted_recommendations.append(
                    {
                        "rank": rec.get("rank"),
                        "food_name": rec.get("name", "Unknown"),
                        "restaurant_name": rec.get("restaurant_name", "N/A"),
                        "price": rec.get("price", 0),
                        "predicted_rating": rec.get("predicted_rating"),
                    }
                )

            console.print(
                f"[green]✓[/green] Formatted {len(formatted_recommendations)} recommendations"
            )

            # Display recommendations with Rich Console
            display_recommendations(
                user_name=user.name,
                user_username=user.username,
                recommendations=formatted_recommendations,
                user_ratings_data=user_ratings_data,
            )

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        import traceback

        console.print(f"[red]{traceback.format_exc()}[/red]")
        return

    console.print("\n[bold white on green]" + " " * 100 + "[/bold white on green]")
    console.print(
        "[bold white on green]  ✅ TESTING SELESAI"
        + " " * 80
        + "[/bold white on green]"
    )
    console.print("[bold white on green]" + " " * 100 + "[/bold white on green]\n")


if __name__ == "__main__":
    main()
