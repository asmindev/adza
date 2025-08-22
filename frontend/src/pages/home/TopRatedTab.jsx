import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import FoodCard from "@/components/food/FoodCard";
import FoodCardSkeleton from "@/components/food/FoodCardSkeleton";
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

// Top Rated Content component (used with Suspense)
const TopRatedContent = ({ onToggleFavorite, favorites = [], onError }) => {
    // Use SWR with suspense mode enabled
    const { data, error } = useSWR("/api/v1/recommendations/top-rated", {
        suspense: true,
        revalidateOnFocus: false,
        revalidateOnMount: true,
        onError: (err) => {
            // Menangani kesalahan
            toast.error("Gagal memuat makanan populer", {
                description: err.message || "Please try again later",
            });
        },
    });

    useEffect(() => {
        if (data?.error) {
            onError(new Error(data.message || "Gagal memuat makanan populer"));
            toast.error("Gagal memuat makanan populer", {
                description: data.message || "Silakan coba lagi nanti",
            });
        }
    }, [data, onError]);

    // Empty state
    if (data?.length === 0) {
        return (
            <div className="col-span-full text-center py-10">
                <h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Belum ada makanan populer
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                    Jadilah yang pertama untuk menilai makanan
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
            {data?.top_rated?.map((food) => (
                <FoodCard
                    key={food.id}
                    food={food}
                    onToggleFavorite={onToggleFavorite}
                    isFavorite={favorites.includes(food.id)}
                />
            ))}
        </motion.div>
    );
};

// Main component that uses state for error handling
const TopRatedTab = ({ onToggleFavorite, favorites = [] }) => {
    const [hasError, setHasError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    const handleError = (error) => {
        setHasError(true);
        setErrorMessage(error.message || "Gagal memuat makanan populer");
    };

    const resetError = () => {
        setHasError(false);
        setErrorMessage("");
        window.location.reload();
    };

    if (hasError) {
        return (
            <div className="col-span-full text-center py-10">
                <h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Terjadi kesalahan
                </h3>
                <p className="text-gray-500 dark:text-gray-400 mb-4">
                    {errorMessage}
                </p>
                <button
                    onClick={resetError}
                    className="px-4 py-2 bg-accent text-white rounded-md hover:bg-accent/90"
                >
                    Coba Lagi
                </button>
            </div>
        );
    }

    return (
        <React.Suspense fallback={<LoadingFallback />}>
            <TopRatedContent
                onToggleFavorite={onToggleFavorite}
                favorites={favorites}
                onError={handleError}
            />
        </React.Suspense>
    );
};

export default TopRatedTab;
