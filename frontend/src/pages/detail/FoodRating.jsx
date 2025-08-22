import React, { useState, useEffect } from "react";
import { Star } from "lucide-react";

export default function FoodRating({
    averageRating = 0,
    ratingCount = 0,
    onRateFood,
    foodId,
    initialRating = 0,
}) {
    const [userRating, setUserRating] = useState(initialRating);
    const [hoveredRating, setHoveredRating] = useState(0);

    useEffect(() => {
        setUserRating(initialRating);
    }, [initialRating]);

    const handleRating = async (rating) => {
        setUserRating(rating);

        if (onRateFood) {
            await onRateFood({ rating, food_id: foodId });
        }
    };

    return (
        <div className="mb-4">
            {/* Display average rating */}
            <div className="flex items-center mb-2">
                <div className="flex items-center space-x-1">
                    {[...Array(5)].map((_, index) => (
                        <Star
                            key={index}
                            className={`h-4 w-4 ${
                                index < Math.floor(averageRating)
                                    ? "text-yellow-400 fill-yellow-400"
                                    : index < averageRating
                                    ? "text-yellow-400 fill-yellow-400/50"
                                    : "text-muted-foreground/30"
                            }`}
                        />
                    ))}
                    <span className="ml-1 text-muted-foreground font-medium">
                        {averageRating.toFixed(1)}
                    </span>
                    {ratingCount > 0 && (
                        <span className="text-muted-foreground/80 text-sm">
                            ({ratingCount}{" "}
                            {ratingCount === 1 ? "penilaian" : "penilaian"})
                        </span>
                    )}
                </div>
            </div>

            {/* Interactive rating selector */}
            <div className="mb-4">
                <p className="text-sm text-muted-foreground mb-1">
                    Nilai hidangan ini:
                </p>
                <div className="flex items-center">
                    {[1, 2, 3, 4, 5].map((rating) => (
                        <button
                            key={rating}
                            onClick={() => handleRating(rating)}
                            onMouseEnter={() => setHoveredRating(rating)}
                            onMouseLeave={() => setHoveredRating(0)}
                            className="mr-1 focus:outline-none transition-transform hover:scale-110"
                        >
                            <Star
                                className={`h-6 w-6 ${
                                    rating <= (hoveredRating || userRating)
                                        ? "text-yellow-400 fill-yellow-400"
                                        : "text-muted-foreground/30"
                                }`}
                            />
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
