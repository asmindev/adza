import { useState, useEffect } from "react";
import { apiService } from "@/pages/detail/components/lib/api";

/**
 * Hook untuk mendapatkan makanan populer
 * @param {number} limit - Limit jumlah makanan (default: 10)
 * @param {number} minRatings - Minimum jumlah rating (default: 5)
 * @returns {Object} - Object dengan data popular foods
 */
export function usePopularFoods(limit = 10, minRatings = 5) {
    const [popularFoods, setPopularFoods] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPopularFoods = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await apiService.foods.getPopular();
                const data = response.data;

                if (data.error) {
                    throw new Error(
                        data.message || "Failed to fetch popular foods"
                    );
                }

                setPopularFoods(data.data.popular_foods || []);
            } catch (err) {
                console.error("Error fetching popular foods:", err);
                setError(err);
                setPopularFoods([]);
            } finally {
                setLoading(false);
            }
        };

        fetchPopularFoods();
    }, [limit, minRatings]);

    return {
        popularFoods,
        loading,
        error,
    };
}
