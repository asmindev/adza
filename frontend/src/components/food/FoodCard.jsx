import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router"; // Fixed import from react-router to react-router-dom
import { Badge } from "@/components/ui/badge";
import { Heart, Clock, Award, Star, DollarSign } from "lucide-react"; // Added DollarSign
import { cn } from "@/lib/utils";

export default function FoodCard({
    food,
    onToggleFavorite,
    hybridScore,
    predictedRating,
}) {
    if (!food) return null;
    console.log("FoodCard food", food);

    const handleFavoriteClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        onToggleFavorite(food.id);
    };

    // Format price to IDR currency
    const formattedPrice = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0,
    }).format(food.price || 0);

    // The card animation
    const cardVariants = {
        hidden: { opacity: 0, y: 50 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
    };

    // Get image URL from main_image if available
    const imageUrl =
        food.main_image?.image_url ||
        (food.images && food.images.length > 0
            ? food.images[0].image_url
            : null) ||
        food.image ||
        "https://placehold.co/600x400?text=Food+Image";

    return (
        <motion.div variants={cardVariants}>
            <Link
                to={`/food/${food.id}`}
                className="block"
                aria-label={`View details for ${food.name}`}
            >
                <div className="w-full group bg-white dark:bg-gray-800 rounded-lg overflow-hidden duration-300 border hover:shadow-2xl shadow-accent/20">
                    <div className="relative">
                        <img
                            src={imageUrl}
                            alt={food.name}
                            className="w-full min-w-52 h-48 min-h-48 object-cover transition-transform duration-300 group-hover:scale-105"
                            onError={(e) => {
                                e.target.src =
                                    "https://placehold.co/600x400?text=Food+Image";
                            }}
                        />
                        <button
                            onClick={handleFavoriteClick}
                            className="absolute top-2 right-2 p-2 bg-white dark:bg-gray-900 rounded-full shadow-md hover:scale-110 transition-transform"
                            aria-label={
                                food.isFavorite
                                    ? "Remove from favorites"
                                    : "Add to favorites"
                            }
                        >
                            <Heart
                                className={cn(
                                    "h-5 w-5",
                                    food.isFavorite
                                        ? "fill-red-500 text-red-500"
                                        : "text-gray-400 dark:text-gray-300"
                                )}
                            />
                        </button>

                        {/* Show category badge on the image */}
                        {food.category && (
                            <div className="absolute top-2 left-2 px-2 py-1 bg-white/80 dark:bg-gray-800/80 text-gray-800 dark:text-white text-xs font-medium rounded">
                                {food.category}
                            </div>
                        )}
                    </div>

                    <div className="p-4">
                        <div className="flex justify-between items-start mb-2">
                            <h3 className="font-bold text-gray-800 dark:text-white line-clamp-1">
                                {food.name}
                            </h3>
                            <div className="flex items-center">
                                <Star className="h-4 w-4 text-yellow-500 mr-1" />

                                {food?.ratings?.average && (
                                    <span className="text-xs text-gray-500 ml-1">
                                        {food?.ratings?.average.toFixed(1)}
                                    </span>
                                )}
                            </div>
                        </div>

                        {/* <p className="text-gray-600 dark:text-gray-400 text-sm mb-3 line-clamp-2">
                            {food.description}
                        </p> */}

                        <div className="flex flex-wrap gap-2">
                            {/* Price badge */}
                            {food.price && (
                                <Badge
                                    variant="outline"
                                    className="flex items-center gap-1 bg-secondary/10 text-secondary dark:bg-green-900/30 dark:text-green-300"
                                >
                                    {/* <DollarSign className="h-3 w-3" /> */}
                                    {formattedPrice}
                                </Badge>
                            )}
                        </div>
                    </div>
                </div>
            </Link>
        </motion.div>
    );
}
