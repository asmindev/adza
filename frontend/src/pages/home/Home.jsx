import React, { useState, useCallback } from "react";

import {
    ANIMATION_VARIANTS,
    PAGINATION_CONSTANTS,
    handleToggleFavorite,
} from "./utils";
import {
    EmptyState,
    ErrorState,
    LoadingState,
} from "./components/StateComponents";
import { SearchSection } from "./components/SearchSection";
import { HeroSection } from "./components/HeroSection";
import { FoodCollectionSection } from "./components/FoodSection";
import { usePaginatedFoods } from "./hooks/usePaginatedFoods";
import { useInfiniteScroll } from "./hooks/useInfiniteScroll";

export default function Home() {
    const [searchQuery, setSearchQuery] = useState("");

    const { foods, error, loading, hasMore, loadMore } = usePaginatedFoods(
        PAGINATION_CONSTANTS.DEFAULT_LIMIT,
        searchQuery
    );

    const { isLoadingMore } = useInfiniteScroll(loadMore, {
        hasMore,
        loading,
        threshold: PAGINATION_CONSTANTS.LOAD_MORE_THRESHOLD,
        throttleDelay: PAGINATION_CONSTANTS.THROTTLE_DELAY,
    });

    // Event handlers
    const onToggleFavorite = useCallback((foodId) => {
        handleToggleFavorite(foodId);
    }, []);

    const onSearch = useCallback((query) => {
        setSearchQuery(query);
        console.log("Searching for:", query);
    }, []);

    // Loading and error states
    if (error) {
        return <ErrorState error={error} />;
    }

    // if (loading && (!foods || foods.length === 0)) {
    //     return <LoadingState />;
    // }

    // Main render
    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <HeroSection />

            {/* Search Section */}
            <SearchSection
                onSearch={onSearch}
                searchValue={searchQuery}
                isLoading={loading}
            />

            {/* Food Collection Section */}
            {foods && foods.length > 0 ? (
                <FoodCollectionSection
                    foods={foods}
                    containerVariants={ANIMATION_VARIANTS.container}
                    onToggleFavorite={onToggleFavorite}
                    isLoadingMore={isLoadingMore}
                />
            ) : !loading ? (
                <EmptyState />
            ) : null}
        </div>
    );
}
