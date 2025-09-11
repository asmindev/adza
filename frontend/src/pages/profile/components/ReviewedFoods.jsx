import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MessageSquare, Clock, Star, ThumbsUp, Eye, Quote } from "lucide-react";
import { formatDate, truncateText } from "../utils/profile.utils";
import { useState } from "react";
import { Link } from "react-router";

export const ReviewedFoods = ({ reviews = [], showAll = false }) => {
    const [expanded, setExpanded] = useState(showAll);
    const displayReviews = expanded ? reviews : reviews.slice(0, 3);
    const hasMore = reviews.length > 3;

    if (reviews.length === 0) {
        return (
            <Card>
                <CardHeader className="pb-4">
                    <CardTitle className="text-lg font-semibold flex items-center gap-2">
                        <MessageSquare className="w-5 h-5 text-primary" />
                        Review Makanan
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8 text-muted-foreground">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full border flex items-center justify-center">
                            <MessageSquare className="w-8 h-8 opacity-50" />
                        </div>
                        <p className="font-medium">Belum ada review makanan</p>
                        <p className="text-sm mt-1">
                            Bagikan pengalaman Anda tentang makanan
                        </p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-semibold flex items-center gap-2">
                        <MessageSquare className="w-5 h-5 text-primary" />
                        Review Makanan
                        <Badge variant="secondary" className="ml-2">
                            {reviews.length}
                        </Badge>
                    </CardTitle>
                    {!showAll && hasMore && !expanded && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setExpanded(true)}
                            className="text-xs"
                        >
                            <Eye className="w-3 h-3 mr-1" />
                            Lihat Semua
                        </Button>
                    )}
                </div>
            </CardHeader>
            <CardContent className="pt-0">
                <div className="space-y-4">
                    {displayReviews.map((review) => (
                        <Link
                            to={`/food/${review.food?.id}`}
                            key={review.id}
                            className="p-4 border rounded-lg hover:bg-accent transition-colors block w-full"
                        >
                            <Quote className="w-4 h-4 text-muted-foreground opacity-50 mb-2" />

                            <div className="flex items-start justify-between mb-3">
                                <div className="flex-1">
                                    <h4 className="font-semibold text-foreground">
                                        {review.food?.name ||
                                            "Makanan Tidak Diketahui"}
                                    </h4>

                                    {review.food?.restaurant && (
                                        <p className="text-sm text-muted-foreground mt-1">
                                            📍 {review.food.restaurant.name}
                                        </p>
                                    )}
                                </div>

                                {review.rating && (
                                    <div className="flex items-center gap-1 bg-accent px-2 py-1 rounded-full">
                                        <Star className="w-3 h-3 text-primary fill-current" />
                                        <span className="text-sm font-medium">
                                            {review.rating}
                                        </span>
                                    </div>
                                )}
                            </div>

                            {review.comment && (
                                <div className="mb-4">
                                    <div className="bg-muted rounded-lg p-3 border-l-4 border-primary/20">
                                        <p className="text-sm text-foreground italic">
                                            "{truncateText(review.comment, 150)}
                                            "
                                        </p>
                                    </div>
                                </div>
                            )}

                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    {review.helpful_count > 0 && (
                                        <div className="flex items-center gap-1 bg-accent px-2 py-1 rounded-full">
                                            <ThumbsUp className="w-3 h-3 text-primary" />
                                            <span className="text-xs font-medium">
                                                {review.helpful_count} helpful
                                            </span>
                                        </div>
                                    )}
                                </div>

                                {review.created_at && (
                                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                        <Clock className="w-3 h-3" />
                                        <span>
                                            {formatDate(review.created_at)}
                                        </span>
                                    </div>
                                )}
                            </div>
                        </Link>
                    ))}
                </div>

                {!showAll && hasMore && expanded && (
                    <div className="mt-4 text-center">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setExpanded(false)}
                            className="text-xs"
                        >
                            Tampilkan Lebih Sedikit
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};
