import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Star } from "lucide-react";
import useSWR from "swr";
import { Link } from "react-router";
import { formatTimeAgo } from "@/utils";

export default function RatedFoods({ ratings = [] }) {
    const [searchTerm, setSearchTerm] = useState("");

    // Fetch foods data to get information about the rated foods
    const { data: foodsData } = useSWR("/api/v1/foods", {
        revalidateOnFocus: false,
    });

    const foods = foodsData?.data.foods || [];

    // Find food details for each rating
    const ratedFoodsWithDetails = ratings.map((rating) => {
        const food = foods.find((f) => f.id === rating.food_id) || null;
        return {
            ...rating,
            food,
        };
    });

    // Filter the rated foods based on search term
    const filteredRatings = ratedFoodsWithDetails.filter((item) => {
        return (
            !searchTerm ||
            (item.food &&
                item.food.name &&
                item.food.name.toLowerCase().includes(searchTerm.toLowerCase()))
        );
    });

    return (
        <Card>
            <CardHeader>
                <CardTitle>My Ratings</CardTitle>
                <Input
                    placeholder="Search foods..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="mt-2"
                />
            </CardHeader>
            <CardContent>
                {filteredRatings.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                        {searchTerm
                            ? "No matching ratings found"
                            : "You haven't rated any foods yet"}
                    </div>
                ) : (
                    <div className="space-y-4">
                        {filteredRatings.map((item) => (
                            <div
                                key={item.id}
                                className="flex flex-col sm:flex-row justify-between border-b pb-4"
                            >
                                <div className="flex-1">
                                    <Link to={`/food/${item.food_id}`}>
                                        <h3 className="font-medium hover:text-primary transition-colors">
                                            {item.food
                                                ? item.food.name
                                                : `Food #${item.food_id}`}
                                        </h3>
                                    </Link>
                                    <p className="text-sm text-muted-foreground">
                                        Rated on{" "}
                                        {formatTimeAgo(item.created_at)}
                                    </p>
                                </div>
                                <div className="flex items-center mt-2 sm:mt-0">
                                    <div className="flex items-center">
                                        <Star
                                            className="text-yellow-400 fill-yellow-400"
                                            size={18}
                                        />
                                        <span className="ml-1 font-medium">
                                            {item.rating}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
