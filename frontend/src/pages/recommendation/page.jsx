// src/pages/Recommendation.jsx
import React, { useEffect, useState } from "react";
import useSWR from "swr";
import { apiService } from "../detail/components/lib/api";
import FoodCard from "@/components/food/FoodCard";
import { useNavigate } from "react-router";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";
import EmptyState from "./EmptyState";

export default function Recommendation() {
    const navigate = useNavigate();
    const [countdown, setCountdown] = useState(60);
    const [redirecting, setRedirecting] = useState(false);

    // Menggunakan SWR untuk mengambil data rekomendasi
    const {
        data,
        error,
        isLoading,
        mutate: refreshRecommendations,
    } = useSWR(
        "foods-recommendation",
        () => apiService.foods.getRecommendation(),
        {
            revalidateOnFocus: false,
            revalidateOnReconnect: true,
            errorRetryCount: 0,
            errorRetryInterval: 5000,
        }
    );

    const foodItems = data?.data?.data?.recommendations || data?.data || [];

    const handleRefresh = () => {
        setRedirecting(false);
        setCountdown(5);
        refreshRecommendations();
    };

    if (isLoading) {
        return <LoadingState />;
    }

    if (error) {
        return (
            <ErrorState
                error={error}
                countdown={countdown}
                redirecting={redirecting}
                handleRefresh={handleRefresh}
            />
        );
    }

    return (
        <div className="container mx-auto px-4 py-8 max-w-7xl">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">Rekomendasi</h1>
            </div>

            {foodItems.length > 0 ? (
                <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {foodItems.map((food) => (
                        <FoodCard food={food} key={food.id} />
                    ))}
                </div>
            ) : (
                <EmptyState
                    countdown={countdown}
                    redirecting={redirecting}
                    handleRefresh={handleRefresh}
                />
            )}
        </div>
    );
}
