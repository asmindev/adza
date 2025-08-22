import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import FoodCard from "@/components/food/FoodCard";
import FoodCardSkeleton from "@/components/food/FoodCardSkeleton";
import PriceRangeFilter from "@/components/search/PriceRangeFilter";
import useSWR from "swr";
import { toast } from "sonner";

// Loading fallback component
const LoadingFallback = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-6">
        {Array(8)
            .fill()
            .map((_, index) => (
                <FoodCardSkeleton key={index} />
            ))}
    </div>
);

// Recommendations Content component (used with Suspense)
const RecommendationsContent = ({
    onToggleFavorite,
    favorites = [],
    onError,
    priceFilter,
}) => {
    // Build query parameters for price filtering
    const queryParams = new URLSearchParams();
    if (priceFilter.min_price > 0) {
        queryParams.append("min_price", priceFilter.min_price.toString());
    }
    if (priceFilter.max_price < 100000) {
        queryParams.append("max_price", priceFilter.max_price.toString());
    }

    const queryString = queryParams.toString();
    const apiUrl = `/api/v1/recommendations${
        queryString ? `?${queryString}` : ""
    }`;

    // Use SWR with suspense mode enabled
    const { data, error } = useSWR(apiUrl, {
        suspense: true,
        revalidateOnFocus: false,
        revalidateOnMount: true,
        onError: (err) => {
            // Menangani kesalahan
            toast.error("Failed to load recommendations", {
                description: err.message || "Please try again later",
            });
        },
    });
    console.log("Recommendations data:", data);

    useEffect(() => {
        if (data?.error) {
            onError(
                new Error(data.message || "Failed to load recommendations")
            );
            toast.error("Failed to load recommendations", {
                description: data.message || "Please try again later",
            });
        }
    }, [data, onError]);

    // Empty state
    if (data?.length === 0) {
        return (
            <div className="col-span-full text-center py-10">
                <h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
                    No recommendations available
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                    Try rating some recipes to get personalized recommendations
                </p>
            </div>
        );
    }

    return (
        <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-6"
            initial="hidden"
            animate="visible"
            variants={{
                hidden: { opacity: 0, y: 20 },
                visible: {
                    opacity: 1,
                    y: 0,
                    transition: { staggerChildren: 0.05 },
                },
            }}
        >
            {data?.recommendations?.map((food) => (
                <FoodCard
                    key={food.food.id}
                    food={food.food}
                    onToggleFavorite={onToggleFavorite}
                    isFavorite={favorites.includes(food.id)}
                />
            ))}
        </motion.div>
    );
};

// Main component without ErrorBoundary
const RecommendedTab = ({ onToggleFavorite, favorites = [] }) => {
    const [hasError, setHasError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [priceFilter, setPriceFilter] = useState({
        min_price: 0,
        max_price: 100000,
    });

    const handleError = (error) => {
        setHasError(true);
        setErrorMessage(error.message || "Failed to load recommendations");
    };

    const resetError = () => {
        setHasError(false);
        setErrorMessage("");
        window.location.reload();
    };

    const handlePriceChange = (newPriceFilter) => {
        setPriceFilter(newPriceFilter);
    };

    if (hasError) {
        return (
            <div className="col-span-full text-center py-10">
                <h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Something went wrong
                </h3>
                <p className="text-gray-500 dark:text-gray-400 mb-4">
                    {errorMessage}
                </p>
                <button
                    onClick={resetError}
                    className="px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90"
                >
                    Try again
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Price Range Filter */}
            <PriceRangeFilter
                onPriceChange={handlePriceChange}
                initialMinPrice={priceFilter.min_price}
                initialMaxPrice={priceFilter.max_price}
                minPrice={0}
                maxPrice={100000}
            />

            {/* Recommendations Content */}
            <React.Suspense fallback={<LoadingFallback />}>
                <RecommendationsContent
                    onToggleFavorite={onToggleFavorite}
                    favorites={favorites}
                    onError={handleError}
                    priceFilter={priceFilter}
                />
            </React.Suspense>
        </div>
    );
};

export default RecommendedTab;
