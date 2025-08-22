import React from "react";
import { Link } from "react-router";
import {
    Heart,
    Share2,
    Clock,
    DollarSign,
    ThumbsUp,
    Bookmark,
    Utensils,
    MapPin,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function FoodInfo({ food, isFavorite, onToggleFavorite }) {
    if (!food) return null;

    // Format price to Indonesian Rupiah
    const formattedPrice = new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0,
    }).format(food.price);

    return (
        <div className="w-full p-6">
            <div className="flex flex-col h-full justify-between">
                <div>
                    <div className="flex justify-between items-start mb-2">
                        <Badge
                            variant="outline"
                            className="bg-primary/10 text-primary border-primary/20 font-medium px-2 py-1"
                        >
                            {food.category}
                        </Badge>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={onToggleFavorite}
                                className="p-2 bg-background hover:bg-muted rounded-full transition-colors"
                                aria-label={
                                    isFavorite
                                        ? "Hapus dari favorit"
                                        : "Tambahkan ke favorit"
                                }
                            >
                                <Heart
                                    className={cn(
                                        "h-5 w-5",
                                        isFavorite
                                            ? "fill-destructive text-destructive"
                                            : "text-muted-foreground"
                                    )}
                                />
                            </button>
                            <button
                                className="p-2 bg-background hover:bg-muted rounded-full transition-colors"
                                aria-label="Bagikan"
                            >
                                <Share2 className="h-5 w-5 text-muted-foreground" />
                            </button>
                        </div>
                    </div>

                    <h1 className="text-3xl font-bold text-foreground mb-2">
                        {food.name}
                    </h1>
                    {/* Restaurant Information */}
                    {food.restaurant && (
                        <div className="mb-4 bg-muted/30 rounded-lg">
                            <div className="flex gap-2 text-sm text-muted-foreground">
                                <MapPin className="size-4 mt-1" />
                                <div>
                                    <p className="font-medium text-foreground">
                                        {food.restaurant.name}
                                    </p>
                                    <p className="text-xs">
                                        {food.restaurant.address}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    <p className="text-muted-foreground mb-4">
                        {food.description}
                    </p>

                    <div className="flex items-center space-x-4 mb-6">
                        <div className="flex items-center text-primary text-xl font-bold">
                            <DollarSign className="h-5 w-5" />
                            <span>{formattedPrice}</span>
                        </div>

                        <Badge variant="secondary" className="font-medium">
                            <Clock size={14} className="mr-1" />
                            Siap dalam 30 menit
                        </Badge>
                    </div>
                </div>

                <div className="space-y-3 mt-4">
                    <Link to={`/navigation/food/${food.id}`}>
                        <Button className="w-full bg-primary hover:bg-primary/90 text-white">
                            <MapPin className="mr-2 h-4 w-4" />
                            Lihat Lokasi & Rute
                        </Button>
                    </Link>

                    <div className="flex space-x-2 mt-2">
                        <Button variant="outline" className="flex-1">
                            <ThumbsUp className="mr-2 h-4 w-4" /> Rekomendasikan
                        </Button>
                        <Button variant="outline" className="flex-1">
                            <Bookmark className="mr-2 h-4 w-4" /> Simpan
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
