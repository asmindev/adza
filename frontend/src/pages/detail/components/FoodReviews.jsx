import React from "react";
import { motion } from "framer-motion";
import { Star, MessageSquare } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { formatTimeAgo } from "@/utils";

export default function FoodReviews({ reviews, averageRating, totalReviews }) {
    if (!reviews || reviews.length === 0) {
        return (
            <Card>
                <CardContent className="p-6">
                    <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <MessageSquare className="h-6 w-6 text-primary" />
                        Ulasan
                    </h2>
                    <div className="text-center py-8">
                        <MessageSquare className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
                        <h3 className="text-xl font-medium text-foreground mb-2">
                            Belum Ada Ulasan
                        </h3>
                        <p className="text-muted-foreground">
                            Jadilah yang pertama memberikan ulasan untuk makanan
                            ini.
                        </p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardContent className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <MessageSquare className="h-6 w-6 text-primary" />
                        Ulasan ({totalReviews})
                    </h2>
                    {averageRating && (
                        <div className="flex items-center gap-2">
                            <Star className="h-5 w-5 text-yellow-400 fill-yellow-400" />
                            <span className="text-lg font-semibold">
                                {averageRating.toFixed(1)}
                            </span>
                        </div>
                    )}
                </div>

                <div className="space-y-4">
                    {reviews.map((review) => (
                        <motion.div
                            key={review.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <Card className="bg-muted/20">
                                <CardContent className="p-4">
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-2">
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
                                            </div>
                                            <span className="font-medium">
                                                {review.rating.toFixed(1)}
                                            </span>
                                            {review.user && (
                                                <span className="text-sm text-muted-foreground">
                                                    oleh {review.user.name}
                                                </span>
                                            )}
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
                        </motion.div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
