import React from "react";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
} from "@/components/ui/card";
import TopRatedFoodsChart from "../components/charts/TopRatedFoodsChart";
import { TrendingUp } from "lucide-react";

export default function ChartsSection({ isLoading, stats }) {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card className="col-span-2">
                <CardHeader>
                    <CardTitle>Makanan Terpopuler</CardTitle>
                    <CardDescription>
                        Makanan dengan jumlah rating terbanyak
                    </CardDescription>
                </CardHeader>
                <CardContent className={"h-full"}>
                    <TopRatedFoodsChart data={stats.popularFoods} />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Rating Tertinggi</CardTitle>
                    <CardDescription>
                        Makanan dengan rating tertinggi (min. 5 rating)
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex items-center justify-center h-[200px]">
                            <p className="text-muted-foreground">
                                Memuat data...
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {stats.topRatedFoods?.length > 0 ? (
                                stats.topRatedFoods.slice(0, 6).map((food) => (
                                    <div
                                        key={food.id}
                                        className="flex items-center justify-between border-b pb-2 last:border-b-0"
                                    >
                                        <div className="flex-1">
                                            <p className="text-sm font-medium truncate">
                                                {food.name}
                                            </p>
                                            <p className="text-xs text-muted-foreground">
                                                {food.rating_count} rating • Rp{" "}
                                                {food.price?.toLocaleString(
                                                    "id-ID"
                                                ) || "N/A"}
                                            </p>
                                        </div>
                                        <div className="flex items-center space-x-1">
                                            <TrendingUp className="h-3 w-3 text-yellow-500" />
                                            <span className="text-sm font-medium">
                                                {food.avg_rating.toFixed(1)}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-center text-muted-foreground">
                                    Tidak ada data makanan dengan rating tinggi
                                </p>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
