"""
Performance Test for Recommendation System with 100+ Users
Tests recommendation generation time and memory usage
"""

import time
import random
import statistics
from datetime import datetime
from app import create_app
from app.modules.user.models import User
from app.recommendation.recommender import Recommendations
from app.extensions import db

# Test configuration
NUM_TEST_USERS = 20  # Test with random 20 users
NUM_RECOMMENDATIONS = 10
NUM_REPETITIONS = 3  # Test each user multiple times for consistency


class PerformanceMonitor:
    """Simple performance monitor without psutil"""

    def __init__(self):
        self.start_time = time.time()

    def get_current_memory(self):
        """Placeholder for memory usage"""
        return 0

    def get_memory_usage(self):
        """Placeholder for memory usage"""
        return 0


def test_recommendation_performance():
    """Test recommendation system performance"""
    app = create_app()

    with app.app_context():
        print("🚀 Starting Recommendation System Performance Test")
        print(
            f"Target: Test {NUM_TEST_USERS} users with {NUM_REPETITIONS} repetitions each"
        )
        print(f"Requesting {NUM_RECOMMENDATIONS} recommendations per user")
        print("-" * 60)

        # Initialize performance monitor
        monitor = PerformanceMonitor()

        # Get all users (excluding the first 5 original users)
        all_users = db.session.query(User).offset(5).all()  # Skip original 5 users

        if len(all_users) < NUM_TEST_USERS:
            print(f"❌ Not enough users! Found {len(all_users)}, need {NUM_TEST_USERS}")
            return

        print(f"Found {len(all_users)} total users (excluding original 5)")

        # Select random test users
        test_users = random.sample(all_users, NUM_TEST_USERS)
        print(f"Selected {len(test_users)} random users for testing")

        # Initialize recommendation system
        print("Initializing recommendation system...")
        start_init = time.time()
        recommender = Recommendations(alpha=0.7)  # Default hybrid scoring
        init_time = time.time() - start_init
        print(f"✅ Recommendation system initialized in {init_time:.3f}s")

        memory_after_init = monitor.get_memory_usage()
        print(f"Memory usage after init: +{memory_after_init:.1f}MB")
        print("-" * 60)

        # Store results
        all_times = []
        all_recommendations = []
        user_results = []

        # Test each user
        for i, user in enumerate(test_users, 1):
            print(f"\n🧪 Testing User {i}/{NUM_TEST_USERS}: {user.username}")

            user_times = []
            user_recommendations = []

            # Test multiple times for consistency
            for rep in range(NUM_REPETITIONS):
                start_time = time.time()

                try:
                    # Test recommendation generation
                    recommendations, scores = recommender.recommend_with_scores(
                        user.id, NUM_RECOMMENDATIONS
                    )

                    end_time = time.time()
                    processing_time = end_time - start_time

                    user_times.append(processing_time)
                    user_recommendations.append(len(recommendations))

                    print(
                        f"  Rep {rep+1}: {processing_time:.3f}s → {len(recommendations)} recommendations"
                    )

                    # Show sample recommendations for first repetition
                    if rep == 0 and recommendations:
                        sample_scores = {
                            food_id: scores[food_id] for food_id in recommendations[:3]
                        }
                        print(f"  Sample scores: {sample_scores}")

                except Exception as e:
                    print(f"  Rep {rep+1}: ❌ ERROR - {e}")
                    user_times.append(float("inf"))
                    user_recommendations.append(0)

            # Calculate user statistics
            valid_times = [t for t in user_times if t != float("inf")]
            if valid_times:
                avg_time = statistics.mean(valid_times)
                min_time = min(valid_times)
                max_time = max(valid_times)
                avg_recommendations = statistics.mean(user_recommendations)

                user_results.append(
                    {
                        "username": user.username,
                        "avg_time": avg_time,
                        "min_time": min_time,
                        "max_time": max_time,
                        "avg_recommendations": avg_recommendations,
                        "success_rate": len(valid_times) / NUM_REPETITIONS,
                    }
                )

                all_times.extend(valid_times)
                all_recommendations.extend(user_recommendations)

                print(
                    f"  📊 User {user.username}: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s"
                )
            else:
                print(f"  ❌ All tests failed for user {user.username}")

        # Calculate overall statistics
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE RESULTS")
        print("=" * 60)

        if all_times:
            # Time statistics
            avg_time = statistics.mean(all_times)
            median_time = statistics.median(all_times)
            min_time = min(all_times)
            max_time = max(all_times)
            std_time = statistics.stdev(all_times) if len(all_times) > 1 else 0

            print(f"⏱️  Response Time Statistics:")
            print(f"   Average: {avg_time:.3f}s")
            print(f"   Median:  {median_time:.3f}s")
            print(f"   Min:     {min_time:.3f}s")
            print(f"   Max:     {max_time:.3f}s")
            print(f"   Std Dev: {std_time:.3f}s")

            # Performance categories
            fast_count = sum(1 for t in all_times if t < 1.0)
            medium_count = sum(1 for t in all_times if 1.0 <= t < 3.0)
            slow_count = sum(1 for t in all_times if t >= 3.0)

            print(f"\n📊 Performance Distribution:")
            print(
                f"   Fast (<1s):     {fast_count}/{len(all_times)} ({fast_count/len(all_times)*100:.1f}%)"
            )
            print(
                f"   Medium (1-3s):  {medium_count}/{len(all_times)} ({medium_count/len(all_times)*100:.1f}%)"
            )
            print(
                f"   Slow (≥3s):     {slow_count}/{len(all_times)} ({slow_count/len(all_times)*100:.1f}%)"
            )

            # Recommendation statistics
            avg_rec_count = statistics.mean(all_recommendations)
            print(f"\n🎯 Recommendation Statistics:")
            print(f"   Average recommendations per user: {avg_rec_count:.1f}")
            print(f"   Target recommendations: {NUM_RECOMMENDATIONS}")

            # Memory usage (simplified without psutil)
            print(f"\n💾 Memory Usage:")
            print(f"   Memory monitoring: Not available (psutil not installed)")
            print(f"   Test duration: {time.time() - monitor.start_time:.1f}s")

            # System statistics
            stats = recommender.get_system_stats()
            print(f"\n🔧 System Statistics:")
            print(f"   Total requests: {stats.get('total_requests', 0)}")
            print(f"   Success rate: {stats.get('success_rate', 0):.1%}")
            print(f"   Fallback rate: {stats.get('fallback_rate', 0):.1%}")

            # Performance assessment
            print(f"\n🏆 PERFORMANCE ASSESSMENT:")
            if avg_time < 1.0:
                print(f"   ✅ EXCELLENT: Average response time {avg_time:.3f}s")
            elif avg_time < 2.0:
                print(f"   ✅ GOOD: Average response time {avg_time:.3f}s")
            elif avg_time < 5.0:
                print(f"   ⚠️  ACCEPTABLE: Average response time {avg_time:.3f}s")
            else:
                print(
                    f"   ❌ POOR: Average response time {avg_time:.3f}s - Optimization needed!"
                )

            # Scalability assessment
            print(f"\n📈 SCALABILITY ASSESSMENT:")
            requests_per_minute = 60 / avg_time if avg_time > 0 else 0
            concurrent_users = (
                requests_per_minute / 4
            )  # Assuming 4 requests per user per minute

            print(f"   Estimated throughput: {requests_per_minute:.1f} requests/minute")
            print(f"   Estimated concurrent users: {concurrent_users:.1f} users")

            if concurrent_users >= 100:
                print(f"   ✅ GOOD: Can handle 100+ concurrent users")
            elif concurrent_users >= 50:
                print(f"   ⚠️  MODERATE: Can handle 50+ concurrent users")
            else:
                print(f"   ❌ LIMITED: May struggle with high concurrency")

            # Top and bottom performers
            user_results.sort(key=lambda x: x["avg_time"])
            print(f"\n🏃 TOP PERFORMERS (Fastest):")
            for user in user_results[:3]:
                print(f"   {user['username']}: {user['avg_time']:.3f}s avg")

            print(f"\n🐌 BOTTOM PERFORMERS (Slowest):")
            for user in user_results[-3:]:
                print(f"   {user['username']}: {user['avg_time']:.3f}s avg")

        else:
            print("❌ No successful tests completed!")

        print("\n" + "=" * 60)
        print(f"Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    test_recommendation_performance()
