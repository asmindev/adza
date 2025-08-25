import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import useSWR from "swr";
import {
    Edit,
    Settings,
    Mail,
    MapPin,
    Calendar,
    Clock,
    Shield,
    Star,
    Trophy,
    Users,
    Activity,
    TrendingUp,
    MessageCircle,
    FileText,
    CheckCircle,
    Phone,
    Code,
    Rocket,
    Loader2,
} from "lucide-react";
import ProfileInfo from "./ProfileInfo";
import RatedFoods from "./RatedFoods";
import ReviewedFoods from "./ReviewedFoods";
import { formatTimeAgo } from "@/utils";

export default function ProfilePage() {
    // Fetch current user profile data
    const {
        data: userData,
        isLoading,
        error,
        mutate,
    } = useSWR("/api/v1/me", {
        revalidateOnFocus: false,
    });

    // Show loading state
    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
                <div className="flex items-center gap-2">
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Loading profile...</span>
                </div>
            </div>
        );
    }

    // Show error state
    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-500 mb-4">Failed to load profile</p>
                    <Button onClick={() => mutate()}>Retry</Button>
                </div>
            </div>
        );
    }

    // If no user data is available
    if (!userData?.data) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-muted-foreground">
                        No profile data found
                    </p>
                </div>
            </div>
        );
    }

    const user = userData.data;
    const foodRatings = user.food_ratings || [];
    const reviews = user.reviews || [];

    // Get user initials for avatar
    const getUserInitials = (name) => {
        if (!name) return "UN";
        return name
            .split(" ")
            .map((word) => word[0])
            .join("")
            .toUpperCase()
            .slice(0, 2);
    };

    // Calculate average rating
    const averageRating =
        foodRatings.length > 0
            ? (
                  foodRatings.reduce((sum, rating) => sum + rating.rating, 0) /
                  foodRatings.length
              ).toFixed(1)
            : 0;
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
            <div className="container mx-auto px-4 py-8 max-w-7xl">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                Profile
                            </h1>
                            <p className="text-muted-foreground mt-1">
                                Manage your account and preferences
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col lg:flex-row gap-6">
                    {/* Sticky Sidebar */}
                    <div className="lg:w-80 lg:sticky lg:top-6 lg:self-start">
                        <Card>
                            <CardContent className="p-6">
                                {/* Profile Header */}
                                <div className="text-center mb-6">
                                    <div className="relative inline-block">
                                        <Avatar className="w-24 h-24 border-2 border-gray-200 dark:border-gray-700">
                                            <AvatarImage
                                                src={
                                                    user.avatar_url ||
                                                    "/avatar.png"
                                                }
                                            />
                                            <AvatarFallback className="text-xl font-semibold bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                                                {getUserInitials(user.name)}
                                            </AvatarFallback>
                                        </Avatar>
                                        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 border-2 border-white dark:border-gray-900 rounded-full"></div>
                                    </div>
                                    <div className="mt-4">
                                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                                            {user.name || user.username}
                                        </h2>
                                        <p className="text-muted-foreground flex items-center justify-center gap-1 mt-1">
                                            <Mail className="w-4 h-4" />
                                            {user.email}
                                        </p>
                                    </div>

                                    <Badge
                                        variant="secondary"
                                        className="mt-3 capitalize"
                                    >
                                        <Shield className="w-3 h-3 mr-1" />
                                        {user.role || "User"}
                                    </Badge>
                                </div>

                                <Separator className="my-6" />

                                {/* Profile Stats */}
                                <div className="space-y-4">
                                    <h3 className="font-medium text-gray-900 dark:text-white">
                                        Profile Information
                                    </h3>
                                    <div className="space-y-3 text-sm">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <Calendar className="w-4 h-4 text-muted-foreground" />
                                                <span className="text-muted-foreground">
                                                    Member since
                                                </span>
                                            </div>
                                            <span className="font-medium">
                                                {formatTimeAgo(user.created_at)}
                                            </span>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <Star className="w-4 h-4 text-muted-foreground" />
                                                <span className="text-muted-foreground">
                                                    Avg Rating
                                                </span>
                                            </div>
                                            <span className="font-medium text-yellow-600">
                                                {averageRating}/5
                                            </span>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <MessageCircle className="w-4 h-4 text-muted-foreground" />
                                                <span className="text-muted-foreground">
                                                    Total Reviews
                                                </span>
                                            </div>
                                            <span className="font-medium">
                                                {reviews.length}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Main Content */}
                    <div className="flex-1 space-y-6">
                        {/* Stats Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-800/20 rounded-lg flex items-center justify-center">
                                            <Star className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                                        </div>
                                        <div>
                                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                                {foodRatings.length}
                                            </div>
                                            <p className="text-sm text-muted-foreground">
                                                Food Ratings
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-800/20 rounded-lg flex items-center justify-center">
                                            <MessageCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                        </div>
                                        <div>
                                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                                {reviews.length}
                                            </div>
                                            <p className="text-sm text-muted-foreground">
                                                Reviews Written
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="p-6">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 bg-green-100 dark:bg-green-800/20 rounded-lg flex items-center justify-center">
                                            <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                                        </div>
                                        <div>
                                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                                {averageRating}
                                            </div>
                                            <p className="text-sm text-muted-foreground">
                                                Average Rating
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Tabs Navigation and Content */}
                        <Tabs defaultValue="profile" className="w-full">
                            <TabsList className="grid w-full grid-cols-3">
                                <TabsTrigger
                                    value="profile"
                                    className="flex items-center gap-2"
                                >
                                    <Edit className="w-4 h-4" />
                                    Profile Info
                                </TabsTrigger>
                                <TabsTrigger
                                    value="ratings"
                                    className="flex items-center gap-2"
                                >
                                    <Star className="w-4 h-4" />
                                    My Ratings
                                </TabsTrigger>
                                <TabsTrigger
                                    value="reviews"
                                    className="flex items-center gap-2"
                                >
                                    <MessageCircle className="w-4 h-4" />
                                    My Reviews
                                </TabsTrigger>
                            </TabsList>

                            <TabsContent
                                value="profile"
                                className="space-y-6 mt-6"
                            >
                                <ProfileInfo userData={user} mutate={mutate} />

                                {/* Recent Activity */}
                                <Card>
                                    <CardHeader>
                                        <div className="flex items-center gap-3">
                                            <Activity className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                                            <div>
                                                <CardTitle>
                                                    Recent Activity
                                                </CardTitle>
                                                <p className="text-sm text-muted-foreground">
                                                    Your latest ratings and
                                                    reviews
                                                </p>
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <ScrollArea className="h-[300px]">
                                            <div className="space-y-4">
                                                {/* Combine and sort recent ratings and reviews */}
                                                {[
                                                    ...foodRatings
                                                        .slice(0, 3)
                                                        .map((rating) => ({
                                                            type: "rating",
                                                            id: rating.id,
                                                            food_id:
                                                                rating.food_id,
                                                            rating: rating.rating,
                                                            created_at:
                                                                rating.created_at,
                                                        })),
                                                    ...reviews
                                                        .slice(0, 3)
                                                        .map((review) => ({
                                                            type: "review",
                                                            id: review.id,
                                                            food_id:
                                                                review.food_id,
                                                            rating: review.rating,
                                                            created_at:
                                                                review.created_at,
                                                        })),
                                                ]
                                                    .sort(
                                                        (a, b) =>
                                                            new Date(
                                                                b.created_at
                                                            ) -
                                                            new Date(
                                                                a.created_at
                                                            )
                                                    )
                                                    .slice(0, 5)
                                                    .map((activity) => (
                                                        <div
                                                            key={`${activity.type}-${activity.id}`}
                                                            className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                                                        >
                                                            {activity.type ===
                                                            "rating" ? (
                                                                <Star className="w-5 h-5 text-yellow-500 mt-0.5" />
                                                            ) : (
                                                                <MessageCircle className="w-5 h-5 text-blue-500 mt-0.5" />
                                                            )}
                                                            <div className="flex-1">
                                                                <p className="font-medium text-gray-900 dark:text-white">
                                                                    {activity.type ===
                                                                    "rating"
                                                                        ? `Rated a food ${activity.rating}/5 stars`
                                                                        : `Wrote a review with ${activity.rating}/5 stars`}
                                                                </p>
                                                                <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
                                                                    <Clock className="w-3 h-3" />
                                                                    {formatTimeAgo(
                                                                        activity.created_at
                                                                    )}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    ))}

                                                {foodRatings.length === 0 &&
                                                    reviews.length === 0 && (
                                                        <div className="text-center py-8 text-muted-foreground">
                                                            <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                                            <p>
                                                                No activity yet
                                                            </p>
                                                            <p className="text-sm">
                                                                Start rating and
                                                                reviewing foods!
                                                            </p>
                                                        </div>
                                                    )}
                                            </div>
                                        </ScrollArea>
                                    </CardContent>
                                </Card>
                            </TabsContent>

                            <TabsContent value="ratings" className="mt-6">
                                <RatedFoods ratings={foodRatings} />
                            </TabsContent>

                            <TabsContent value="reviews" className="mt-6">
                                <ReviewedFoods reviews={reviews} />
                            </TabsContent>
                        </Tabs>
                    </div>
                </div>
            </div>
        </div>
    );
}
