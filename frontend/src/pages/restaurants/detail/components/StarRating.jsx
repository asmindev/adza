import React from "react";
import { Star } from "lucide-react";

function StarRating({ rating, showRating = true, size = "sm" }) {
    const filledStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    return (
        <div className="flex items-center gap-1">
            <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                        key={star}
                        className={`${size === "sm" ? "h-4 w-4" : "h-5 w-5"} ${
                            star <= filledStars
                                ? "text-yellow-500 fill-yellow-500"
                                : star === filledStars + 1 && hasHalfStar
                                ? "text-yellow-500 fill-yellow-500/50"
                                : "text-muted-foreground/30 fill-muted-foreground/30"
                        }`}
                    />
                ))}
            </div>
            {showRating && (
                <span className="text-sm font-medium text-foreground">
                    {rating.toFixed(1)}
                </span>
            )}
        </div>
    );
}

export default StarRating;
