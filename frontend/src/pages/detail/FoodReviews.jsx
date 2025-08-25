import React from "react";
import { MessageCircle, ThumbsUp, Send, Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { formatTimeAgo } from "@/utils";

import FormReviews from "./components/FormReviews";

export default function FoodReviews({
    reviews = [],
    foodId,
    foodRatings = {
        data: [],
    },
}) {
    return (
        <div className="mb-6">
            <div className="bg-muted py-2 mb-2">
                <FormReviews
                    foodId={foodId}
                    onReviewSubmitted={(data) => {
                        // Handle review submitted - this will be called after successful submission
                        console.log("Review submitted:", data);
                    }}
                />
            </div>
            <div className="flex items-center gap-x-2 border-b border-muted py-2">
                <h2 className="text-lg font-semibold text-foreground flex items-center">
                    <MessageCircle className="mr-1.5 text-primary h-4 w-4" />
                    {reviews.length} Ulasan Pelanggan
                </h2>
            </div>
            {/* Compact reviews list */}
            {reviews.length > 0 ? (
                <div>
                    {reviews.map((review) => (
                        <Card
                            key={review.id}
                            className="overflow-hidden shadow-none border py-3 border-none"
                        >
                            <CardContent className="p-0">
                                <div className="flex items-start gap-2">
                                    <Avatar className="h-7 w-7 border">
                                        <AvatarFallback className="text-xs font-semibold text-muted-foreground">
                                            {review.user?.name
                                                ?.split(" ")
                                                .map((name) => name[0])
                                                .join("") || "?"}
                                        </AvatarFallback>
                                    </Avatar>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex flex-wrap justify-between items-center gap-1 mb-1">
                                            <div className="flex items-center gap-2">
                                                <h3 className="font-medium text-sm truncate">
                                                    {review.user?.name ||
                                                        "Pengguna Anonim"}
                                                </h3>
                                                {/* Compact rating stars */}
                                                {foodRatings?.data?.find(
                                                    (r) =>
                                                        r.user_id ===
                                                        review.user?.id
                                                ) && (
                                                    <div className="flex items-center">
                                                        {[...Array(5)].map(
                                                            (_, i) => {
                                                                const rating =
                                                                    foodRatings.data.find(
                                                                        (r) =>
                                                                            r.user_id ===
                                                                            review
                                                                                .user
                                                                                ?.id
                                                                    )?.rating ||
                                                                    0;
                                                                return (
                                                                    <Star
                                                                        key={i}
                                                                        className={`h-2.5 w-2.5 ${
                                                                            i <
                                                                            rating
                                                                                ? "text-yellow-400 fill-yellow-400"
                                                                                : "text-muted-foreground/30"
                                                                        }`}
                                                                    />
                                                                );
                                                            }
                                                        )}
                                                    </div>
                                                )}
                                                <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                                                    {formatTimeAgo(
                                                        review.created_at
                                                    )}
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-muted-foreground text-xs line-clamp-3">
                                            {review.content}
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            ) : (
                <div className="text-center py-6 bg-muted/30 rounded-lg">
                    <MessageCircle className="h-8 w-8 mx-auto text-muted-foreground/50 mb-2" />
                    <h3 className="text-sm font-medium text-foreground mb-1">
                        Belum Ada Ulasan
                    </h3>
                    <p className="text-xs text-muted-foreground max-w-md mx-auto">
                        Jadilah yang pertama berbagi pengalaman Anda dengan
                        hidangan ini.
                    </p>
                </div>
            )}
        </div>
    );
}
