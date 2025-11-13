import { useState, useEffect } from "react";
import { apiService } from "@/pages/detail/components/lib/api";

/**
 * Hook untuk mendapatkan rekomendasi makanan
 * @param {boolean} enabled - Apakah hook ini enabled (user harus login)
 * @param {number} limit - Limit jumlah rekomendasi (default: 10)
 * @returns {Object} - Object dengan data recommendations
 */
export function useRecommendations(enabled = false, limit = 10) {
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!enabled) {
            setRecommendations([]);
            return;
        }

        const fetchRecommendations = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await apiService.foods.getRecommendation();
                const data = response.data;

                if (data.error) {
                    throw new Error(
                        data.message || "Failed to fetch recommendations"
                    );
                }

                setRecommendations(data.data.recommendations || []);
            } catch (err) {
                console.error("Error fetching recommendations:", err);
                setError(err);
                setRecommendations([]);
            } finally {
                setLoading(false);
            }
        };

        fetchRecommendations();
    }, [enabled, limit]);

    return {
        recommendations,
        loading,
        error,
    };
}
