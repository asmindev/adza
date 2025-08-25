import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Star, Clock, ChefHat, Eye } from "lucide-react";
import { formatDate, formatRating } from "../utils/profile.utils";
import { useState } from "react";

export const RatedFoods = ({ foodRatings = [], showAll = false }) => {
    const [expanded, setExpanded] = useState(showAll);
    const displayRatings = expanded ? foodRatings : foodRatings.slice(0, 3);
    const hasMore = foodRatings.length > 3;

    if (foodRatings.length === 0) {
        return (
            <Card>
                <CardHeader className="pb-4">
                    <CardTitle className="text-lg font-semibold flex items-center gap-2">
                        <Star className="w-5 h-5 text-primary" />
                        Makanan yang Dinilai
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8 text-muted-foreground">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full border flex items-center justify-center">
                            <Star className="w-8 h-8 opacity-50" />
                        </div>
                        <p className="font-medium">
                            Belum ada penilaian makanan
                        </p>
                        <p className="text-sm mt-1">
                            Mulai beri rating pada makanan favorit Anda
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
                        <Star className="w-5 h-5 text-primary" />
                        Makanan yang Dinilai
                        <Badge variant="secondary" className="ml-2">
                            {foodRatings.length}
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
                <div className="space-y-3">
                    {displayRatings.map((rating) => (
                        <div
                            key={rating.id}
                            className="p-4 border rounded-lg hover:bg-accent transition-colors"
                        >
                            <div className="flex items-start gap-3">
                                {/* Food Icon */}
                                <div className="w-10 h-10 rounded-lg border flex items-center justify-center flex-shrink-0">
                                    <ChefHat className="w-5 h-5 text-muted-foreground" />
                                </div>

                                <div className="flex-1 min-w-0">
                                    <h4 className="font-semibold text-foreground">
                                        {rating.food?.name ||
                                            "Makanan Tidak Diketahui"}
                                    </h4>

                                    {rating.food?.restaurant && (
                                        <p className="text-sm text-muted-foreground mt-1">
                                            📍 {rating.food.restaurant.name}
                                        </p>
                                    )}

                                    <div className="flex items-center justify-between mt-3">
                                        <div className="flex items-center gap-2">
                                            <div className="flex items-center">
                                                {[...Array(5)].map((_, i) => (
                                                    <Star
                                                        key={i}
                                                        className={`w-4 h-4 ${
                                                            i < rating.rating
                                                                ? "text-primary fill-current"
                                                                : "text-muted-foreground"
                                                        }`}
                                                    />
                                                ))}
                                            </div>
                                            <span className="text-sm font-medium">
                                                {formatRating(rating.rating)}
                                            </span>
                                        </div>

                                        {rating.created_at && (
                                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                                <Clock className="w-3 h-3" />
                                                <span>
                                                    {formatDate(
                                                        rating.created_at
                                                    )}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
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
