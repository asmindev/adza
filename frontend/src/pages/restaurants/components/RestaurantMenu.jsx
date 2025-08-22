import React from "react";
import { Utensils } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import FoodCard from "@/components/food/FoodCard";

export default function RestaurantMenu({ foods, favorites, onToggleFavorite }) {
    return (
        <Card>
            <CardContent className="p-6">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                    <Utensils className="h-6 w-6 text-primary" />
                    Menu Makanan
                </h2>

                {foods.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {foods.map((food) => (
                            <FoodCard
                                key={food.id}
                                food={food}
                                onToggleFavorite={() =>
                                    onToggleFavorite(food.id)
                                }
                                isFavorite={favorites.includes(food.id)}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <Utensils className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
                        <h3 className="text-xl font-medium text-foreground mb-2">
                            Belum Ada Menu
                        </h3>
                        <p className="text-muted-foreground">
                            Restoran ini belum menambahkan menu makanan.
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
