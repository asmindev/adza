import React, { useCallback } from "react";
import { useNavigate } from "react-router";
import {
    ANIMATION_VARIANTS,
    handleToggleFavorite,
} from "../home/utils";
import { EmptyState, ErrorState } from "../home/components/StateComponents";
import { FoodCollectionSection } from "../home/components/FoodSection";
import { SectionLoading } from "../home/components/SectionLoading";
import { usePopularFoods } from "../home/hooks/usePopularFoods";

export default function Popular() {
    const navigate = useNavigate();

    const {
        popularFoods,
        loading,
        error,
    } = usePopularFoods(50, 5); // Fetch more items for full page

    const onToggleFavorite = useCallback((foodId) => {
        handleToggleFavorite(foodId);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen pt-20">
                <SectionLoading title="Makanan Populer" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen pt-20">
                <ErrorState error={error} />
            </div>
        );
    }

    return (
        <div className="min-h-screen pt-20">
            {/* Header */}
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 py-12">
                <div className="container mx-auto px-4">
                    <button
                        onClick={() => navigate("/")}
                        className="text-white hover:text-orange-100 mb-4 flex items-center gap-2 transition-colors"
                    >
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15 19l-7-7 7-7"
                            />
                        </svg>
                        Kembali
                    </button>
                    <h1 className="text-3xl md:text-4xl font-bold text-white">
                        Makanan Populer
                    </h1>
                    <p className="text-orange-100 mt-2">
                        Makanan favorit yang banyak disukai
                    </p>
                </div>
            </div>

            {/* Content */}
            {popularFoods && popularFoods.length > 0 ? (
                <FoodCollectionSection
                    foods={popularFoods}
                    containerVariants={ANIMATION_VARIANTS.container}
                    onToggleFavorite={onToggleFavorite}
                    isLoadingMore={false}
                    showDivider={false}
                />
            ) : (
                <div className="py-20">
                    <EmptyState />
                </div>
            )}
        </div>
    );
}
