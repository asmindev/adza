import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Star, MapPin, Calendar } from "lucide-react";
import {
    getUserInitials,
    formatRating,
    formatDate,
} from "../utils/profile.utils";
import { LogoutButton } from "./LogoutButton";

export const ProfileHeader = ({ user, stats }) => {
    return (
        <Card>
            <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row items-center gap-6">
                    {/* Avatar */}
                    <div className="relative">
                        <Avatar className="w-20 h-20">
                            <AvatarImage src={user.avatar} alt={user.name} />
                            <AvatarFallback className="text-lg font-semibold">
                                {getUserInitials(user.name)}
                            </AvatarFallback>
                        </Avatar>
                    </div>

                    {/* Info */}
                    <div className="flex-1 text-center sm:text-left space-y-3">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                            <div>
                                <h1 className="text-2xl font-bold text-foreground">
                                    {user.name}
                                </h1>
                                <p className="text-muted-foreground text-sm">
                                    {user.email}
                                </p>
                            </div>
                            <div className="flex justify-center sm:justify-end">
                                <LogoutButton size="sm" />
                            </div>
                        </div>

                        {user.bio && (
                            <p className="text-sm text-muted-foreground max-w-md">
                                {user.bio}
                            </p>
                        )}

                        {/* Stats Grid */}
                        <div className="grid grid-cols-3 gap-3 mt-4">
                            <div className="text-center p-3 rounded-lg border">
                                <div className="flex items-center justify-center gap-1 mb-1">
                                    <Star className="w-4 h-4 text-primary fill-current" />
                                    <span className="text-base font-semibold">
                                        {formatRating(stats.averageRating)}
                                    </span>
                                </div>
                                <span className="text-xs text-muted-foreground">
                                    Avg Rating
                                </span>
                            </div>

                            <div className="text-center p-3 rounded-lg border">
                                <div className="text-base font-semibold mb-1">
                                    {stats.totalRatings}
                                </div>
                                <span className="text-xs text-muted-foreground">
                                    Penilaian
                                </span>
                            </div>

                            <div className="text-center p-3 rounded-lg border">
                                <div className="text-base font-semibold mb-1">
                                    {stats.totalReviews}
                                </div>
                                <span className="text-xs text-muted-foreground">
                                    Review
                                </span>
                            </div>
                        </div>

                        {user.created_at && (
                            <div className="flex items-center justify-center sm:justify-start gap-2 text-xs text-muted-foreground mt-3">
                                <Calendar className="w-3 h-3" />
                                <span>
                                    Bergabung {formatDate(user.created_at)}
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
