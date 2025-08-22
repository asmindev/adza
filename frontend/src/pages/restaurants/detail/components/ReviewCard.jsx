import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Star, ThumbsUp } from "lucide-react";

export default function ReviewCard({ review }) {
    const renderStars = (rating) => {
        return Array.from({ length: 5 }, (_, i) => (
            <Star
                key={i}
                className={`w-3 h-3 ${
                    i < rating
                        ? "fill-yellow-400 text-yellow-400"
                        : "text-gray-300"
                }`}
            />
        ));
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString("id-ID", {
            day: "numeric",
            month: "short",
            year: "numeric",
        });
    };

    return (
        <Card className="border-0 border-b border-gray-100 rounded-none pb-4 mb-4 last:border-b-0 last:mb-0">
            <CardContent className="p-0">
                <div className="flex gap-3">
                    {/* Avatar */}
                    <Avatar className="w-10 h-10 flex-shrink-0">
                        <AvatarFallback className="bg-blue-100 text-blue-600 text-sm font-medium">
                            {review.userName?.charAt(0)?.toUpperCase() || "U"}
                        </AvatarFallback>
                    </Avatar>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                        {/* Header */}
                        <div className="flex items-start justify-between mb-2">
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <h4 className="text-sm font-medium text-gray-900 truncate">
                                        {review.userName || "Anonymous"}
                                    </h4>
                                    {review.isVerified && (
                                        <Badge
                                            variant="secondary"
                                            className="text-xs px-1.5 py-0.5"
                                        >
                                            Verified
                                        </Badge>
                                    )}
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="flex items-center gap-1">
                                        {renderStars(review.rating)}
                                    </div>
                                    <span className="text-xs text-gray-500">
                                        {formatDate(review.createdAt)}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Review Text */}
                        <p className="text-sm text-gray-700 leading-relaxed mb-3">
                            {review.comment}
                        </p>

                        {/* Food Name */}
                        {review.foodName && (
                            <div className="mb-2">
                                <Badge variant="outline" className="text-xs">
                                    {review.foodName}
                                </Badge>
                            </div>
                        )}

                        {/* Actions */}
                        <div className="flex items-center gap-4">
                            <button className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 transition-colors">
                                <ThumbsUp className="w-3 h-3" />
                                <span>Helpful</span>
                                {review.helpfulCount > 0 && (
                                    <span className="text-gray-400">
                                        ({review.helpfulCount})
                                    </span>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
