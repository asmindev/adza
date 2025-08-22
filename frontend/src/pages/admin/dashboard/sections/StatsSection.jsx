import React from "react";
import StatsCard from "../components/StatsCard";
import { Utensils, Users, ClipboardList, Star } from "lucide-react";

export default function StatsSection({ stats }) {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatsCard
                title="Total Makanan"
                value={stats.totalFoods}
                description="Semua item makanan terdaftar"
                icon={<Utensils className="h-4 w-4 text-orange-500" />}
                trend={stats.foodsGrowth || 0}
            />
            <StatsCard
                title="Total Pengguna"
                value={stats.totalUsers}
                description="Pengguna terdaftar"
                icon={<Users className="h-4 w-4 text-blue-500" />}
                trend={stats.usersGrowth || 0}
            />
            <StatsCard
                title="Total Ulasan"
                value={stats.totalReviews}
                description="Ulasan makanan yang dikirimkan"
                icon={<ClipboardList className="h-4 w-4 text-purple-500" />}
                trend={stats.reviewsGrowth || 0}
            />
            <StatsCard
                title="Rata-rata Rating"
                value={stats.averageRating.toFixed(1) || "0.0"}
                description="Rata-rata rating makanan"
                icon={<Star className="h-4 w-4 text-yellow-500" />}
                isRating={true}
            />
        </div>
    );
}
