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

// Custom hook to get theme colors
const useThemeColors = () => {
    const [colors, setColors] = React.useState({
        primary: "#1f2937",
        chart1: "#3b82f6",
        chart2: "#10b981",
        chart3: "#f59e0b",
        chart4: "#ef4444",
        chart5: "#6b7280",
    });

    React.useEffect(() => {
        const updateColors = () => {
            if (typeof window === "undefined") return;

            const root = document.documentElement;
            const computedStyle = getComputedStyle(root);

            const getColor = (property, fallback) => {
                const value = computedStyle.getPropertyValue(property).trim();
                if (value) {
                    // Convert OKLCH to hex if needed
                    return value.includes("oklch") ? `oklch(${value})` : value;
                }
                return fallback;
            };

            setColors({
                primary: getColor("--primary", "#1f2937"),
                chart1: getColor("--chart-1", "#3b82f6"),
                chart2: getColor("--chart-2", "#10b981"),
                chart3: getColor("--chart-3", "#f59e0b"),
                chart4: getColor("--chart-4", "#ef4444"),
                chart5: getColor("--chart-5", "#6b7280"),
            });
        };

        updateColors();

        // Listen for theme changes
        const observer = new MutationObserver(updateColors);
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ["class"],
        });

        return () => observer.disconnect();
    }, []);

    return colors;
};

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

    // Get theme colors
    const themeColors = useThemeColors();

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

    // Function to get bar color based on rating
    const getBarColor = (rating) => {
        // Color system based on rating quality:
        // 4.5+ = Primary (Best)
        // 4.0-4.4 = Chart-1 (Very Good)
        // 3.5-3.9 = Chart-2 (Good)
        // 3.0-3.4 = Chart-3 (Average)
        // 2.0-2.9 = Chart-4 (Below Average)
        // <2.0 = Chart-5 (Poor)
        if (rating >= 4.5) return themeColors.primary; // Excellent - Primary
        if (rating >= 4.0) return themeColors.chart1; // Very Good - Chart 1
        if (rating >= 3.5) return themeColors.chart2; // Good - Chart 2
        if (rating >= 3.0) return themeColors.chart3; // Average - Chart 3
        if (rating >= 2.0) return themeColors.chart4; // Below Average - Chart 4
        return themeColors.chart5; // Poor - Chart 5
    };

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
    const CustomTooltip = ({ active, payload }) => {
        if (!active || !payload || !payload.length) return null;

        const data = payload[0].payload;
        const rating = data.rating;
        const fullName = data.fullName;

        // Create star rating display
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;

        return (
            <div className="bg-card dark:bg-card p-3 border border-border rounded-md shadow-md">
                <p className="font-medium text-card-foreground mb-1">
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
                                <span className="text-muted-foreground">☆</span>
                            )}
                        </span>
                    ))}
                    <span className="ml-2 font-medium text-foreground">
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
                        stroke="var(--border)"
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
                            fill: "var(--muted-foreground)",
                        }}
                        tickMargin={10}
                    />
                    <YAxis
                        domain={[0, 5]}
                        ticks={[0, 1, 2, 3, 4, 5]}
                        tick={{
                            fill: "var(--muted-foreground)",
                        }}
                        tickFormatter={(value) => `${value}★`}
                    />
                    <Tooltip
                        content={<CustomTooltip />}
                        cursor={{ fill: "var(--muted) / 0.1" }}
                        backgroundColor="var(--card)"
                    />
                    <Legend
                        content={() => (
                            <div className="flex justify-center mt-2 text-sm text-muted-foreground">
                                <Star className="h-4 w-4 text-yellow-500 fill-yellow-500 mr-1" />
                                <span>Penilaian Makanan (0-5 bintang)</span>
                            </div>
                        )}
                    />
                    <Bar
                        dataKey="rating"
                        radius={[10, 10, 0, 0]}
                        animationDuration={1000}
                        animationEasing="ease-out"
                        fill="var(--chart-1)"
                    >
                        {chartData.map((entry, index) => (
                            <rect
                                key={`cell-${index}`}
                                fill="var(--primary)"
                                className="hover:opacity-80 transition-opacity duration-200"
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
