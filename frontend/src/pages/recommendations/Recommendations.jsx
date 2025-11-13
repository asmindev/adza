import React, { useCallback, useContext } from "react";
import { useNavigate } from "react-router";
import { UserContext } from "@/contexts/UserContextDefinition";
import {
    ANIMATION_VARIANTS,
    handleToggleFavorite,
} from "../home/utils";
import { EmptyState, ErrorState } from "../home/components/StateComponents";
import { FoodCollectionSection } from "../home/components/FoodSection";
import { SectionLoading } from "../home/components/SectionLoading";
import { useRecommendations } from "../home/hooks/useRecommendations";

export default function Recommendations() {
    const { isAuthenticated } = useContext(UserContext);
    const navigate = useNavigate();
    const isLoggedIn = isAuthenticated();

    // Redirect if not logged in
    React.useEffect(() => {
        if (!isLoggedIn) {
            navigate("/");
        }
    }, [isLoggedIn, navigate]);

    const {
        recommendations,
        loading,
        error,
    } = useRecommendations(isLoggedIn, 50); // Fetch more items for full page

    const onToggleFavorite = useCallback((foodId) => {
        handleToggleFavorite(foodId);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen pt-20">
                <SectionLoading title="Rekomendasi untuk Anda" />
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
                        Rekomendasi untuk Anda
                    </h1>
                    <p className="text-orange-100 mt-2">
                        Makanan yang dipersonalisasi berdasarkan preferensi Anda
                    </p>
                </div>
            </div>

            {/* Content */}
            {recommendations && recommendations.length > 0 ? (
                <FoodCollectionSection
                    foods={recommendations}
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
