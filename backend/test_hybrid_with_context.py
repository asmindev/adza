#!/usr/bin/env python3
"""
Test script for Hybrid Recommendation System with Flask App Context
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import Flask app
from main import app
from app.recommendation.service import (
    HybridRecommendationSystem,
    create_and_train_hybrid_system,
)
from app.modules.user.models import User
import json


def test_hybrid_recommendation_system():
    """
    Test the hybrid recommendation system with different alpha values
    """
    print("=" * 60)
    print("HYBRID RECOMMENDATION SYSTEM TEST")
    print("=" * 60)

    # Test different alpha values
    alpha_values = [0.3, 0.5, 0.7, 0.9]

    with app.app_context():
        for alpha in alpha_values:
            print(f"\n🔍 Testing with alpha = {alpha}")
            print(f"   Food weight: {alpha:.1f}, Restaurant weight: {1-alpha:.1f}")
            print("-" * 50)

            # Create and train system
            system = HybridRecommendationSystem(alpha=alpha)

            # Execute 4-step process
            results = system.train_full_system()

            if results["success"]:
                print("✅ Training completed successfully!")
                print(f"   Steps completed: {', '.join(results['steps_completed'])}")

                # Display validation metrics
                if results["validation_metrics"]:
                    print("\n📊 Validation Metrics:")
                    for model_name, metrics in results["validation_metrics"].items():
                        print(f"   {model_name.replace('_', ' ').title()}:")
                        print(
                            f"     RMSE: {metrics['rmse']:.4f} ± {metrics['rmse_std']:.4f}"
                        )
                        print(
                            f"     MAE:  {metrics['mae']:.4f} ± {metrics['mae_std']:.4f}"
                        )

                # Test prediction for a sample user
                test_user_predictions(system)

            else:
                print(f"❌ Training failed: {results['error']}")

            print("\n" + "=" * 60)


def test_user_predictions(system: HybridRecommendationSystem):
    """
    Test predictions for sample users
    """
    print("\n🎯 Testing Predictions:")

    # Get some sample users
    users = User.query.limit(3).all()

    if not users:
        print("   No users found for testing")
        return

    for user in users:
        print(f"\n   User: {user.name} (ID: {user.id})")

        # Get recommendations
        recommendations = system.predict_hybrid_recommendations(user.id, limit=5)

        if recommendations:
            print(f"   Top {len(recommendations)} recommendations:")

            for i, rec in enumerate(recommendations, 1):
                print(f"     {i}. {rec['food_name']}")
                print(f"        Restaurant: {rec['restaurant_name']}")
                print(f"        Food Rating: {rec['predicted_food_rating']:.2f}")
                print(
                    f"        Restaurant Rating: {rec['predicted_restaurant_rating']:.2f}"
                )
                print(f"        Hybrid Score: {rec['hybrid_score']:.3f}")
                print(f"        Final Rating: {rec['final_predicted_rating']:.2f}")

                if i < len(recommendations):
                    print()
        else:
            print("   No recommendations generated")


def benchmark_alpha_performance():
    """
    Benchmark different alpha values to find optimal weighting
    """
    print("\n🏆 ALPHA PARAMETER BENCHMARKING")
    print("=" * 60)

    alpha_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    results_summary = []

    with app.app_context():
        for alpha in alpha_values:
            print(f"\nTesting alpha = {alpha}")

            system = HybridRecommendationSystem(alpha=alpha)
            results = system.train_full_system()

            if results["success"]:
                metrics = results["validation_metrics"]

                # Calculate average metrics across both models
                avg_rmse = (
                    metrics["food_model"]["rmse"] + metrics["restaurant_model"]["rmse"]
                ) / 2
                avg_mae = (
                    metrics["food_model"]["mae"] + metrics["restaurant_model"]["mae"]
                ) / 2

                results_summary.append(
                    {
                        "alpha": alpha,
                        "avg_rmse": avg_rmse,
                        "avg_mae": avg_mae,
                        "food_rmse": metrics["food_model"]["rmse"],
                        "food_mae": metrics["food_model"]["mae"],
                        "restaurant_rmse": metrics["restaurant_model"]["rmse"],
                        "restaurant_mae": metrics["restaurant_model"]["mae"],
                    }
                )

                print(f"  Average RMSE: {avg_rmse:.4f}")
                print(f"  Average MAE:  {avg_mae:.4f}")

        # Find best alpha
        if results_summary:
            best_rmse = min(results_summary, key=lambda x: x["avg_rmse"])
            best_mae = min(results_summary, key=lambda x: x["avg_mae"])

            print(f"\n🏅 BEST RESULTS:")
            print(
                f"   Best RMSE: alpha = {best_rmse['alpha']} (RMSE: {best_rmse['avg_rmse']:.4f})"
            )
            print(
                f"   Best MAE:  alpha = {best_mae['alpha']} (MAE: {best_mae['avg_mae']:.4f})"
            )

            # Save results to file
            with open("alpha_benchmark_results.json", "w") as f:
                json.dump(results_summary, f, indent=2)
            print(f"\n   Results saved to: alpha_benchmark_results.json")


def demonstrate_4_steps():
    """
    Demonstrate the 4-step process clearly
    """
    print("\n📚 DEMONSTRATING 4-STEP PROCESS")
    print("=" * 60)

    with app.app_context():
        print("\n🎯 Creating Hybrid Recommendation System with alpha=0.7")
        system = HybridRecommendationSystem(alpha=0.7)

        print("\n📋 STEP-BY-STEP EXECUTION:")
        print("=" * 50)

        # Step 1: Import modules
        print("\n🔧 STEP 1: Import Modules")
        print("-" * 30)
        step1_result = system._import_modules()
        print(f"Result: {'✅ Success' if step1_result else '❌ Failed'}")

        # Step 2: Prepare data
        print("\n📊 STEP 2: Prepare Data")
        print("-" * 30)
        step2_result = system._prepare_data()
        print(f"Result: {'✅ Success' if step2_result else '❌ Failed'}")

        if step2_result:
            food_count = (
                len(system.food_ratings_df) if system.food_ratings_df is not None else 0
            )
            restaurant_count = (
                len(system.restaurant_ratings_df)
                if system.restaurant_ratings_df is not None
                else 0
            )
            print(f"  - Food ratings: {food_count} records")
            print(f"  - Restaurant ratings: {restaurant_count} records")

        # Step 3: Train models
        print("\n🧠 STEP 3: Train and Test Models")
        print("-" * 30)
        step3_result = system._train_and_test_models()
        print(f"Result: {'✅ Success' if step3_result else '❌ Failed'}")

        # Step 4: Validate models
        print("\n📈 STEP 4: Validate Models (RMSE & MAE)")
        print("-" * 30)
        validation_results = system._validate_models()
        if validation_results:
            print("✅ Validation completed successfully!")
            for model_name, metrics in validation_results.items():
                print(f"\n  {model_name.replace('_', ' ').title()}:")
                print(f"    RMSE: {metrics['rmse']:.4f} ± {metrics['rmse_std']:.4f}")
                print(f"    MAE:  {metrics['mae']:.4f} ± {metrics['mae_std']:.4f}")
        else:
            print("❌ Validation failed")

        # Step 5: Predict
        print("\n🎯 STEP 5: Generate Predictions")
        print("-" * 30)
        users = User.query.limit(2).all()
        if users:
            for user in users:
                print(f"\nPredictions for {user.name}:")
                recommendations = system.predict_hybrid_recommendations(
                    user.id, limit=3
                )

                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        print(
                            f"  {i}. {rec['food_name']} (Score: {rec['hybrid_score']:.3f})"
                        )
                else:
                    print("  No recommendations available")
        else:
            print("  No users found for testing")


def main():
    """
    Main test function
    """
    try:
        # Demonstrate 4-step process
        demonstrate_4_steps()

        # Test the hybrid recommendation system
        test_hybrid_recommendation_system()

        # Benchmark different alpha values
        benchmark_alpha_performance()

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
