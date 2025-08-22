import React, { useMemo } from "react";
import {
    PieChart,
    Pie,
    ResponsiveContainer,
    Tooltip,
    Legend,
    Cell,
} from "recharts";
import { Badge } from "@/components/ui/badge";
import { Star } from "lucide-react";

// Dummy data generator function
const generateDummyData = () => {
    return [
        { name: "5★", value: 15 },
        { name: "4★-4.9★", value: 30 },
        { name: "3★-3.9★", value: 25 },
        { name: "2★-2.9★", value: 10 },
        { name: "0★-1.9★", value: 5 },
        { name: "Belum Dinilai", value: 8 },
    ];
};

export default function FoodRatingChart({ data }) {
    // Process data for chart
    const chartData = useMemo(() => {
        // If no data is provided, return dummy data
        if (!data || data.length === 0) {
            return generateDummyData();
        }

        // Group foods by rating range
        const ratingGroups = {
            "5★": 0,
            "4★-4.9★": 0,
            "3★-3.9★": 0,
            "2★-2.9★": 0,
            "0★-1.9★": 0,
            "Belum Dinilai": 0,
        };

        data.forEach((food) => {
            const rating = food.rating;

            if (rating === undefined || rating === null) {
                ratingGroups["Belum Dinilai"]++;
            } else if (rating === 5) {
                ratingGroups["5★"]++;
            } else if (rating >= 4) {
                ratingGroups["4★-4.9★"]++;
            } else if (rating >= 3) {
                ratingGroups["3★-3.9★"]++;
            } else if (rating >= 2) {
                ratingGroups["2★-2.9★"]++;
            } else {
                ratingGroups["0★-1.9★"]++;
            }
        });

        // Convert to array format for chart
        return Object.entries(ratingGroups)
            .map(([name, value]) => ({ name, value }))
            .filter((item) => item.value > 0);
    }, [data]);

    // Chart colors
    const COLORS = [
        "hsl(142, 76%, 36%)", // Green
        "hsl(262, 80%, 50%)", // Purple
        "hsl(230, 80%, 50%)", // Blue
        "hsl(43, 96%, 50%)", // Yellow
        "hsl(22, 100%, 52%)", // Orange
        "hsl(215, 20%, 65%)", // Gray
    ];

    // Custom tooltip
    const CustomTooltip = ({ active, payload }) => {
        if (!active || !payload || !payload.length) return null;

        const data = payload[0];
        const name = data.name;
        const value = data.value;

        return (
            <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 rounded-md shadow-md">
                <p className="font-medium text-gray-900 dark:text-gray-100">
                    {name}
                </p>
                <p className="text-gray-700 dark:text-gray-300">
                    {value} makanan
                </p>
            </div>
        );
    };

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        fill="#8884d8"
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) =>
                            `${name} (${(percent * 100).toFixed(0)}%)`
                        }
                        labelLine={false}
                    >
                        {chartData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                            />
                        ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend
                        layout="horizontal"
                        verticalAlign="bottom"
                        align="center"
                        formatter={(value) => (
                            <span className="text-sm">{value}</span>
                        )}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}
