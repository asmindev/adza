import React from "react";
import { motion } from "framer-motion";
import FoodCard from "@/components/food/FoodCard";
import FoodCardSkeleton from "@/components/food/FoodCardSkeleton";

const AllFoodsTab = ({ foods, loading, onToggleFavorite }) => {
    if (loading) {
        return (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-6">
                {Array(8)
                    .fill()
                    .map((_, index) => (
                        <FoodCardSkeleton key={index} />
                    ))}
            </div>
        );
    }

    if (foods.length === 0) {
        return (
            <div className="col-span-full text-center py-10">
                <h3 className="text-xl font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tidak ada makanan ditemukan
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                    Coba sesuaikan filter pencarian Anda
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
            {foods.map((food) => (
                <FoodCard
                    key={food.id}
                    food={food}
                    onToggleFavorite={onToggleFavorite}
                />
            ))}
        </motion.div>
    );
};

export default AllFoodsTab;
