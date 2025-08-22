import React from "react";
import { motion } from "framer-motion";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";

export const LoadingGrid = ({ count = 8, className = "" }) => (
    <div
        className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 ${className}`}
    >
        {Array(count)
            .fill()
            .map((_, index) => (
                <Card key={index} className="overflow-hidden">
                    <CardContent className="p-0">
                        <Skeleton className="h-48 w-full" />
                        <div className="p-4 space-y-2">
                            <Skeleton className="h-6 w-3/4" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-2/3" />
                            <div className="flex justify-between items-center pt-2">
                                <Skeleton className="h-5 w-20" />
                                <Skeleton className="h-8 w-8 rounded-full" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            ))}
    </div>
);

export const EmptyState = ({
    icon: Icon,
    title,
    description,
    action,
    className = "",
}) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`text-center py-12 ${className}`}
    >
        {Icon && (
            <Icon className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
        )}
        <h3 className="text-xl font-medium text-foreground mb-2">{title}</h3>
        <p className="text-muted-foreground mb-4">{description}</p>
        {action && action}
    </motion.div>
);

export const ErrorState = ({
    title = "Terjadi Kesalahan",
    description = "Silakan coba lagi nanti",
    onRetry,
    className = "",
}) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`text-center py-12 ${className}`}
    >
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h3 className="text-xl font-medium text-foreground mb-2">{title}</h3>
        <p className="text-muted-foreground mb-4">{description}</p>
        {onRetry && (
            <button
                onClick={onRetry}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
                Coba Lagi
            </button>
        )}
    </motion.div>
);

export const FoodGrid = ({
    foods,
    onToggleFavorite,
    favorites,
    className = "",
}) => (
    <div
        className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 ${className}`}
    >
        {foods.map((food, index) => (
            <motion.div
                key={food.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
            >
                <FoodCard
                    food={food}
                    onToggleFavorite={() => onToggleFavorite(food.id)}
                    isFavorite={favorites.includes(food.id)}
                />
            </motion.div>
        ))}
    </div>
);

// Import FoodCard component
import FoodCard from "@/components/food/FoodCard";
