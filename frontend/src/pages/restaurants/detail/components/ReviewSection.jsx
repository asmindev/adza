import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

function ReviewSection({ showReviews, reviews }) {
    return (
        <AnimatePresence>
            {showReviews && reviews?.data && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{
                        duration: 0.3,
                        ease: "easeInOut",
                        height: { duration: 0.3 },
                        opacity: { duration: 0.2 },
                    }}
                    className="border-t bg-muted/30 overflow-hidden"
                >
                    <div className="p-3 sm:p-4">
                        <h4 className="font-semibold text-foreground mb-3 text-sm">
                            Reviews ({reviews.review_count})
                        </h4>
                        <div className="space-y-3 max-h-60 sm:max-h-48 overflow-y-auto">
                            {reviews.data.map((review) => (
                                <Card key={review.id} className="p-3 shadow-sm">
                                    <div className="flex items-start gap-3 sm:gap-2">
                                        <Avatar className="h-8 w-8 sm:h-6 sm:w-6">
                                            <AvatarFallback className="text-sm sm:text-xs">
                                                {review.user?.name?.charAt(0) ||
                                                    "U"}
                                            </AvatarFallback>
                                        </Avatar>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 mb-2">
                                                <span className="font-medium text-sm sm:text-xs text-foreground">
                                                    {review.user?.name ||
                                                        "Anonymous"}
                                                </span>
                                                <span className="text-xs text-muted-foreground">
                                                    {new Date(
                                                        review.created_at
                                                    ).toLocaleDateString(
                                                        "id-ID"
                                                    )}
                                                </span>
                                            </div>
                                            <p className="text-muted-foreground text-sm sm:text-xs leading-relaxed">
                                                {review.content}
                                            </p>
                                        </div>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

export default ReviewSection;
