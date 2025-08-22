import React, { useState } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Star } from "lucide-react";

export default function RatingForm({
    foodId,
    onSubmit,
    existingRating = null,
}) {
    const [rating, setRating] = useState(existingRating?.rating || 0);
    const [reviewTitle, setReviewTitle] = useState(
        existingRating?.review_title || ""
    );
    const [reviewText, setReviewText] = useState(existingRating?.content || "");
    const [comment, setComment] = useState(existingRating?.comment || "");
    const [hoveredRating, setHoveredRating] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (rating === 0) {
            return; // Don't submit if no rating is selected
        }

        setIsSubmitting(true);

        try {
            await onSubmit(foodId, {
                rating,
                review_title: reviewTitle,
                content: reviewText,
                comment,
            });

            // Clear form after successful submission
            if (!existingRating) {
                setRating(0);
                setReviewTitle("");
                setReviewText("");
                setComment("");
            }
        } catch (error) {
            console.error("Error submitting rating:", error);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Rate this Recipe</CardTitle>
                <CardDescription>
                    Share your experience and help others discover great recipes
                </CardDescription>
            </CardHeader>

            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">
                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="rating">Rating</Label>
                        <div className="flex space-x-1">
                            {[1, 2, 3, 4, 5].map((value) => (
                                <button
                                    key={value}
                                    type="button"
                                    onClick={() => setRating(value)}
                                    onMouseEnter={() => setHoveredRating(value)}
                                    onMouseLeave={() => setHoveredRating(0)}
                                    className="focus:outline-none"
                                >
                                    <Star
                                        className={`h-8 w-8 cursor-pointer ${
                                            value <= (hoveredRating || rating)
                                                ? "text-yellow-500 fill-yellow-500"
                                                : "text-gray-300"
                                        }`}
                                    />
                                </button>
                            ))}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                            {rating
                                ? `You rated this recipe ${rating} ${
                                      rating === 1 ? "star" : "stars"
                                  }`
                                : "Click to rate"}
                        </p>
                    </div>

                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="review-title">Review Title</Label>
                        <Input
                            id="review-title"
                            placeholder="Summarize your experience in a short title"
                            value={reviewTitle}
                            onChange={(e) => setReviewTitle(e.target.value)}
                        />
                    </div>

                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="review-text">Review</Label>
                        <Textarea
                            id="review-text"
                            placeholder="Share your experience with this recipe - what did you like or dislike?"
                            className="min-h-[100px]"
                            value={reviewText}
                            onChange={(e) => setReviewText(e.target.value)}
                        />
                    </div>

                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="comment">Short Comment</Label>
                        <Input
                            id="comment"
                            placeholder="A brief comment about the recipe"
                            value={comment}
                            onChange={(e) => setComment(e.target.value)}
                        />
                    </div>
                </CardContent>

                <CardFooter>
                    <Button
                        type="submit"
                        disabled={isSubmitting || rating === 0}
                        className="w-full sm:w-auto"
                    >
                        {isSubmitting
                            ? "Submitting..."
                            : existingRating
                            ? "Update Rating"
                            : "Submit Rating"}
                    </Button>
                </CardFooter>
            </form>
        </Card>
    );
}
