import React from "react";
import { motion } from "framer-motion";
import FoodCard from "@/components/food/FoodCard";

/**
 * Food Collection Section Component
 * Menampilkan section koleksi makanan dengan grid layout
 */
export function FoodCollectionSection({
    foods,
    containerVariants,
    onToggleFavorite,
    isLoadingMore,
}) {
    return (
        <div className="container mx-auto px-4 py-16">
            {/* Section Header */}
            <div className="mb-12 text-center">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
                    Koleksi Makanan Pilihan
                </h2>
                <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                    Nikmati berbagai hidangan lezat yang telah dipilih khusus
                    untuk Anda
                </p>
            </div>

            {/* Food Grid */}
            <FoodGrid
                foods={foods}
                containerVariants={containerVariants}
                onToggleFavorite={onToggleFavorite}
            />

            {/* Loading More Indicator */}
            {isLoadingMore && <LoadingMoreIndicator />}
        </div>
    );
}

/**
 * Food Grid Component
 * Menampilkan grid layout untuk food cards
 */
export function FoodGrid({ foods, containerVariants, onToggleFavorite }) {
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
export function LoadingMoreIndicator() {
    return (
        <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">
                Memuat lebih banyak...
            </span>
        </div>
    );
}
