import React, { useEffect, useState, useContext } from "react";
import { Link } from "react-router";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import useSWR, { mutate } from "swr";
import { toast } from "sonner";

// Import our component files
import FoodGallery from "./FoodGallery";
import FoodInfo from "./FoodInfo";
import FoodRating from "./FoodRating";
import FoodReviews from "./FoodReviews";
import { UserContext } from "@/contexts/UserContextDefinition";
import { useRateFood, useSubmitReview, useToggleFavorite } from "@/lib/api";

export default function FoodDetail({ foodId, onRateFood }) {
    console.log("Rendering FoodDetail for foodId:", foodId);
    const { user: currentUser } = useContext(UserContext);
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

    // SWR mutations
    const { trigger: rateFoodMutation, isMutating: isRating } =
        useRateFood(foodId);
    const { trigger: submitReviewMutation, isMutating: isReviewing } =
        useSubmitReview(foodId);
    const { trigger: toggleFavoriteMutation, isMutating: isTogglingFavorite } =
        useToggleFavorite(foodId);

    const food = data?.data || null;

    // Extract reviews from food data
    const reviews = food?.reviews?.data || [];

    // Scroll to top when component mounts or foodId changes
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [foodId]);

    const handleToggleFavorite = async () => {
        if (!currentUser) {
            toast.error("Autentikasi Diperlukan", {
                description:
                    "Silakan masuk untuk menambahkan makanan ini ke favorit",
            });
            return;
        }

        // Optimistic UI update
        setIsFavorite((prevState) => !prevState);

        try {
            // Use SWR mutation instead of direct fetch
            await toggleFavoriteMutation({ is_favorite: !isFavorite });

            toast.success(
                isFavorite ? "Dihapus dari favorit" : "Ditambahkan ke favorit"
            );

            // Revalidate food data and global food list
            revalidateFood();
            mutate("/api/v1/foods");
        } catch (error) {
            console.error("Error updating favorite:", error);
            // Revert on error
            setIsFavorite((prevState) => !prevState);
            toast.error("Gagal memperbarui favorit", {
                description: error.message || "Silakan coba lagi nanti",
            });
        }
    };

    const handleRateFood = async (ratingData) => {
        if (!currentUser) {
            toast.error("Silakan masuk untuk memberikan penilaian", {
                description: "Anda harus masuk untuk menilai makanan ini.",
            });
            return false;
        }

        try {
            // Use SWR mutation instead of direct fetch
            await rateFoodMutation(ratingData);

            toast.success("Penilaian berhasil dikirim");

            // Revalidate food data
            revalidateFood();

            return true;
        } catch (error) {
            console.error("Error rating food:", error);
            toast.error("Gagal mengirim penilaian", {
                description: error.message || "Silakan coba lagi nanti",
            });
            return false;
        }
    };

    const handleSubmitReview = async (reviewData) => {
        if (!currentUser) {
            toast.error("Silakan masuk untuk mengirim ulasan", {
                description: "Anda harus masuk untuk mengulas makanan ini.",
            });
            return false;
        }

        try {
            // Use SWR mutation instead of direct fetch
            await submitReviewMutation(reviewData);

            toast.success("Ulasan berhasil dikirim");

            // Revalidate food data
            revalidateFood();

            return true;
        } catch (error) {
            console.error("Error submitting review:", error);
            toast.error("Gagal mengirim ulasan", {
                description: error.message || "Silakan coba lagi nanti",
            });
            return false;
        }
    };

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
                        <Link
                            to="/"
                            className="inline-flex items-center px-4 py-2 bg-accent text-accent-foreground rounded-md hover:bg-accent/90 transition-colors"
                        >
                            <ArrowLeft size={18} className="mr-2" />
                            Kembali ke Makanan
                        </Link>
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
                    <Link
                        to="/"
                        className="inline-flex items-center px-4 py-2 bg-accent text-accent-foreground rounded-md hover:bg-accent/90 transition-colors"
                    >
                        <ArrowLeft size={18} className="mr-2" />
                        Kembali ke Makanan
                    </Link>
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

    // Get average rating and user rating
    const averageRating = food?.ratings?.average || 0;
    const ratingCount = food?.ratings?.count || 0;
    const userRating = food?.ratings?.user_rating || 0;

    return (
        <div className="max-w-6xl mx-auto sm:p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="mb-6"
            >
                <Link
                    to="/"
                    className="inline-flex items-center text-accent hover:text-accent/90 mb-6 transition-colors"
                >
                    <ArrowLeft size={18} className="mr-1" />
                    <span>Kembali ke Makanan</span>
                </Link>

                <div className="bg-card text-card-foreground rounded-xl shadow-lg overflow-hidden">
                    <div className="flex flex-col md:flex-row">
                        {/* Image Gallery */}
                        <div className="w-full md:w-3/5">
                            <FoodGallery images={sortedImages} />
                        </div>

                        {/* Food Information with Rating */}
                        <div className="w-full md:w-2/5">
                            <FoodInfo
                                food={food}
                                isFavorite={isFavorite}
                                onToggleFavorite={handleToggleFavorite}
                            />

                            {/* Rating component */}
                            <div className="px-6 pb-6">
                                <FoodRating
                                    averageRating={averageRating}
                                    ratingCount={ratingCount}
                                    onRateFood={handleRateFood}
                                    foodId={foodId}
                                    initialRating={userRating}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="p-6 border-t border-border">
                        {/* Reviews section */}
                        <FoodReviews
                            reviews={reviews}
                            onSubmitReview={handleSubmitReview}
                            foodId={foodId}
                            foodRatings={food?.ratings}
                        />
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
