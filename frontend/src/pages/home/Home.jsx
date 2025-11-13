import React, { useState, useCallback, useContext } from "react";

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
import { SectionLoading } from "./components/SectionLoading";
import { usePaginatedFoods } from "./hooks/usePaginatedFoods";
import { useInfiniteScroll } from "./hooks/useInfiniteScroll";
import { useRecommendations } from "./hooks/useRecommendations";
import { usePopularFoods } from "./hooks/usePopularFoods";
import { UserContext } from "@/contexts/UserContextDefinition";

export default function Home() {
    const [searchQuery, setSearchQuery] = useState("");
    const { isAuthenticated } = useContext(UserContext);
    const isLoggedIn = isAuthenticated();

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

    // Fetch recommendations only if logged in
    const {
        recommendations,
        loading: recommendationsLoading,
        error: recommendationsError,
    } = useRecommendations(isLoggedIn, 8);

    // Fetch popular foods
    const {
        popularFoods,
        loading: popularLoading,
        error: popularError,
    } = usePopularFoods(8, 5);

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

            {/* If user is logged in, show: Recommendations -> Popular -> All Foods */}
            {isLoggedIn ? (
                <>
                    {/* Recommendations Section */}
                    {recommendationsLoading ? (
                        <SectionLoading title="Rekomendasi untuk Anda" />
                    ) : recommendationsError ? (
                        <div className="container mx-auto px-4 py-4">
                            <p className="text-red-500 dark:text-red-400">
                                Gagal memuat rekomendasi
                            </p>
                        </div>
                    ) : recommendations && recommendations.length > 0 ? (
                        <FoodCollectionSection
                            foods={recommendations.slice(0, 8)}
                            containerVariants={ANIMATION_VARIANTS.container}
                            onToggleFavorite={onToggleFavorite}
                            isLoadingMore={false}
                            title="Rekomendasi untuk Anda"
                            subtitle="Makanan yang dipersonalisasi berdasarkan preferensi Anda"
                            showDivider={true}
                            viewAllLink="/recommendation"
                        />
                    ) : null}

                    {/* Popular Foods Section */}
                    {popularLoading ? (
                        <SectionLoading title="Makanan Populer" />
                    ) : popularError ? (
                        <div className="container mx-auto px-4 py-4">
                            <p className="text-red-500 dark:text-red-400">
                                Gagal memuat makanan populer
                            </p>
                        </div>
                    ) : popularFoods && popularFoods.length > 0 ? (
                        <FoodCollectionSection
                            foods={popularFoods.slice(0, 8)}
                            containerVariants={ANIMATION_VARIANTS.container}
                            onToggleFavorite={onToggleFavorite}
                            isLoadingMore={false}
                            title="Makanan Populer"
                            subtitle="Makanan favorit yang banyak disukai"
                            showDivider={true}
                            viewAllLink="/popular"
                        />
                    ) : null}

                    {/* All Foods Section */}
                    {foods && foods.length > 0 ? (
                        <FoodCollectionSection
                            foods={foods}
                            containerVariants={ANIMATION_VARIANTS.container}
                            onToggleFavorite={onToggleFavorite}
                            isLoadingMore={isLoadingMore}
                            title="Semua Makanan"
                            subtitle="Jelajahi semua makanan yang tersedia"
                            showDivider={false}
                        />
                    ) : !loading ? (
                        <EmptyState />
                    ) : null}
                </>
            ) : (
                <>
                    {/* If not logged in, show: Popular -> All Foods */}
                    {/* Popular Foods Section */}
                    {popularLoading ? (
                        <SectionLoading title="Makanan Populer" />
                    ) : popularError ? (
                        <div className="container mx-auto px-4 py-4">
                            <p className="text-red-500 dark:text-red-400">
                                Gagal memuat makanan populer
                            </p>
                        </div>
                    ) : popularFoods && popularFoods.length > 0 ? (
                        <FoodCollectionSection
                            foods={popularFoods.slice(0, 8)}
                            containerVariants={ANIMATION_VARIANTS.container}
                            onToggleFavorite={onToggleFavorite}
                            isLoadingMore={false}
                            title="Makanan Populer"
                            subtitle="Makanan favorit yang banyak disukai"
                            showDivider={true}
                            viewAllLink="/popular"
                        />
                    ) : null}

                    {/* All Foods Section */}
                    {foods && foods.length > 0 ? (
                        <FoodCollectionSection
                            foods={foods}
                            containerVariants={ANIMATION_VARIANTS.container}
                            onToggleFavorite={onToggleFavorite}
                            isLoadingMore={isLoadingMore}
                            title="Semua Makanan"
                            subtitle="Jelajahi semua makanan yang tersedia"
                            showDivider={false}
                        />
                    ) : !loading ? (
                        <EmptyState />
                    ) : null}
                </>
            )}
        </div>
    );
}
