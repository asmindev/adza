import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router";
import { toast } from "sonner";
import {
    ArrowLeft,
    Edit,
    Trash2,
    Star,
    Users,
    TrendingUp,
    DollarSign,
    MapPin,
    Utensils,
    Award,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import apiService from "@/pages/detail/components/lib/api";

export default function FoodDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [food, setFood] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchFoodDetail = useCallback(async () => {
        try {
            setLoading(true);
            const response = await apiService.foods.getById(id);
            if (!response.data?.error) {
                console.log(response.data.data);
                setFood(response.data.data);
            } else {
                toast.error("Failed to load food details");
            }
        } catch (err) {
            console.error("Error fetching food:", err);
            toast.error("Failed to load food details");
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchFoodDetail();
    }, [fetchFoodDetail]);

    const handleEdit = () => {
        navigate(`/dashboard/foods/${id}/edit`);
    };

    const handleDelete = async () => {
        if (window.confirm("Are you sure you want to delete this food item?")) {
            try {
                const response = await apiService.foods.delete(id);
                if (response.data?.success) {
                    toast.success("Food deleted successfully");
                    navigate("/dashboard/foods");
                }
            } catch (err) {
                console.error("Error deleting food:", err);
                toast.error("Failed to delete food");
            }
        }
    };

    if (loading) {
        return <LoadingSkeleton />;
    }

    if (!food) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px]">
                <p className="text-muted-foreground">Food not found</p>
                <Button
                    onClick={() => navigate("/dashboard/foods")}
                    className="mt-4"
                >
                    Back to Foods
                </Button>
            </div>
        );
    }

    const ratingDetails = food.rating_details || {};
    const criteriaBreakdown = ratingDetails.criteria_breakdown || {};
    const ratingDistribution = ratingDetails.rating_distribution || {};

    return (
        <div className="container mx-auto py-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => navigate("/dashboard/foods")}
                    >
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold">{food.name}</h1>
                        <p className="text-muted-foreground mt-1">
                            {food.restaurant?.name || "No restaurant"}
                        </p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button onClick={handleEdit} variant="outline">
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                    </Button>
                    <Button onClick={handleDelete} variant="destructive">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content - Left Side */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Images */}
                    <Card>
                        <CardContent className="p-6">
                            {food.images && food.images.length > 0 ? (
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                    {food.images.map((image, index) => (
                                        <div
                                            key={image.id || index}
                                            className="relative aspect-square rounded-lg overflow-hidden"
                                        >
                                            <img
                                                src={
                                                    image.image_url || image.url
                                                }
                                                alt={`${food.name} - ${
                                                    index + 1
                                                }`}
                                                className="w-full h-full object-cover"
                                            />
                                            {image.is_main && (
                                                <Badge className="absolute top-2 left-2">
                                                    Main
                                                </Badge>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="flex items-center justify-center h-48 bg-muted rounded-lg">
                                    <p className="text-muted-foreground">
                                        No images available
                                    </p>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Description */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Description</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground">
                                {food.description || "No description available"}
                            </p>
                        </CardContent>
                    </Card>

                    {/* Rating Details - Admin Only */}
                    {ratingDetails && ratingDetails.total_ratings > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Award className="h-5 w-5" />
                                    Rating Details (Admin Only)
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {/* Overall Summary */}
                                <div className="bg-muted/50 p-4 rounded-lg">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground mb-1">
                                                Total Ratings
                                            </p>
                                            <p className="text-2xl font-bold">
                                                {ratingDetails.total_ratings}
                                            </p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground mb-1">
                                                Average Overall
                                            </p>
                                            <div className="flex items-center justify-center gap-1">
                                                <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                                                <p className="text-2xl font-bold">
                                                    {ratingDetails.average_overall?.toFixed(
                                                        2
                                                    ) || "0.00"}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground mb-1">
                                                Highest Rating
                                            </p>
                                            <div className="flex items-center justify-center gap-1">
                                                <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                                                <p className="text-2xl font-bold">
                                                    5.00
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground mb-1">
                                                Lowest Rating
                                            </p>
                                            <div className="flex items-center justify-center gap-1">
                                                <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                                                <p className="text-2xl font-bold">
                                                    1.00
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <Separator />

                                {/* Criteria Breakdown */}
                                <div>
                                    <h3 className="font-semibold mb-4">
                                        Criteria Breakdown
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <CriteriaCard
                                            icon={
                                                <Utensils className="h-5 w-5" />
                                            }
                                            title="Flavor"
                                            rating={
                                                criteriaBreakdown.flavor
                                                    ?.average || 0
                                            }
                                            count={
                                                criteriaBreakdown.flavor
                                                    ?.count || 0
                                            }
                                            color="text-orange-500"
                                        />
                                        <CriteriaCard
                                            icon={<Users className="h-5 w-5" />}
                                            title="Serving"
                                            rating={
                                                criteriaBreakdown.serving
                                                    ?.average || 0
                                            }
                                            count={
                                                criteriaBreakdown.serving
                                                    ?.count || 0
                                            }
                                            color="text-blue-500"
                                        />
                                        <CriteriaCard
                                            icon={
                                                <DollarSign className="h-5 w-5" />
                                            }
                                            title="Price"
                                            rating={
                                                criteriaBreakdown.price
                                                    ?.average || 0
                                            }
                                            count={
                                                criteriaBreakdown.price
                                                    ?.count || 0
                                            }
                                            color="text-green-500"
                                        />
                                        <CriteriaCard
                                            icon={
                                                <MapPin className="h-5 w-5" />
                                            }
                                            title="Place"
                                            rating={
                                                criteriaBreakdown.place
                                                    ?.average || 0
                                            }
                                            count={
                                                criteriaBreakdown.place
                                                    ?.count || 0
                                            }
                                            color="text-purple-500"
                                        />
                                    </div>
                                </div>

                                <Separator />

                                {/* Rating Distribution */}
                                <div>
                                    <h3 className="font-semibold mb-4">
                                        Rating Distribution
                                    </h3>
                                    <div className="space-y-3">
                                        {[5, 4, 3, 2, 1].map((star) => {
                                            const count =
                                                ratingDistribution[star] || 0;
                                            const percentage =
                                                ratingDetails.total_ratings > 0
                                                    ? (count /
                                                          ratingDetails.total_ratings) *
                                                      100
                                                    : 0;

                                            return (
                                                <div
                                                    key={star}
                                                    className="flex items-center gap-3"
                                                >
                                                    <div className="flex items-center gap-1 w-16">
                                                        <span className="text-sm font-medium">
                                                            {star}
                                                        </span>
                                                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                                                    </div>
                                                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-yellow-400 transition-all"
                                                            style={{
                                                                width: `${percentage}%`,
                                                            }}
                                                        />
                                                    </div>
                                                    <span className="text-sm text-muted-foreground w-16 text-right">
                                                        {count} (
                                                        {percentage.toFixed(0)}
                                                        %)
                                                    </span>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* All Individual Ratings - Admin Only */}
                    {food.ratings?.data && food.ratings.data.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <TrendingUp className="h-5 w-5" />
                                    All User Ratings ({food.ratings.data.length}
                                    )
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {food.ratings.data.map((rating, index) => (
                                        <div
                                            key={rating.id || index}
                                            className="border rounded-lg p-4 space-y-3"
                                        >
                                            <div className="flex items-start justify-between">
                                                <div>
                                                    <p className="font-medium">
                                                        {rating.user?.name ||
                                                            "Anonymous User"}
                                                    </p>
                                                    <p className="text-sm text-muted-foreground">
                                                        {rating.created_at
                                                            ? new Date(
                                                                  rating.created_at
                                                              ).toLocaleString()
                                                            : "N/A"}
                                                    </p>
                                                </div>
                                                <div className="flex items-center gap-1 bg-yellow-50 px-3 py-1 rounded-full">
                                                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                                                    <span className="font-bold">
                                                        {rating.rating?.toFixed(
                                                            2
                                                        ) || "N/A"}
                                                    </span>
                                                </div>
                                            </div>

                                            {rating.rating_details && (
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 pt-2 border-t">
                                                    <div className="flex items-center gap-2">
                                                        <Utensils className="h-4 w-4 text-orange-500" />
                                                        <div>
                                                            <p className="text-xs text-muted-foreground">
                                                                Flavor
                                                            </p>
                                                            <p className="text-sm font-medium">
                                                                {rating.rating_details.flavor?.toFixed(
                                                                    1
                                                                ) || "N/A"}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <Users className="h-4 w-4 text-blue-500" />
                                                        <div>
                                                            <p className="text-xs text-muted-foreground">
                                                                Serving
                                                            </p>
                                                            <p className="text-sm font-medium">
                                                                {rating.rating_details.serving?.toFixed(
                                                                    1
                                                                ) || "N/A"}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <DollarSign className="h-4 w-4 text-green-500" />
                                                        <div>
                                                            <p className="text-xs text-muted-foreground">
                                                                Price
                                                            </p>
                                                            <p className="text-sm font-medium">
                                                                {rating.rating_details.price?.toFixed(
                                                                    1
                                                                ) || "N/A"}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <MapPin className="h-4 w-4 text-purple-500" />
                                                        <div>
                                                            <p className="text-xs text-muted-foreground">
                                                                Place
                                                            </p>
                                                            <p className="text-sm font-medium">
                                                                {rating.rating_details.place?.toFixed(
                                                                    1
                                                                ) || "N/A"}
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Reviews */}
                    {food.reviews && food.reviews.review_count > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>
                                    Reviews ({food.reviews.review_count})
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {food.reviews.data
                                        .slice(0, 5)
                                        .map((review) => (
                                            <div
                                                key={review.id}
                                                className="border-b last:border-0 pb-4 last:pb-0"
                                            >
                                                <div className="flex items-start justify-between mb-2">
                                                    <div>
                                                        <p className="font-medium">
                                                            {review.user
                                                                ?.name ||
                                                                "Anonymous"}
                                                        </p>
                                                        <p className="text-sm text-muted-foreground">
                                                            {new Date(
                                                                review.created_at
                                                            ).toLocaleDateString()}
                                                        </p>
                                                    </div>
                                                    <div className="flex items-center gap-1">
                                                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                                                        <span className="text-sm font-medium">
                                                            {review.rating ||
                                                                "N/A"}
                                                        </span>
                                                    </div>
                                                </div>
                                                <p className="text-sm text-muted-foreground">
                                                    {review.comment ||
                                                        "No comment"}
                                                </p>
                                            </div>
                                        ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Sidebar - Right Side */}
                <div className="space-y-6">
                    {/* Quick Stats */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Quick Stats</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-muted-foreground">
                                    Price
                                </span>
                                <span className="font-semibold">
                                    Rp{" "}
                                    {food.price?.toLocaleString("id-ID") || "0"}
                                </span>
                            </div>
                            <Separator />
                            <div className="flex items-center justify-between">
                                <span className="text-muted-foreground">
                                    Average Rating
                                </span>
                                <div className="flex items-center gap-1">
                                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                                    <span className="font-semibold">
                                        {food.ratings?.average?.toFixed(2) ||
                                            "0.00"}
                                    </span>
                                </div>
                            </div>
                            <Separator />
                            <div className="flex items-center justify-between">
                                <span className="text-muted-foreground">
                                    Total Ratings
                                </span>
                                <span className="font-semibold">
                                    {ratingDetails.total_ratings ||
                                        food.ratings?.count ||
                                        0}
                                </span>
                            </div>
                            <Separator />
                            <div className="flex items-center justify-between">
                                <span className="text-muted-foreground">
                                    Reviews
                                </span>
                                <span className="font-semibold">
                                    {food.reviews?.review_count || 0}
                                </span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Restaurant Info */}
                    {food.restaurant && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Restaurant</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div>
                                    <p className="font-medium">
                                        {food.restaurant.name}
                                    </p>
                                    {food.restaurant.address && (
                                        <p className="text-sm text-muted-foreground mt-1">
                                            {food.restaurant.address}
                                        </p>
                                    )}
                                </div>
                                {food.category && (
                                    <>
                                        <Separator />
                                        <div>
                                            <p className="text-sm text-muted-foreground mb-1">
                                                Category
                                            </p>
                                            <Badge variant="secondary">
                                                {food.category.name}
                                            </Badge>
                                        </div>
                                    </>
                                )}
                            </CardContent>
                        </Card>
                    )}

                    {/* Metadata */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Metadata</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3 text-sm">
                            <div>
                                <p className="text-muted-foreground">Created</p>
                                <p className="font-medium">
                                    {food.created_at
                                        ? new Date(
                                              food.created_at
                                          ).toLocaleString()
                                        : "N/A"}
                                </p>
                            </div>
                            <Separator />
                            <div>
                                <p className="text-muted-foreground">
                                    Last Updated
                                </p>
                                <p className="font-medium">
                                    {food.updated_at
                                        ? new Date(
                                              food.updated_at
                                          ).toLocaleString()
                                        : "N/A"}
                                </p>
                            </div>
                            <Separator />
                            <div>
                                <p className="text-muted-foreground">Food ID</p>
                                <p className="font-mono text-xs">{food.id}</p>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

// Criteria Card Component
function CriteriaCard({ icon, title, rating, count, color }) {
    return (
        <div className="border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
                <div className={color}>{icon}</div>
                <span className="font-medium">{title}</span>
            </div>
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="text-2xl font-bold">
                        {rating.toFixed(2)}
                    </span>
                </div>
                <span className="text-sm text-muted-foreground">
                    {count} ratings
                </span>
            </div>
        </div>
    );
}

// Loading Skeleton
function LoadingSkeleton() {
    return (
        <div className="container mx-auto py-6 space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10 rounded" />
                    <div className="space-y-2">
                        <Skeleton className="h-8 w-64" />
                        <Skeleton className="h-4 w-40" />
                    </div>
                </div>
                <div className="flex gap-2">
                    <Skeleton className="h-10 w-24" />
                    <Skeleton className="h-10 w-24" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <Card>
                        <CardContent className="p-6">
                            <Skeleton className="h-64 w-full" />
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <Skeleton className="h-6 w-32" />
                        </CardHeader>
                        <CardContent>
                            <Skeleton className="h-20 w-full" />
                        </CardContent>
                    </Card>
                </div>
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <Skeleton className="h-6 w-32" />
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
