"use client";

import {
    Bar,
    BarChart,
    XAxis,
    YAxis,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
} from "recharts";
import { ChartContainer } from "@/components/ui/chart";

const chartConfig = {
    rating_count: {
        label: "Jumlah Rating",
        color: "hsl(var(--chart-1))",
    },
    avg_rating: {
        label: "Rata-rata Rating",
        color: "hsl(var(--chart-2))",
    },
};

export function Component({ data = [] }) {
    // Transform the data for the chart
    const chartData = data.slice(0, 8).map((food) => ({
        name:
            food.name.length > 15
                ? food.name.substring(0, 15) + "..."
                : food.name,
        rating_count: food.rating_count,
        avg_rating: food.avg_rating,
        full_name: food.name,
        price: food.price,
    }));

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
                    <p className="font-medium">{data.full_name}</p>
                    <p className="text-sm text-muted-foreground">
                        Harga: Rp {data.price?.toLocaleString("id-ID") || "N/A"}
                    </p>
                    <p className="text-sm">
                        <span className="text-chart-1">
                            Jumlah Rating: {data.rating_count}
                        </span>
                    </p>
                    <p className="text-sm">
                        <span className="text-chart-2">
                            Rata-rata: {data.avg_rating}
                        </span>
                    </p>
                </div>
            );
        }
        return null;
    };

    if (!data || data.length === 0) {
        return (
            <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                Tidak ada data makanan terpopuler
            </div>
        );
    }

    return (
        <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={chartData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="name"
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        fontSize={12}
                    />
                    <YAxis fontSize={12} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar
                        dataKey="rating_count"
                        fill="var(--color-rating_count)"
                        radius={[4, 4, 0, 0]}
                        name="Jumlah Rating"
                    />
                </BarChart>
            </ResponsiveContainer>
        </ChartContainer>
    );
}

export default Component;
