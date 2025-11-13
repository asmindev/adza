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

    // if (isLoading) {
    //     return <LoadingState />;
    // }

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
        <>
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 py-12">
                <div className="container mx-auto px-4">
                    <button
                        onClick={() => navigate("/")}
                        className="text-white hover:text-orange-100 mb-4 flex items-center gap-2 transition-colors"
                    >
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15 19l-7-7 7-7"
                            />
                        </svg>
                        Kembali
                    </button>
                    <h1 className="text-3xl md:text-4xl font-bold text-white">
                        Rekomendasi untuk Anda
                    </h1>
                    <p className="text-orange-100 mt-2">
                        Makanan favorit yang banyak disukai
                    </p>
                </div>
            </div>

            <div className="container mx-auto px-4 py-8 max-w-7xl">
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
        </>
    );
}
