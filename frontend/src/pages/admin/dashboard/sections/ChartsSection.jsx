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
import { motion } from "framer-motion";

export default function ChartsSection({ isLoading, stats }) {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card className="col-span-2">
                <CardHeader>
                    <CardTitle>Makanan Terpopuler</CardTitle>
                    <CardDescription>
                        Makanan dengan rating tertinggi di koleksi Anda
                    </CardDescription>
                </CardHeader>
                <CardContent className={"h-full"}>
                    <TopRatedFoodsChart />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Aktivitas Terbaru</CardTitle>
                    <CardDescription>
                        Aktivitas terbaru di platform
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex items-center justify-center h-[200px]">
                            <p className="text-muted-foreground">
                                Memuat aktivitas...
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {stats.recentActivities?.length > 0 ? (
                                stats.recentActivities.map(
                                    (activity, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{
                                                opacity: 0,
                                                y: 10,
                                            }}
                                            animate={{
                                                opacity: 1,
                                                y: 0,
                                            }}
                                            transition={{
                                                delay: index * 0.1,
                                            }}
                                            className="flex items-center space-x-2 border-b pb-2"
                                        >
                                            <TrendingUp className="h-4 w-4 text-green-500" />
                                            <div className="space-y-1">
                                                <p className="text-sm font-medium">
                                                    {activity.title}
                                                </p>
                                                <p className="text-xs text-muted-foreground">
                                                    {activity.time}
                                                </p>
                                            </div>
                                        </motion.div>
                                    )
                                )
                            ) : (
                                <p className="text-center text-muted-foreground">
                                    Tidak ada aktivitas terbaru
                                </p>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
