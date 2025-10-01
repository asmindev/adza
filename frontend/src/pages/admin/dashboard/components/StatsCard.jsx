import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/pages/detail/components/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function StatsCard({
    title,
    value,
    description,
    icon,
    trend = null,
    isRating = false,
}) {
    // Helper to determine the trend indicator
    const renderTrendIndicator = () => {
        if (trend === null) return null;

        if (trend > 0) {
            return (
                <div className="flex items-center text-emerald-500">
                    <TrendingUp className="h-4 w-4 mr-1" />
                    <span>+{trend}%</span>
                </div>
            );
        } else if (trend < 0) {
            return (
                <div className="flex items-center text-red-500">
                    <TrendingDown className="h-4 w-4 mr-1" />
                    <span>{trend}%</span>
                </div>
            );
        } else {
            return (
                <div className="flex items-center text-gray-500">
                    {/* <Minus className="h-4 w-4 mr-1" />
                    <span>0%</span> */}
                </div>
            );
        }
    };

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                {icon}
            </CardHeader>
            <CardContent>
                <div className="flex flex-col space-y-1">
                    <div className="flex items-baseline">
                        <span
                            className={cn(
                                "text-2xl font-bold",
                                isRating && "flex items-center"
                            )}
                        >
                            {value}
                            {isRating && (
                                <span className="ml-1 text-yellow-500">★</span>
                            )}
                        </span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                        <p className="text-muted-foreground">{description}</p>
                        {renderTrendIndicator()}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
