import React from "react";
import { Link } from "react-router";
import { MapPin, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function FoodInfo({ food }) {
    if (!food) return null;

    const rating = food.ratings || { average: 0, count: 0 };
    console.log("rating", rating);
    const { average: averageRating, count: ratingCount } = rating;

    // Format price to Indonesian Rupiah
    const formattedPrice = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0,
    }).format(food.price);

    return (
        <div className="w-full p-6 h-full overflow-hidden">
            <div className="flex flex-col h-full justify-between">
                <div className="flex-1 min-h-0">
                    {/* Header dengan Badge dan Price */}
                    <div className="flex justify-between items-start mb-4">
                        <Badge
                            variant="outline"
                            className="bg-primary/10 text-primary border-primary/20 font-medium px-2 py-1 flex-shrink-0"
                        >
                            {food.category}
                        </Badge>
                        <div className="flex items-center text-primary text-xl font-bold ml-2">
                            <span>{formattedPrice}</span>
                        </div>
                    </div>

                    {/* Title dan Rating */}
                    <div className="flex justify-between items-start mb-4 gap-4">
                        <div className="flex-1 min-w-0">
                            <h1 className="text-xl sm:text-2xl lg:text-3xl font-semibold sm:font-bold text-foreground break-words">
                                {food.name}
                            </h1>
                        </div>
                        <div className="flex items-center text-sm flex-shrink-0">
                            <div className="flex items-center space-x-1">
                                <Star
                                    className={`w-4 h-4 ${
                                        averageRating > 0
                                            ? "text-yellow-400 fill-yellow-400"
                                            : "text-muted-foreground/30"
                                    }`}
                                />
                                <span className="text-muted-foreground">
                                    {averageRating.toFixed(1)}
                                </span>
                                {ratingCount > 0 && (
                                    <span className="text-muted-foreground">
                                        ({ratingCount})
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Restaurant Information */}
                    {food.restaurant && (
                        <div className="mb-4 p-3 bg-muted/30 rounded-lg">
                            <div className="flex gap-2 text-sm text-muted-foreground">
                                <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
                                <div className="min-w-0 flex-1">
                                    <p className="font-medium text-foreground break-words">
                                        {food.restaurant.name}
                                    </p>
                                    <p className="text-xs break-words">
                                        {food.restaurant.address}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Description */}
                    <p className="text-muted-foreground mb-4 break-words overflow-hidden">
                        {food.description}
                    </p>
                </div>

                {/* Button - Fixed at bottom */}
                <div className="mt-4 flex-shrink-0">
                    <Link to={`/navigation/food/${food.id}`}>
                        <Button className="w-full">
                            <MapPin className="mr-2 h-4 w-4" />
                            Lihat Lokasi & Rute
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
}
