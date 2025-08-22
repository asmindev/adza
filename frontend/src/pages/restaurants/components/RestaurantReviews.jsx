import React from "react";
import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { formatTimeAgo } from "@/utils";

export default function RestaurantReviews({ restaurant }) {
    if (!restaurant.rating?.rating || restaurant.rating.rating.length === 0) {
        return null;
    }

    return (
        <Card className="mt-6">
            <CardContent className="p-6">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                    <Star className="h-6 w-6 text-yellow-500" />
                    Ulasan Restoran
                </h2>
                <div className="space-y-4">
                    {restaurant.rating.rating.map((review) => (
                        <Card key={review.id} className="bg-muted/20">
                            <CardContent className="p-4">
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center gap-1">
                                        {[...Array(5)].map((_, i) => (
                                            <Star
                                                key={i}
                                                className={`h-4 w-4 ${
                                                    i < review.rating
                                                        ? "text-yellow-400 fill-yellow-400"
                                                        : "text-muted-foreground/30"
                                                }`}
                                            />
                                        ))}
                                        <span className="ml-2 font-medium">
                                            {review.rating.toFixed(1)}
                                        </span>
                                    </div>
                                    <span className="text-sm text-muted-foreground">
                                        {formatTimeAgo(review.created_at)}
                                    </span>
                                </div>
                                {review.comment && (
                                    <p className="text-muted-foreground leading-relaxed">
                                        {review.comment}
                                    </p>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
