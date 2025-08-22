import React, { useState } from "react";
import { motion } from "framer-motion";

// Import modular components
import HomeHeader from "./components/HomeHeader";
import FoodTabs from "./components/FoodTabs";
import SearchAndFilter from "@/components/search/SearchAndFilter";

// Import common components
import {
    LoadingGrid,
    ErrorState,
    EmptyState,
} from "@/components/common/CommonStates";

// Import hooks
import { useFoodData } from "@/hooks/useApiData";
import { useFavorites } from "@/hooks/useFavorites";
import {
    useFoodSortAndFilter,
    useFoodCategories,
} from "@/hooks/useFoodFilters";

// Import icons
import { Utensils } from "lucide-react";

export default function HomePage() {
    const [activeTab, setActiveTab] = useState("all");

    // Fetch food data using custom hook
    const { foods, isLoading, error, refetch } = useFoodData();

    // Manage favorites using custom hook
    const { favorites, toggleFavorite } = useFavorites();

    // Sort and filter foods using custom hook
    const { allFoods, recommendedFoods, topRatedFoods } =
        useFoodSortAndFilter(foods);

    // Get categories for filtering
    const categories = useFoodCategories(foods);

    // Retry function for error state
    const handleRetry = () => {
        refetch();
    };

    return (
        <div className="min-h-screen">
            <div className="max-w-7xl mx-auto p-4 space-y-8">
                {/* Header */}
                {/* <HomeHeader /> */}

                {/* Search and Filter */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <SearchAndFilter
                        categories={categories}
                        showFavorites={false}
                        onShowFavoritesChange={() => {}}
                    />
                </motion.div>

                {/* Content */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                >
                    {isLoading ? (
                        <LoadingGrid count={12} />
                    ) : error ? (
                        <ErrorState
                            title="Gagal Memuat Makanan"
                            description="Terjadi kesalahan saat memuat daftar makanan"
                            onRetry={handleRetry}
                        />
                    ) : foods.length === 0 ? (
                        <EmptyState
                            icon={Utensils}
                            title="Belum Ada Makanan"
                            description="Belum ada makanan yang tersedia di sistem"
                        />
                    ) : (
                        <FoodTabs
                            activeTab={activeTab}
                            setActiveTab={setActiveTab}
                            allFoods={allFoods}
                            recommendedFoods={recommendedFoods}
                            topRatedFoods={topRatedFoods}
                            isLoading={isLoading}
                            toggleFavorite={toggleFavorite}
                            favorites={favorites}
                        />
                    )}
                </motion.div>
            </div>
        </div>
    );
}
