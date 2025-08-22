import React from "react";
import useSWR from "swr";
import {
    BarChart,
    Bar,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import { Badge } from "@/components/ui/badge";
import { Star } from "lucide-react";

// Dummy data generator function
const generateDummyData = () => {
    return [
        {
            name: "Sinonggi",
            rating: 4.8,
            fullName: "Sinonggi (Bubur Sagu Khas)",
        },
        { name: "Kasuami", rating: 4.6, fullName: "Kasuami (Beras Singkong)" },
        { name: "Parende", rating: 3.5, fullName: "Ikan Parende Pedas" },
        {
            name: "Lapa-Lapa",
            rating: 4.7,
            fullName: "Lapa-Lapa (Beras dalam Daun)",
        },
        { name: "Pokea", rating: 4.3, fullName: "Pokea (Kerang Sungai)" },
        { name: "Kabuto", rating: 2.4, fullName: "Kabuto (Ikan dalam Bambu)" },
        { name: "Natinumbho", rating: 4.2, fullName: "Natinumbho (Ikan Asap)" },
        { name: "Ikan Bakar", rating: 4.5, fullName: "Ikan Bakar Mangrove" },
    ];
};

export default function TopRatedFoodsChart() {
    const { data, isLoading } = useSWR("/api/v1/dashboard/top-rated-foods", {
        revalidateOnFocus: false,
    });

    // Format data for the chart
    const chartData = React.useMemo(() => {
        if (!data?.data) {
            if (!isLoading) {
                return generateDummyData();
            }
            return [];
        }

        return data.data.slice(0, 7).map((item) => ({
            name:
                item.name.length > 15
                    ? item.name.substring(0, 12) + "..."
                    : item.name,
            rating: item.rating,
            fullName: item.name, // For tooltip
        }));
    }, [data, isLoading]);

    // New color palette for the bars
    const colorPalette = [
        "hsl(142, 76%, 36%)", // Green
        "hsl(262, 80%, 50%)", // Purple
        "hsl(230, 80%, 50%)", // Blue
        "hsl(43, 96%, 50%)", // Yellow
        "hsl(22, 100%, 52%)", // Orange
        "hsl(0, 84%, 60%)", // Red
        "hsl(176, 80%, 36%)", // Teal
    ];

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-[300px] w-full">
                <p className="text-muted-foreground">Memuat data grafik...</p>
            </div>
        );
    }

    if (!chartData.length) {
        return (
            <div className="flex items-center justify-center h-[300px] w-full">
                <p className="text-muted-foreground">
                    Tidak ada data penilaian tersedia
                </p>
            </div>
        );
    }

    // Custom tooltip component with stars representation
    const CustomTooltip = ({ active, payload, label }) => {
        if (!active || !payload || !payload.length) return null;

        const data = payload[0].payload;
        const rating = data.rating;
        const fullName = data.fullName;

        // Create star rating display
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;

        return (
            <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded-md shadow-md">
                <p className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                    {fullName}
                </p>
                <div className="flex items-center mb-1">
                    {[...Array(5)].map((_, i) => (
                        <span key={i} className="text-lg">
                            {i < fullStars ? (
                                <span className="text-yellow-500">★</span>
                            ) : i === fullStars && hasHalfStar ? (
                                <span className="text-yellow-500">✯</span>
                            ) : (
                                <span className="text-gray-300 dark:text-gray-600">
                                    ☆
                                </span>
                            )}
                        </span>
                    ))}
                    <span className="ml-2 font-medium">
                        {rating.toFixed(1)}
                    </span>
                </div>
                <Badge className="mt-1" variant="outline">
                    {getRatingCategory(rating)}
                </Badge>
            </div>
        );
    };

    // Function to get rating category
    const getRatingCategory = (rating) => {
        if (rating >= 4.5) return "Sangat Baik";
        if (rating >= 4.0) return "Baik Sekali";
        if (rating >= 3.5) return "Baik";
        if (rating >= 3.0) return "Rata-rata";
        if (rating >= 2.0) return "Di Bawah Rata-rata";
        return "Kurang";
    };

    return (
        <div className="w-full h-[30rem]">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={chartData}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 60,
                    }}
                    barCategoryGap={8}
                    barGap={4}
                >
                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="rgba(0, 0, 0, 0.1)"
                        className="dark:stroke-[rgba(255,255,255,0.1)]"
                        vertical={false}
                    />
                    <XAxis
                        dataKey="name"
                        angle={-45}
                        textAnchor="end"
                        height={70}
                        tick={{
                            fontSize: 12,
                            fontWeight: 500,
                        }}
                        className="text-gray-600 dark:text-gray-300"
                        tickMargin={10}
                    />
                    <YAxis
                        domain={[0, 5]}
                        ticks={[0, 1, 2, 3, 4, 5]}
                        className="text-gray-600 dark:text-gray-300"
                        tickFormatter={(value) => `${value}★`}
                    />
                    <Tooltip
                        content={<CustomTooltip />}
                        cursor={{ fill: "rgba(0, 0, 0, 0.05)" }}
                    />
                    <Legend
                        content={() => (
                            <div className="flex justify-center mt-2 text-sm text-gray-600 dark:text-gray-300">
                                <Star className="h-4 w-4 text-yellow-500 fill-yellow-500 mr-1" />
                                <span>Penilaian Makanan (0-5 bintang)</span>
                            </div>
                        )}
                    />
                    <Bar
                        dataKey="rating"
                        radius={[4, 4, 0, 0]}
                        animationDuration={1000}
                        animationEasing="ease-out"
                    >
                        {chartData.map((entry, index) => (
                            <rect
                                key={`cell-${index}`}
                                x={0}
                                y={0}
                                width="100%"
                                height="100%"
                                fill={colorPalette[index % colorPalette.length]}
                                className="hover:opacity-80 transition-opacity"
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
