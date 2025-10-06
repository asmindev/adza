"""
Script untuk menguji evaluasi model SVD
Melakukan training dan evaluasi dengan train-test split
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from app.recommendation.local_data import LocalDataProcessor
from app.recommendation.local_model import LocalSVDModel
from app.utils.logger import get_logger
from app.extensions import db
from app import create_app

logger = get_logger(__name__)


def print_section(title):
    """Print section separator"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_model_evaluation():
    """
    Test SVD model evaluation dengan train-test split
    """
    print_section("🧪 TEST MODEL EVALUATION - SVD RECOMMENDER SYSTEM")

    # Initialize Flask app context
    app = create_app()

    with app.app_context():
        # 1. Load data
        print("📊 Step 1: Loading ratings data from database...")
        data_processor = LocalDataProcessor(alpha=0.7)
        ratings_df = data_processor.load_hybrid_ratings_from_db()

        if len(ratings_df) == 0:
            print("❌ No ratings data found!")
            return

        print(f"✅ Loaded {len(ratings_df)} ratings")
        print(f"   - Users: {ratings_df['user_id'].nunique()}")
        print(f"   - Foods: {ratings_df['food_id'].nunique()}")
        print(
            f"   - Rating range: [{ratings_df['rating'].min():.1f}, {ratings_df['rating'].max():.1f}]"
        )
        print(f"   - Average rating: {ratings_df['rating'].mean():.2f}")

        # 2. Create pivot matrix
        print_section("📈 Step 2: Creating User-Item Matrix")

        pivot_matrix = ratings_df.pivot_table(
            index="user_id", columns="food_id", values="rating", fill_value=0
        )

        n_users, n_items = pivot_matrix.shape
        total_possible = n_users * n_items
        actual_ratings = (pivot_matrix.values > 0).sum()
        sparsity = 1 - (actual_ratings / total_possible)

        print(f"Matrix shape: {n_users} users × {n_items} items")
        print(f"Sparsity: {sparsity:.1%}")
        print(f"Total ratings: {actual_ratings}/{total_possible}")

        # 3. Train-Test Split Strategy
        print_section("🔀 Step 3: Train-Test Split")

        # Strategy: Split by randomly holding out 20% of ratings per user
        train_matrix = pivot_matrix.copy()
        test_matrix = pd.DataFrame(
            0, index=pivot_matrix.index, columns=pivot_matrix.columns
        )

        test_ratio = 0.2
        n_test_ratings = 0
        n_train_ratings = 0

        print(f"Splitting with test ratio: {test_ratio:.0%}")

        for user_idx in range(n_users):
            user_ratings_indices = np.where(pivot_matrix.iloc[user_idx].values > 0)[0]

            if len(user_ratings_indices) < 2:
                # If user has less than 2 ratings, keep all in training
                continue

            # Randomly select test indices
            n_test = max(1, int(len(user_ratings_indices) * test_ratio))
            test_indices = np.random.choice(
                user_ratings_indices, size=n_test, replace=False
            )

            for test_idx in test_indices:
                # Move rating from train to test
                rating_value = train_matrix.iloc[user_idx, test_idx]
                test_matrix.iloc[user_idx, test_idx] = rating_value
                train_matrix.iloc[user_idx, test_idx] = 0
                n_test_ratings += 1

            n_train_ratings += len(user_ratings_indices) - n_test

        print(f"✅ Split completed:")
        print(f"   - Training ratings: {n_train_ratings}")
        print(f"   - Test ratings: {n_test_ratings}")
        print(
            f"   - Actual test ratio: {n_test_ratings/(n_train_ratings + n_test_ratings):.1%}"
        )

        # 4. Train SVD Model
        print_section("🎯 Step 4: Training SVD Model")

        svd_model = LocalSVDModel(n_components=12, random_state=42)

        print("Training on train matrix...")
        success = svd_model.fit(train_matrix)

        if not success:
            print("❌ Training failed!")
            return

        model_info = svd_model.get_model_info()
        print(f"✅ Training completed!")
        print(f"   - Components: {model_info.get('n_components', 'N/A')}")
        print(
            f"   - Explained variance: {model_info.get('total_explained_variance', 0):.1%}"
        )
        print(f"   - Global mean: {model_info.get('global_mean', 0):.2f}")

        # 5. Evaluate on Test Set
        print_section("📊 Step 5: Model Evaluation on Test Set")

        print("Evaluating model performance...")
        metrics = svd_model.evaluate_model(test_matrix)

        if not metrics:
            print("❌ Evaluation failed!")
            return

        print(f"✅ Evaluation Results:")
        print(f"\n📈 Accuracy Metrics:")
        print(f"   - MAE (Mean Absolute Error):     {metrics.get('mae', 0):.4f}")
        print(f"   - MSE (Mean Squared Error):      {metrics.get('mse', 0):.4f}")
        print(f"   - RMSE (Root Mean Squared Error): {metrics.get('rmse', 0):.4f}")

        print(f"\n🎯 Ranking Metrics:")
        print(f"   - NDCG@10 (Normalized DCG):      {metrics.get('ndcg', 0):.4f}")

        print(f"\n📊 Coverage Metrics:")
        print(f"   - Coverage (items ≥ 3.0):        {metrics.get('coverage', 0):.1%}")

        print(f"\n📉 Test Statistics:")
        print(f"   - Total predictions:             {metrics.get('n_predictions', 0)}")
        print(
            f"   - Users evaluated (NDCG):        {metrics.get('n_users_evaluated', 0)}"
        )

        # 6. Interpretation
        print_section("💡 Step 6: Results Interpretation")

        mae = metrics.get("mae", 0)
        rmse = metrics.get("rmse", 0)
        ndcg = metrics.get("ndcg", 0)

        print("🔍 Model Performance Analysis:\n")

        # MAE interpretation
        if mae < 0.5:
            mae_quality = "Excellent ⭐⭐⭐⭐⭐"
        elif mae < 0.75:
            mae_quality = "Very Good ⭐⭐⭐⭐"
        elif mae < 1.0:
            mae_quality = "Good ⭐⭐⭐"
        elif mae < 1.5:
            mae_quality = "Fair ⭐⭐"
        else:
            mae_quality = "Poor ⭐"

        print(f"1. MAE = {mae:.4f} → {mae_quality}")
        print(f"   Average prediction error is {mae:.2f} stars on a 1-5 scale")

        # RMSE interpretation
        if rmse < 0.7:
            rmse_quality = "Excellent ⭐⭐⭐⭐⭐"
        elif rmse < 1.0:
            rmse_quality = "Very Good ⭐⭐⭐⭐"
        elif rmse < 1.3:
            rmse_quality = "Good ⭐⭐⭐"
        elif rmse < 1.8:
            rmse_quality = "Fair ⭐⭐"
        else:
            rmse_quality = "Poor ⭐"

        print(f"\n2. RMSE = {rmse:.4f} → {rmse_quality}")
        print(f"   Penalizes larger errors more heavily")

        # NDCG interpretation
        if ndcg > 0.8:
            ndcg_quality = "Excellent ⭐⭐⭐⭐⭐"
        elif ndcg > 0.6:
            ndcg_quality = "Very Good ⭐⭐⭐⭐"
        elif ndcg > 0.4:
            ndcg_quality = "Good ⭐⭐⭐"
        elif ndcg > 0.2:
            ndcg_quality = "Fair ⭐⭐"
        else:
            ndcg_quality = "Poor ⭐"

        print(f"\n3. NDCG@10 = {ndcg:.4f} → {ndcg_quality}")
        print(f"   Ranking quality (1.0 = perfect ranking)")

        # Overall assessment
        print(f"\n{'─' * 80}")
        avg_score = (
            (1 if mae < 0.75 else 0)
            + (1 if rmse < 1.0 else 0)
            + (1 if ndcg > 0.4 else 0)
        ) / 3

        if avg_score > 0.8:
            overall = "🎉 EXCELLENT - Model is performing very well!"
        elif avg_score > 0.5:
            overall = "👍 GOOD - Model is performing adequately"
        else:
            overall = "⚠️  NEEDS IMPROVEMENT - Consider model tuning"

        print(f"\n🏆 Overall Assessment: {overall}")

        # 7. Sample Predictions
        print_section("🔮 Step 7: Sample Predictions")

        # Get first user with test ratings
        sample_user_idx = None
        for i in range(min(5, n_users)):
            if test_matrix.iloc[i].sum() > 0:
                sample_user_idx = i
                break

        if sample_user_idx is not None:
            print(f"Sample predictions for User #{sample_user_idx}:\n")
            print(f"{'Food Index':<12} {'Actual':<10} {'Predicted':<12} {'Error':<10}")
            print(f"{'-' * 50}")

            for food_idx in range(min(10, n_items)):
                actual = test_matrix.iloc[sample_user_idx, food_idx]
                if actual > 0:
                    predicted = svd_model.predict_user_item(sample_user_idx, food_idx)
                    error = abs(actual - predicted)
                    print(
                        f"{food_idx:<12} {actual:<10.2f} {predicted:<12.3f} {error:<10.3f}"
                    )

        # 8. Recommendations Test
        print_section("🎁 Step 8: Generate Sample Recommendations")

        if sample_user_idx is not None:
            # Get items user has rated (to exclude)
            rated_items = list(
                np.where(pivot_matrix.iloc[sample_user_idx].values > 0)[0]
            )

            # Get top recommendations
            recommendations = svd_model.get_top_recommendations(
                user_idx=sample_user_idx,
                top_n=10,
                exclude_items=rated_items,
                min_rating=3.0,
            )

            print(f"Top 10 recommendations for User #{sample_user_idx}:\n")
            print(f"{'Rank':<6} {'Food Index':<12} {'Predicted Rating':<20}")
            print(f"{'-' * 40}")

            for rank, (food_idx, predicted_rating) in enumerate(recommendations, 1):
                print(f"{rank:<6} {food_idx:<12} {predicted_rating:<20.3f}")

        print_section("✅ EVALUATION COMPLETED")


if __name__ == "__main__":
    try:
        # Set random seed for reproducibility
        np.random.seed(42)

        # Run test
        test_model_evaluation()

    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)
