import { useMemo } from "react";

export const useFoodFilters = (
    foods,
    searchQuery,
    showFavorites,
    selectedCategory,
    favorites
) => {
    return useMemo(() => {
        if (!foods) return [];

        return foods.filter((food) => {
            // Search filtering
            const matchesSearch =
                !searchQuery ||
                food.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                food.description
                    ?.toLowerCase()
                    .includes(searchQuery.toLowerCase());

            // Favorites filtering
            const matchesFavorites =
                !showFavorites || favorites.includes(food.id);

            // Category filtering
            const matchesCategory =
                !selectedCategory || food.category === selectedCategory;

            return matchesSearch && matchesFavorites && matchesCategory;
        });
    }, [foods, searchQuery, showFavorites, selectedCategory, favorites]);
};

export const useFoodCategories = (foods) => {
    return useMemo(() => {
        if (!foods) return [];
        return [...new Set(foods.map((food) => food.category).filter(Boolean))];
    }, [foods]);
};

export const useFoodSortAndFilter = (foods) => {
    const allFoods = useMemo(() => foods || [], [foods]);

    const recommendedFoods = useMemo(() => {
        if (!foods) return [];
        return foods.filter((food) => food.average_rating >= 4.0).slice(0, 8);
    }, [foods]);

    const topRatedFoods = useMemo(() => {
        if (!foods) return [];
        return [...foods]
            .sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
            .slice(0, 12);
    }, [foods]);

    return {
        allFoods,
        recommendedFoods,
        topRatedFoods,
    };
};
