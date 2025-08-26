import React, { useEffect, useState, useContext } from "react";
import { Link, useNavigate } from "react-router";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import useSWR from "swr";

// Import our component files
import FoodGallery from "./FoodGallery";
import FoodInfo from "./FoodInfo";
import FoodReviews from "./FoodReviews";
import { UserContext } from "@/contexts/UserContextDefinition";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

export default function FoodDetail({ foodId }) {
    console.log("Rendering FoodDetail for foodId:", foodId);
    const { user: currentUser } = useContext(UserContext);
    const navigate = useNavigate();
    const [isFavorite, setIsFavorite] = useState(false);

    // Use SWR for food data fetching
    const {
        data,
        error,
        isLoading,
        mutate: revalidateFood,
    } = useSWR(`/api/v1/foods/${foodId}`, {
        onSuccess: (data) => {
            // Set favorite status based on user data
            if (currentUser && data?.data?.is_favorite) {
                setIsFavorite(data.data.is_favorite);
            }
        },
        revalidateOnFocus: false,
    });

    const food = data?.data || null;

    // Extract reviews from food data
    const reviews = food?.reviews?.data || [];

    // Scroll to top when component mounts or foodId changes
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [foodId]);

    // Handle error state
    if (error) {
        return (
            <div className="max-w-6xl mx-auto p-4 text-center">
                <motion.div
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-10"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h2 className="text-2xl font-bold text-foreground mb-4">
                        Gagal Memuat Makanan
                    </h2>
                    <p className="text-muted-foreground mb-6">
                        {error.message ||
                            "Kami tidak dapat memuat detail makanan. Silakan coba lagi nanti."}
                    </p>
                    <div className="flex justify-center gap-4">
                        <button
                            onClick={() => navigate(-1)}
                            className="inline-flex items-center px-4 py-2"
                        >
                            <ArrowLeft size={18} className="mr-2" />
                            <span>Kembali ke Makanan</span>
                        </button>
                        <button
                            onClick={() => revalidateFood()}
                            className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                        >
                            Coba Lagi
                        </button>
                    </div>
                </motion.div>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="max-w-6xl mx-auto p-4">
                <motion.div
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 overflow-hidden"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                >
                    <div className="flex space-x-4 mb-8">
                        <Skeleton className="h-[400px] w-2/3 rounded-xl" />
                        <div className="w-1/3 space-y-4">
                            <Skeleton className="h-10 w-full rounded-lg" />
                            <Skeleton className="h-6 w-3/4 rounded-lg" />
                            <Skeleton className="h-28 w-full rounded-lg" />
                            <Skeleton className="h-10 w-1/2 rounded-lg" />
                            <div className="flex space-x-2">
                                <Skeleton className="h-8 w-8 rounded-full" />
                                <Skeleton className="h-8 w-8 rounded-full" />
                                <Skeleton className="h-8 w-8 rounded-full" />
                            </div>
                        </div>
                    </div>
                    <div className="space-y-4">
                        <Skeleton className="h-10 w-full rounded-lg" />
                        <Skeleton className="h-40 w-full rounded-lg" />
                    </div>
                </motion.div>
            </div>
        );
    }

    if (!food) {
        return (
            <div className="max-w-6xl mx-auto p-4 text-center">
                <motion.div
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-10"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h2 className="text-2xl font-bold text-foreground mb-4">
                        Makanan Tidak Ditemukan
                    </h2>
                    <p className="text-muted-foreground mb-6">
                        Kami tidak dapat menemukan makanan yang Anda cari.
                        Mungkin telah dipindahkan atau dihapus.
                    </p>
                    <button
                        onClick={() => navigate(-1)}
                        className="inline-flex items-center px-4 py-2"
                    >
                        <ArrowLeft size={18} className="mr-2" />
                        <span>Kembali ke Makanan</span>
                    </button>
                </motion.div>
            </div>
        );
    }

    // Get all images - prioritize main image first
    const images = food?.images || [];
    const sortedImages = [...images].sort((a, b) => {
        if (a.is_main && !b.is_main) return -1;
        if (!a.is_main && b.is_main) return 1;
        return 0;
    });

    return (
        <div className="max-w-6xl mx-auto px-2 sm:p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <button
                    onClick={() => navigate(-1)}
                    className="inline-flex items-center sm:px-4 sm:py-2 sm:mb-6 mt-4 sm:mt-0"
                >
                    <ArrowLeft size={18} className="mr-1" />
                    <span>Kembali ke Makanan</span>
                </button>

                <Card className="overflow-hidden shadow-none">
                    <div className="flex flex-col md:flex-row">
                        {/* Image Gallery */}
                        <div className="w-full md:w-3/5 p-4 rounded-2xl overflow-hidden">
                            <FoodGallery images={sortedImages} />
                        </div>

                        {/* Food Information with Rating */}
                        <div className="w-full md:w-2/5">
                            <FoodInfo
                                food={food}
                                isFavorite={isFavorite}
                                onToggleFavorite={() => {}}
                            />
                        </div>
                    </div>

                    <div className="p-6 border-t border-border">
                        {/* Reviews section */}
                        <FoodReviews
                            reviews={reviews}
                            foodId={foodId}
                            foodRatings={food?.ratings}
                        />
                    </div>
                </Card>
            </motion.div>
        </div>
    );
}
