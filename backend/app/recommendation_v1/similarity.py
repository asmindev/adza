"""
User Similarity Calculation Module
Contains functions for calculating user similarity using Jaccard and Cosine metrics
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine
from typing import Tuple, List, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Calculate Jaccard similarity between two sets

    Args:
        set1: First set of items
        set2: Second set of items

    Returns:
        float: Jaccard similarity score (0-1)
    """
    if len(set1) == 0 and len(set2) == 0:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union if union > 0 else 0.0


def cosine_similarity_sparse(
    user_matrix: csr_matrix, target_user_idx: int, other_user_idx: int
) -> float:
    """
    Calculate cosine similarity between two users in sparse matrix

    Args:
        user_matrix: Sparse user-item matrix
        target_user_idx: Index of target user
        other_user_idx: Index of other user

    Returns:
        float: Cosine similarity score (0-1)
    """
    try:
        user1_vector = user_matrix[target_user_idx].toarray().flatten()
        user2_vector = user_matrix[other_user_idx].toarray().flatten()

        # Handle zero vectors
        if np.all(user1_vector == 0) or np.all(user2_vector == 0):
            return 0.0

        # Calculate cosine similarity (1 - cosine distance)
        similarity = 1 - cosine(user1_vector, user2_vector)

        # Handle NaN results
        return similarity if not np.isnan(similarity) else 0.0

    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0


def calculate_user_similarities(
    ratings_df: pd.DataFrame,
    target_user_id: str,
    method: str = "jaccard",
    min_common_items: int = 2,
) -> Dict[str, float]:
    """
    Calculate similarities between target user and all other users

    Args:
        ratings_df: DataFrame with columns [user_id, food_id, rating]
        target_user_id: ID of the target user
        method: Similarity method ('jaccard' or 'cosine')
        min_common_items: Minimum number of common items required

    Returns:
        Dict[str, float]: Dictionary mapping user_id to similarity score
    """
    try:
        # Check if target user exists
        if target_user_id not in ratings_df["user_id"].values:
            logger.warning(f"Target user {target_user_id} not found in ratings data")
            return {}

        similarities = {}

        if method == "jaccard":
            # Get target user's rated foods
            target_foods = set(
                ratings_df[ratings_df["user_id"] == target_user_id]["food_id"]
            )

            # Calculate Jaccard similarity with each other user
            for user_id in ratings_df["user_id"].unique():
                if user_id == target_user_id:
                    continue

                user_foods = set(
                    ratings_df[ratings_df["user_id"] == user_id]["food_id"]
                )

                # Check minimum common items
                common_items = len(target_foods.intersection(user_foods))
                if common_items < min_common_items:
                    continue

                similarity = jaccard_similarity(target_foods, user_foods)
                if similarity > 0:
                    similarities[user_id] = similarity

        elif method == "cosine":
            # Create user-item matrix
            user_item_matrix = ratings_df.pivot(
                index="user_id", columns="food_id", values="rating"
            ).fillna(0)

            # Convert to sparse matrix
            sparse_matrix = csr_matrix(user_item_matrix.values)

            # Get target user index
            try:
                target_idx = user_item_matrix.index.get_loc(target_user_id)
            except KeyError:
                logger.warning(
                    f"Target user {target_user_id} not found in pivot matrix"
                )
                return {}

            # Calculate cosine similarity with each other user
            for idx, user_id in enumerate(user_item_matrix.index):
                if user_id == target_user_id:
                    continue

                # Check if users have enough common ratings
                target_ratings = user_item_matrix.iloc[target_idx]
                user_ratings = user_item_matrix.iloc[idx]
                common_items = ((target_ratings > 0) & (user_ratings > 0)).sum()

                if common_items < min_common_items:
                    continue

                similarity = cosine_similarity_sparse(sparse_matrix, target_idx, idx)
                if similarity > 0:
                    similarities[user_id] = similarity

        else:
            raise ValueError(f"Unknown similarity method: {method}")

        logger.info(
            f"Calculated {method} similarities for {len(similarities)} users with target user {target_user_id}"
        )
        return similarities

    except Exception as e:
        logger.error(f"Error calculating user similarities: {e}")
        return {}


def get_similar_users(
    ratings_df: pd.DataFrame,
    target_user_id: str,
    top_k: int = 50,
    similarity_threshold: float = 0.1,
    method: str = "jaccard",
    min_common_items: int = 2,
) -> List[Tuple[str, float]]:
    """
    Get top-K most similar users to target user

    Args:
        ratings_df: DataFrame with columns [user_id, food_id, rating]
        target_user_id: ID of the target user
        top_k: Number of top similar users to return
        similarity_threshold: Minimum similarity score threshold
        method: Similarity method ('jaccard' or 'cosine')
        min_common_items: Minimum number of common items required

    Returns:
        List[Tuple[str, float]]: List of (user_id, similarity_score) tuples
    """
    try:
        # Calculate similarities
        similarities = calculate_user_similarities(
            ratings_df, target_user_id, method=method, min_common_items=min_common_items
        )

        # Filter by threshold and sort
        filtered_similarities = [
            (user_id, score)
            for user_id, score in similarities.items()
            if score >= similarity_threshold
        ]

        # Sort by similarity score (descending) and take top-K
        similar_users = sorted(filtered_similarities, key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        logger.info(
            f"Found {len(similar_users)} similar users for {target_user_id} (threshold: {similarity_threshold})"
        )
        return similar_users

    except Exception as e:
        logger.error(f"Error getting similar users: {e}")
        return []


def validate_similarity_calculation(
    ratings_df: pd.DataFrame, sample_size: int = 5
) -> bool:
    """
    Validate similarity calculation with a small sample

    Args:
        ratings_df: DataFrame with columns [user_id, food_id, rating]
        sample_size: Number of users to test

    Returns:
        bool: True if validation passes
    """
    try:
        if len(ratings_df) == 0:
            logger.warning("Empty ratings dataframe for validation")
            return False

        # Get sample users
        sample_users = ratings_df["user_id"].unique()[:sample_size]

        for user_id in sample_users:
            # Test Jaccard similarity
            jaccard_similarities = get_similar_users(
                ratings_df, user_id, top_k=5, method="jaccard"
            )

            # Test Cosine similarity
            cosine_similarities = get_similar_users(
                ratings_df, user_id, top_k=5, method="cosine"
            )

            logger.info(
                f"User {user_id}: {len(jaccard_similarities)} Jaccard, {len(cosine_similarities)} Cosine similarities"
            )

        logger.info("Similarity calculation validation completed successfully")
        return True

    except Exception as e:
        logger.error(f"Similarity validation failed: {e}")
        return False
