import React, { useState } from "react";
import { Link } from "react-router";
import {
    ArrowLeft,
    Star,
    MapPin,
    Phone,
    Clock,
    Heart,
    Share2,
    ChefHat,
    Users,
    MessageSquare,
    Plus,
    ArrowRight,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import useSWR from "swr";

// Star Rating Component
function StarRating({ rating, showRating = true, size = "sm" }) {
    const filledStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    return (
        <div className="flex items-center gap-1">
            <div className="flex">
                {[...Array(1)].map((_, i) => (
                    <Star
                        key={i}
                        className={`${size === "sm" ? "h-4 w-4" : "h-5 w-5"} ${
                            i < filledStars
                                ? "text-yellow-400 fill-yellow-400"
                                : "text-gray-300 fill-gray-300"
                        }`}
                    />
                ))}
            </div>
            {showRating && (
                <span className="text-sm font-medium text-gray-700">
                    {rating.toFixed(1)}
                </span>
            )}
        </div>
    );
}

// Food Item Component
function FoodItem({ food, index }) {
    const [showReviews, setShowReviews] = useState(false);
    const [quantity, setQuantity] = useState(0);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
        >
            <div className="overflow-hidden border rounded-xl hover:shadow-lg transition-all duration-300 bg-white">
                <CardContent className="p-0">
                    {/* Mobile-optimized layout */}
                    <div className="p-3 sm:p-4">
                        {/* Food header - stacked on mobile */}
                        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                            {/* Food Image */}
                            {food.main_image ? (
                                <img
                                    src={food.main_image.image_url}
                                    alt={food.name}
                                    className="w-full h-32 sm:w-20 sm:h-20 object-cover rounded-lg mb-3 sm:mb-0"
                                />
                            ) : (
                                <div className="w-full h-32 sm:w-20 sm:h-20 bg-gradient-to-br from-orange-200 via-red-200 to-pink-200 rounded-lg relative overflow-hidden flex-shrink-0">
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent"></div>
                                    <div className="absolute top-2 right-2 sm:top-1 sm:right-1">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-7 w-7 sm:h-6 sm:w-6 p-0 bg-white/80 hover:bg-white rounded-full"
                                        >
                                            <Heart className="h-4 w-4 sm:h-3 sm:w-3 text-gray-600" />
                                        </Button>
                                    </div>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <ChefHat className="h-12 w-12 sm:h-8 sm:w-8 text-white/60" />
                                    </div>
                                    {/* Category badge on image for mobile */}
                                    <div className="absolute bottom-2 left-2 sm:hidden">
                                        <Badge
                                            variant="outline"
                                            className="text-xs px-2 py-1 bg-white/90"
                                        >
                                            {food.category}
                                        </Badge>
                                    </div>
                                </div>
                            )}

                            {/* Food Info */}
                            <div className="flex-1 min-w-0">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex-1 min-w-0">
                                        {/* Category badge for desktop */}
                                        <div className="hidden sm:flex items-center gap-2 mb-1">
                                            <Badge
                                                variant="outline"
                                                className="text-xs px-2 py-0.5"
                                            >
                                                {food.category}
                                            </Badge>
                                        </div>
                                        <h3 className="font-bold text-lg sm:text-base text-gray-900 leading-tight">
                                            {food.name}
                                        </h3>
                                    </div>
                                    <div className="text-right ml-2">
                                        <div className="text-xl sm:text-lg font-bold text-green-600">
                                            Rp
                                            {food.price.toLocaleString("id-ID")}
                                        </div>
                                    </div>
                                </div>

                                <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                                    {food.description}
                                </p>

                                {/* Rating and Reviews - mobile friendly */}
                                <div className="flex  sm:items-center sm:justify-between gap-2 mb-3">
                                    <div className="flex items-center gap-2">
                                        <div className="flex items-center gap-1">
                                            <StarRating
                                                rating={
                                                    food.ratings?.average || 0
                                                }
                                                showRating={false}
                                            />
                                            <span className="text-sm font-medium text-gray-700">
                                                {food.ratings?.average?.toFixed(
                                                    1
                                                ) || "0.0"}
                                            </span>
                                        </div>
                                        <span className="text-xs text-gray-500">
                                            ({food.ratings?.count || 0} rating)
                                        </span>
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() =>
                                            setShowReviews(!showReviews)
                                        }
                                        className="text-blue-600 hover:text-blue-700 text-xs h-7 px-2 self-start sm:self-auto"
                                    >
                                        <MessageSquare className="h-3 w-3 mr-1" />
                                        {food.reviews?.review_count || 0}{" "}
                                        Reviews
                                    </Button>
                                </div>
                                <Link
                                    to={`/food/${food.id}`}
                                    className="w-full flex bg-green-500 py-2 gap-2 hover:bg-green-600 text-white rounded-lg justify-center items-center text-sm font-medium transition-all duration-300 group"
                                >
                                    Lihat Detail
                                    <ArrowRight className="size-4 group-hover:translate-x-1 transition-all duration-300" />
                                </Link>
                            </div>
                        </div>
                    </div>

                    {/* Reviews Section with AnimatePresence */}
                    <AnimatePresence>
                        {showReviews && food.reviews?.data && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}
                                transition={{
                                    duration: 0.3,
                                    ease: "easeInOut",
                                    height: { duration: 0.3 },
                                    opacity: { duration: 0.2 },
                                }}
                                className="border-t bg-gray-50 overflow-hidden"
                            >
                                <div className="p-3 sm:p-4">
                                    <h4 className="font-semibold text-gray-800 mb-3 text-sm">
                                        Reviews ({food.reviews.review_count})
                                    </h4>
                                    <div className="space-y-3 max-h-60 sm:max-h-48 overflow-y-auto">
                                        {food.reviews.data.map((review) => (
                                            <div
                                                key={review.id}
                                                className="bg-white rounded-lg p-3 shadow-sm"
                                            >
                                                <div className="flex items-start gap-3 sm:gap-2">
                                                    <div className="w-8 h-8 sm:w-6 sm:h-6 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                                                        <span className="text-white text-sm sm:text-xs font-medium">
                                                            {review.user?.name?.charAt(
                                                                0
                                                            ) || "U"}
                                                        </span>
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 mb-2">
                                                            <span className="font-medium text-sm sm:text-xs text-gray-900">
                                                                {review.user
                                                                    ?.name ||
                                                                    "Anonymous"}
                                                            </span>
                                                            <span className="text-xs text-gray-400">
                                                                {new Date(
                                                                    review.created_at
                                                                ).toLocaleDateString(
                                                                    "id-ID"
                                                                )}
                                                            </span>
                                                        </div>
                                                        <p className="text-gray-700 text-sm sm:text-xs leading-relaxed">
                                                            {review.content}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </CardContent>
            </div>
        </motion.div>
    );
}

export default function RestaurantDetail({ restaurantId }) {
    const { data, error, isLoading } = useSWR(
        `/api/v1/restaurants/${restaurantId}`,
        { revalidateOnFocus: false }
    );

    const restaurant = data?.data || null;

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50">
                <div className="max-w-6xl mx-auto p-4">
                    <Skeleton className="h-8 w-32 mb-6" />
                    <Skeleton className="h-64 w-full mb-8 rounded-2xl" />
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(6)].map((_, i) => (
                            <Skeleton key={i} className="h-80 rounded-xl" />
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error || !restaurant) {
        return (
            <div className="flex items-center justify-center">
                <div className="text-center p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                        Restaurant Not Found
                    </h2>
                    <Link
                        to="/"
                        className="inline-flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Back to Home
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            {/* Mobile-first Header */}
            <div className="bg-white">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center justify-between">
                        <Link
                            to="/"
                            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
                        >
                            <ArrowLeft className="mr-2 h-5 w-5" />
                            <span className="hidden sm:inline">
                                Back to Restaurants
                            </span>
                            <span className="sm:hidden">Kembali</span>
                        </Link>
                        <div className="flex items-center gap-1 sm:gap-2">
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0"
                            >
                                <Share2 className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0"
                            >
                                <Heart className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-6xl mx-auto py-4 sm:py-8 space-y-6 sm:space-y-8">
                {/* Restaurant Hero - mobile optimized */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="overflow-hidden rounded-xl"
                >
                    <div className="h-48 sm:h-64 bg-black relative">
                        <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-6 right-4 sm:right-6 text-white">
                            <h1 className="text-2xl sm:text-4xl font-bold mb-1 sm:mb-2">
                                {restaurant.name}
                            </h1>
                            <p className="text-sm sm:text-lg opacity-90 mb-3 sm:mb-4 line-clamp-2">
                                {restaurant.description}
                            </p>
                            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                                <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm rounded-full px-3 py-1 self-start">
                                    <StarRating
                                        rating={restaurant.rating?.average || 0}
                                        showRating={false}
                                    />
                                    <span className="font-semibold text-sm sm:text-base">
                                        {restaurant.rating?.average?.toFixed(
                                            1
                                        ) || "0.0"}
                                    </span>
                                    <span className="text-xs sm:text-sm opacity-80">
                                        ({restaurant.rating?.total || 0})
                                    </span>
                                </div>
                                <Badge
                                    className={
                                        restaurant.is_active
                                            ? "bg-green-500 hover:bg-green-600"
                                            : "bg-red-500 hover:bg-red-600"
                                    }
                                >
                                    {restaurant.is_active ? "Buka" : "Tutup"}
                                </Badge>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 sm:p-5 bg-black/5">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 text-sm text-gray-600 mb-4">
                            <div className="flex items-center gap-2 bg-white/50 backdrop-blur-sm border border-black/5 rounded-xl px-3 py-2">
                                <MapPin className="h-4 w-4 text-gray-400 flex-shrink-0" />
                                <span className="line-clamp-1">
                                    {restaurant.address}
                                </span>
                            </div>
                            <div className="flex items-center gap-2 bg-white/50 backdrop-blur-sm border border-black/5 rounded-xl px-3 py-2">
                                <Phone className="h-4 w-4 text-gray-400 flex-shrink-0" />
                                <span>{restaurant.phone}</span>
                            </div>
                            <div className="flex items-center gap-2 bg-white/50 backdrop-blur-sm border border-black/5 rounded-xl px-3 py-2">
                                <Clock className="h-4 w-4 text-gray-400 flex-shrink-0" />
                                <span>09:00 - 22:00</span>
                            </div>
                        </div>

                        {/* Location Button */}
                        <Link to={`/navigation/restaurant/${restaurant.id}`}>
                            <Button className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-white">
                                <MapPin className="mr-2 h-4 w-4" />
                                Lihat Lokasi & Rute
                            </Button>
                        </Link>
                    </div>
                </motion.div>

                {/* Menu Section - mobile grid */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
                        <ChefHat className="h-5 w-5 sm:h-6 sm:w-6 text-orange-500" />
                        <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">
                            Menu
                        </h2>
                        <Badge variant="outline" className="text-xs sm:text-sm">
                            {restaurant.foods?.length || 0} items
                        </Badge>
                    </div>

                    {restaurant.foods && restaurant.foods.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                            {restaurant.foods.map((food, index) => (
                                <FoodItem
                                    key={food.id}
                                    food={food}
                                    index={index}
                                />
                            ))}
                        </div>
                    ) : (
                        <Card className="p-8 sm:p-12 text-center border-0 shadow-lg">
                            <ChefHat className="h-12 w-12 sm:h-16 sm:w-16 text-gray-400 mx-auto mb-3 sm:mb-4" />
                            <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
                                No Menu Available
                            </h3>
                            <p className="text-gray-600 text-sm sm:text-base">
                                This restaurant hasn't added any menu items yet.
                            </p>
                        </Card>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
