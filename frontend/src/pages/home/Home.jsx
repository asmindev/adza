import React from "react";
import { motion } from "framer-motion";
import { useFoodData } from "@/hooks/useApiData";
import FoodCard from "@/components/food/FoodCard";

export default function Home() {
    const { foods, error } = useFoodData();

    // Animation variants for food grid
    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
            },
        },
    };

    // Event handlers
    const handleToggleFavorite = (foodId) => {
        // TODO: Implement favorite toggle logic
        console.log("Toggle favorite for food:", foodId);
    };

    // Loading and error states
    if (error) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-red-600 mb-2">
                        Error Loading Data
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        {error.message ||
                            "Failed to load food data. Please try again later."}
                    </p>
                </div>
            </div>
        );
    }

    if (!foods) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">
                        Loading food data...
                    </p>
                </div>
            </div>
        );
    }

    // Render empty state
    if (!foods || foods.length === 0) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                        No Food Items Found
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400">
                        We couldn't find any food items at the moment. Please
                        try again later.
                    </p>
                </div>
            </div>
        );
    }

    // Main render
    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <HeroSection />

            {/* Food Collection Section */}
            <FoodCollectionSection
                foods={foods}
                containerVariants={containerVariants}
                onToggleFavorite={handleToggleFavorite}
            />
        </div>
    );
}

// Hero Section Component
function HeroSection() {
    const heroVariants = {
        hidden: { opacity: 0, y: 50 },
        visible: { opacity: 1, y: 0 },
    };

    const titleVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0 },
    };

    return (
        <div className="px-4 md:px-10 py-8">
            <section className="relative text-white overflow-hidden w-full h-96 md:h-120 flex items-center rounded-2xl shadow-2xl">
                {/* Background Image */}
                <div
                    className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                    style={{
                        backgroundImage:
                            "url('https://cdn.rri.co.id/berita/10/images/1706597617604-6/ols2xpnjja8j69y.jpeg')",
                    }}
                />

                {/* Dark Overlay */}
                <div className="absolute inset-0 bg-black/50" />

                {/* Content */}
                <div className="relative container mx-auto px-4 py-20 md:py-32">
                    <motion.div
                        className="mx-auto text-center max-w-4xl"
                        variants={heroVariants}
                        initial="hidden"
                        animate="visible"
                        transition={{ duration: 0.8 }}
                    >
                        <motion.h1
                            className="text-4xl md:text-6xl font-bold mb-6 leading-tight"
                            variants={titleVariants}
                            transition={{ delay: 0.2, duration: 0.8 }}
                        >
                            Lapar?
                        </motion.h1>

                        <motion.p
                            className="text-xl md:text-2xl mb-8 text-white/90 max-w-2xl mx-auto leading-relaxed"
                            variants={titleVariants}
                            transition={{ delay: 0.4, duration: 0.8 }}
                        >
                            Cari rekomendasi kuliner di Kendari
                        </motion.p>
                    </motion.div>
                </div>
            </section>
        </div>
    );
}

// Food Collection Section Component
function FoodCollectionSection({ foods, containerVariants, onToggleFavorite }) {
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
            <motion.div
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
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
        </div>
    );
}
