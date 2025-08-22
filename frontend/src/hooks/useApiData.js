import useSWR from "swr";
import { toast } from "sonner";

export const useFoodData = () => {
    const { data, error, isLoading, mutate } = useSWR("/api/v1/foods", {
        revalidateOnFocus: false,
        onError: (err) => {
            toast.error("Gagal memuat data makanan", {
                description: err.message || "Silakan coba lagi nanti",
            });
        },
    });

    const foods = data?.data?.foods || [];

    return {
        foods,
        isLoading,
        error,
        refetch: mutate,
    };
};

export const useRestaurantData = () => {
    const { data, error, isLoading, mutate } = useSWR("/api/v1/restaurants", {
        revalidateOnFocus: false,
        onError: (err) => {
            toast.error("Gagal memuat data restoran", {
                description: err.message || "Silakan coba lagi nanti",
            });
        },
    });

    const restaurants = data?.data?.restaurants || [];
    const totalCount = data?.data?.count || 0;

    return {
        restaurants,
        totalCount,
        isLoading,
        error,
        refetch: mutate,
    };
};
