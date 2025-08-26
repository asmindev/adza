import React from "react";
import { Star } from "lucide-react";

function StarRating({ rating, showRating = true, size = "sm" }) {
    const filledStars = Math.floor(rating);

    return (
        <div className="flex items-center gap-1">
            <div className="flex">
                <Star
                    className={`${size === "sm" ? "h-4 w-4" : "h-5 w-5"} ${
                        rating < filledStars
                            ? "text-yellow-500 fill-yellow-500"
                            : "text-muted-foreground/30 fill-muted-foreground/30"
                    }`}
                />
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
