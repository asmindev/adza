import React from "react";
import useSWR from "swr";
import { apiService } from "../../lib/api";
import FoodCard from "@/components/food/FoodCard";

export default function Popular() {
    // Menggunakan SWR untuk mengambil data rekomendasi dengan autentikasi token dari api.js
    const {
        data,
        error,
        isLoading,
        mutate: refreshRecommendations,
    } = useSWR("foods-popular", () => apiService.foods.getPopular(), {
        revalidateOnFocus: false,
        revalidateOnReconnect: true,
        errorRetryCount: 3,
        errorRetryInterval: 5000,
    });

    const handleRefresh = () => {
        refreshRecommendations();
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-[400px]">
                <div className="flex flex-col items-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                    <div className="text-lg text-gray-600">Memuat data...</div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col justify-center items-center min-h-[400px]">
                <div className="text-center max-w-md">
                    <div className="text-red-500 text-lg mb-4">
                        Gagal memuat makanan populer
                    </div>
                    <div className="text-gray-600 text-sm mb-6">
                        {error.message ||
                            "Something went wrong while fetching recommendations"}
                    </div>
                    <button
                        onClick={handleRefresh}
                        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    const foodItems = data?.data?.data || data?.data || [];

    return (
        <div className="container mx-auto px-4 py-8 max-w-7xl">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Makanan Popular</h1>
                </div>
            </div>

            {foodItems.length > 0 ? (
                <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {foodItems.map((food) => (
                        <FoodCard food={food} key={food.id} />
                    ))}
                </div>
            ) : (
                <div className="text-center py-16">
                    <div className="max-w-md mx-auto">
                        <svg
                            className="w-24 h-24 text-gray-300 mx-auto mb-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={1}
                                d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                            />
                        </svg>
                        <h3 className="text-xl font-medium text-gray-600 mb-2">
                            No recommendations available
                        </h3>
                        <p className="text-gray-500 text-sm mb-6">
                            Start rating some foods to get personalized
                            recommendations tailored to your taste!
                        </p>
                        <button
                            onClick={handleRefresh}
                            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                        >
                            Check Again
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
