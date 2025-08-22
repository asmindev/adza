import React from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Star, Heart, MapPin, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatPrice, formatRating, getRatingColor } from "@/utils";

export default function FoodDetailHeader({
    food,
    onBack,
    onToggleFavorite,
    isFavorite,
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            {/* Navigation */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={onBack}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Kembali
                </Button>
            </div>

            {/* Food Info */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Image */}
                <div className="relative">
                    <img
                        src={food.image_url || "/images/placeholder-food.jpg"}
                        alt={food.name}
                        className="w-full h-96 object-cover rounded-lg shadow-lg"
                    />
                    <Button
                        variant="secondary"
                        size="icon"
                        className="absolute top-4 right-4"
                        onClick={onToggleFavorite}
                    >
                        <Heart
                            className={`h-5 w-5 ${
                                isFavorite
                                    ? "fill-red-500 text-red-500"
                                    : "text-muted-foreground"
                            }`}
                        />
                    </Button>
                </div>

                {/* Info */}
                <div className="space-y-4">
                    <div>
                        <h1 className="text-3xl font-bold text-foreground mb-2">
                            {food.name}
                        </h1>
                        <p className="text-lg text-muted-foreground leading-relaxed">
                            {food.description}
                        </p>
                    </div>

                    {/* Rating & Price */}
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                            <Star className="h-5 w-5 text-yellow-400 fill-yellow-400" />
                            <span
                                className={`font-medium ${getRatingColor(
                                    food.average_rating
                                )}`}
                            >
                                {formatRating(food.average_rating || 0)}
                            </span>
                            <span className="text-muted-foreground">
                                ({food.total_reviews || 0} ulasan)
                            </span>
                        </div>
                        <div className="text-2xl font-bold text-primary">
                            {formatPrice(food.price)}
                        </div>
                    </div>

                    {/* Category & Restaurant */}
                    <div className="flex flex-wrap gap-2">
                        {food.category && (
                            <Badge variant="secondary">{food.category}</Badge>
                        )}
                        {food.restaurant && (
                            <Badge
                                variant="outline"
                                className="flex items-center gap-1"
                            >
                                <MapPin className="h-3 w-3" />
                                {food.restaurant.name}
                            </Badge>
                        )}
                    </div>

                    {/* Additional Info */}
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            <span>Tersedia sekarang</span>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
