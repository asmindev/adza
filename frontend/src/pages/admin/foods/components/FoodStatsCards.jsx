import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Utensils, TrendingUp, Calendar, Star } from "lucide-react";
import apiService from "@/pages/detail/components/lib/api";
import { toast } from "sonner";

export default function FoodStatsCards() {
    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            setIsLoading(true);
            const response = await apiService.foods.getStats();
            if (response.data && !response.data.error) {
                setStats(response.data.data);
            }
        } catch (error) {
            console.error("Error fetching stats:", error);
            toast.error("Failed to load statistics");
        } finally {
            setIsLoading(false);
        }
    };

    const statsConfig = [
        {
            title: "Total Makanan",
            value: stats?.total_foods || 0,
            icon: Utensils,
            description: "Total makanan dalam database",
            color: "text-blue-500",
            bgColor: "bg-blue-50",
        },
        {
            title: "Makanan Baru",
            value: stats?.new_foods_last_7_days || 0,
            icon: TrendingUp,
            description: "Ditambahkan 7 hari terakhir",
            color: "text-green-500",
            bgColor: "bg-green-50",
        },
        {
            title: "Rata-rata Rating",
            value: stats?.average_rating?.toFixed(2) || "0.00",
            icon: Star,
            description: `Dari ${stats?.foods_with_ratings || 0} makanan`,
            color: "text-yellow-500",
            bgColor: "bg-yellow-50",
        },
        {
            title: "Belum Ada Rating",
            value: stats?.foods_without_ratings || 0,
            icon: Calendar,
            description: "Makanan tanpa rating",
            color: "text-gray-500",
            bgColor: "bg-gray-50",
        },
    ];

    if (isLoading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                    <Card key={i}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
                            <div className="h-8 w-8 bg-gray-200 rounded animate-pulse" />
                        </CardHeader>
                        <CardContent>
                            <div className="h-8 w-16 bg-gray-200 rounded animate-pulse mb-2" />
                            <div className="h-3 w-32 bg-gray-200 rounded animate-pulse" />
                        </CardContent>
                    </Card>
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {statsConfig.map((stat, index) => {
                const Icon = stat.icon;
                return (
                    <Card key={index}>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">
                                {stat.title}
                            </CardTitle>
                            <div className={`${stat.bgColor} p-2 rounded-lg`}>
                                <Icon className={`h-4 w-4 ${stat.color}`} />
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {stat.value}
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                {stat.description}
                            </p>
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}
