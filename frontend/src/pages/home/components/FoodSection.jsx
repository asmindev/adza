import React from "react";
// eslint-disable-next-line no-unused-vars
import { motion } from "framer-motion";
import FoodCard from "@/components/food/FoodCard";
import { Link } from "react-router";

/**
 * Food Collection Section Component
 * Menampilkan section koleksi makanan dengan grid layout
 */
export function FoodCollectionSection({
    foods,
    containerVariants,
    onToggleFavorite,
    isLoadingMore,
    title,
    subtitle,
    showDivider = true,
    viewAllLink,
}) {
    return (
        <div className="container mx-auto px-4 py-8">
            {/* Section Title */}
            {title && (
                <div className="mb-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
                                {title}
                            </h2>
                            {subtitle && (
                                <p className="text-gray-600 dark:text-gray-400 mt-2">
                                    {subtitle}
                                </p>
                            )}
                        </div>
                        {viewAllLink && (
                            <Link
                                // href={viewAllLink}
                                to={viewAllLink}
                                className="text-orange-600 hover:text-orange-700 dark:text-orange-400 dark:hover:text-orange-300 font-medium text-sm md:text-base flex items-center gap-1 transition-colors"
                            >
                                Lihat Semua
                                <svg
                                    className="w-4 h-4"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M9 5l7 7-7 7"
                                    />
                                </svg>
                            </Link>
                        )}
                    </div>
                </div>
            )}

            {/* Food Grid */}
            <FoodGrid
                foods={foods}
                containerVariants={containerVariants}
                onToggleFavorite={onToggleFavorite}
            />

            {/* Loading More Indicator */}
            {isLoadingMore && <LoadingMoreIndicator />}

            {/* Divider */}
            {showDivider && (
                <div className="mt-8 border-b border-gray-200 dark:border-gray-700"></div>
            )}
        </div>
    );
}

/**
 * Food Grid Component
 * Menampilkan grid layout untuk food cards
 */
function FoodGrid({ foods, containerVariants, onToggleFavorite }) {
    return (
        <motion.div
            className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
        >
            {foods.map((food) => (
                <FoodCard
                    key={food.id}
                    food={food}
                    onToggleFavorite={onToggleFavorite}
                />
            ))}
        </motion.div>
    );
}

/**
 * Loading More Indicator Component
 * Menampilkan indikator loading saat memuat data tambahan
 */
function LoadingMoreIndicator() {
    return (
        <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">
                Memuat lebih banyak...
            </span>
        </div>
    );
}
