import { useState, useEffect } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { useDebounce } from "@/hooks/useDebounce";
import apiService from "@/lib/api";

export const useFoods = (initialPage = 1, initialPageSize = 50) => {
    // State management
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [categoryFilter, setCategoryFilter] = useState("all");
    const [page, setPage] = useState(initialPage);
    const [pageSize] = useState(initialPageSize);

    // Apply debounce to search term to prevent excessive API calls
    const debouncedSearchTerm = useDebounce(searchTerm, 500);
    const debouncedStatusFilter = useDebounce(statusFilter, 500);
    const debouncedCategoryFilter = useDebounce(categoryFilter, 500);

    // Reset page to 1 when filters change
    useEffect(() => {
        setPage(1);
    }, [debouncedSearchTerm, debouncedStatusFilter, debouncedCategoryFilter]);

    // Fetch foods data
    const { data, error, mutate, isLoading } = useSWR(
        [
            `/foods`,
            page,
            pageSize,
            debouncedSearchTerm,
            debouncedStatusFilter,
            debouncedCategoryFilter,
        ],
        () =>
            apiService.foods.getAll(
                page,
                pageSize,
                debouncedSearchTerm,
                debouncedStatusFilter === "all" ? "" : debouncedStatusFilter,
                debouncedCategoryFilter === "all" ? "" : debouncedCategoryFilter
            ),
        {
            revalidateOnFocus: false,
            onError: () => {
                toast.error("Gagal memuat data makanan");
            },
        }
    );

    const foods = data?.data?.data?.foods || [];
    const pagination = data?.data?.data?.pagination || {};

    // Fetch restaurants for restaurant name display
    const { data: restaurantsData } = useSWR(
        ["/restaurants/list"],
        () => apiService.restaurants.getAll(1, 1000, ""),
        {
            revalidateOnFocus: false,
        }
    );

    const restaurants = restaurantsData?.data?.data?.restaurants || [];

    // Create a restaurant lookup map for quick access
    const restaurantMap = restaurants.reduce((acc, restaurant) => {
        acc[restaurant.id] = restaurant.name;
        return acc;
    }, {});

    // Handle search
    const handleSearch = (value) => {
        setSearchTerm(value);
    };

    // Handle status filter change
    const handleStatusFilter = (value) => {
        setStatusFilter(value);
    };

    // Handle category filter change
    const handleCategoryFilter = (value) => {
        setCategoryFilter(value);
    };

    // Handle refresh after operations
    const refreshData = async () => {
        try {
            // Force a revalidation (ignore cache)
            await mutate(undefined, { revalidate: true });
        } catch (error) {
            console.error("Error refreshing data:", error);
        }
    };

    return {
        // Data
        foods,
        pagination,
        restaurantMap,
        isLoading,
        error,

        // Pagination
        page,
        setPage,
        pageSize,

        // Filters
        searchTerm,
        statusFilter,
        categoryFilter,
        handleSearch,
        handleStatusFilter,
        handleCategoryFilter,

        // Actions
        refreshData,
    };
};
