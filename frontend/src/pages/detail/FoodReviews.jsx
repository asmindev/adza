import React, { useState } from "react";
import { MessageCircle, ThumbsUp, Send, Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { formatTimeAgo } from "@/utils";

export default function FoodReviews({
    reviews = [],
    onSubmitReview,
    foodId,
    foodRatings = {
        data: [],
    },
}) {
    const [reviewText, setReviewText] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!reviewText.trim()) return;

        setIsSubmitting(true);

        try {
            await onSubmitReview({ food_id: foodId, content: reviewText });
            setReviewText("");
        } catch (error) {
            console.error("Gagal mengirim ulasan:", error);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-foreground flex items-center">
                    <MessageCircle className="mr-1.5 text-primary h-4 w-4" />
                    Ulasan Pelanggan
                </h2>
                <Badge variant="secondary" className="text-xs font-medium">
                    {reviews.length} Ulasan
                </Badge>
            </div>

            {/* Compact review form */}
            <div className="bg-card p-2 rounded-lg border border-border mb-4">
                <form
                    onSubmit={handleSubmit}
                    className="flex items-center gap-2"
                >
                    <Textarea
                        value={reviewText}
                        onChange={(e) => setReviewText(e.target.value)}
                        placeholder="Tulis ulasan Anda di sini..."
                        className="min-h-[36px] h-9 py-1.5 text-sm resize-none flex-1"
                    />
                    <Button
                        type="submit"
                        className="bg-primary hover:bg-primary/90 h-8 text-xs px-2 shrink-0"
                        disabled={isSubmitting || !reviewText.trim()}
                    >
                        <Send className="h-3 w-3" />
                        <span className="sr-only">Kirim</span>
                    </Button>
                </form>
            </div>

            {/* Compact reviews list */}
            {reviews.length > 0 ? (
                <div className="space-y-3">
                    {reviews.map((review) => (
                        <Card
                            key={review.id}
                            className="overflow-hidden bg-card shadow-none border p-4"
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
                                                <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                                                    {formatTimeAgo(
                                                        review.created_at
                                                    )}
                                                </span>
                                            </div>

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
                                                                )?.rating || 0;
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
