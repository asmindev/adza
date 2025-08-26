import React from "react";
import useSWR from "swr";
import RestaurantHeader from "./components/RestaurantHeader";
import RestaurantHero from "./components/RestaurantHero";
import MenuSection from "./components/MenuSection";
import LoadingState from "./components/LoadingState";
import ErrorState from "./components/ErrorState";

export default function RestaurantDetail({ restaurantId }) {
    const { data, error, isLoading } = useSWR(
        `/api/v1/restaurants/${restaurantId}`,
        { revalidateOnFocus: false }
    );

    const restaurant = data?.data || null;

    if (isLoading) {
        return <LoadingState />;
    }

    if (error || !restaurant) {
        return <ErrorState />;
    }

    return (
        <div className="min-h-screen bg-background">
            <RestaurantHeader />

            <div className="max-w-6xl mx-auto py-4 sm:py-8 space-y-6 sm:space-y-8 px-4">
                <RestaurantHero restaurant={restaurant} />
                <MenuSection restaurant={restaurant} />
            </div>
        </div>
    );
}
