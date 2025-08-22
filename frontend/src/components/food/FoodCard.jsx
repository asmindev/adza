import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Heart, Star, MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

export default function FoodCard({ food, onToggleFavorite }) {
    if (!food) return null;

    const handleFavoriteClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        onToggleFavorite?.(food.id);
    };

    // Format price to IDR currency
    const formattedPrice = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0,
    }).format(food.price || 0);

    // Card animations
    const cardVariants = {
        hidden: { opacity: 0, y: 15 },
        visible: {
            opacity: 1,
            y: 0,
            transition: { duration: 0.3 },
        },
    };

    // Get image URL
    const imageUrl =
        food.main_image?.image_url ||
        food.images?.[0]?.image_url ||
        food.image ||
        "https://placehold.co/600x400?text=Food+Image";

    return (
        <motion.div variants={cardVariants}>
            <Link to={`/food/${food.id}`} className="block group">
                <Card className="border-1 shadow-none duration-300 overflow-hidden p-0">
                    {/* Image Section */}
                    <div className="relative aspect-[5/3] overflow-hidden">
                        <img
                            src={imageUrl}
                            alt={food.name}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            onError={(e) => {
                                e.target.src =
                                    "https://placehold.co/600x400?text=Food+Image";
                            }}
                        />

                        {/* Favorite Button */}
                        <button
                            onClick={handleFavoriteClick}
                            className="absolute top-2 right-2 p-1.5 bg-white/90 rounded-full shadow-sm hover:scale-110 transition-transform"
                        >
                            <Heart
                                className={cn(
                                    "h-3.5 w-3.5",
                                    food.isFavorite
                                        ? "fill-rose-500 text-rose-500"
                                        : "text-gray-600"
                                )}
                            />
                        </button>

                        {/* Price Badge */}
                        <Badge className="absolute bottom-2 right-2 bg-emerald-500 text-white text-xs px-2 py-1">
                            {formattedPrice}
                        </Badge>
                    </div>

                    {/* Content Section */}
                    <div className="p-3">
                        {/* Title */}
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100 line-clamp-1 text-sm mb-1">
                            {food.name}
                        </h3>

                        {/* Restaurant & Rating Row */}
                        <div className="flex items-center justify-between text-xs">
                            {/* Restaurant */}
                            {food.restaurant && (
                                <div className="flex items-center gap-1 text-gray-600 dark:text-gray-400 flex-1 min-w-0">
                                    <MapPin className="w-3 h-3 flex-shrink-0" />
                                    <span className="truncate">
                                        {food.restaurant.name}
                                    </span>
                                </div>
                            )}

                            {/* Rating */}
                            {food.ratings && (
                                <div className="flex items-center gap-1 ml-2">
                                    <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                                    <span className="font-medium text-gray-900 dark:text-gray-100">
                                        {food.ratings.average?.toFixed(1) ||
                                            "0.0"}
                                    </span>
                                    <span className="text-gray-500">
                                        ({food.ratings.count || 0})
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                </Card>
            </Link>
        </motion.div>
    );
}
