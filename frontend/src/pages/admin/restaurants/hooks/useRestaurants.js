import { useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { useDebounce } from "@/hooks/useDebounce";
import apiService from "@/pages/detail/components/lib/api";

export const useRestaurants = () => {
    const [pageIndex, setPageIndex] = useState(0);
    const [pageSize] = useState(10);
    const [searchTerm, setSearchTerm] = useState("");
    const [sorting, setSorting] = useState([]);

    // Apply debounce to search term to prevent excessive API calls
    const debouncedSearchTerm = useDebounce(searchTerm, 500);

    // Fetch restaurants with SWR using real API
    const {
        data: response,
        error,
        mutate,
    } = useSWR(
        [`/restaurants`, pageIndex, pageSize, debouncedSearchTerm],
        () =>
            apiService.restaurants.getAll(
                pageIndex + 1,
                pageSize,
                debouncedSearchTerm
            ),
        {
            revalidateOnFocus: false,
            onError: (err) => {
                toast.error(err.message || "Gagal mengambil data restoran");
            },
        }
    );

    let data = response?.data?.data || {};

    const restaurants = data?.restaurants || [];
    const totalCount = data?.pagination?.total || 0;
    const totalPages = data?.pagination?.pages || 0;
    const isLoading = !data && !error;

    // Handle search
    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
        setPageIndex(0); // Reset to first page on new search
    };

    // Handle refresh after operations
    const refreshData = () => {
        mutate();
    };

    return {
        // Data
        restaurants,
        totalCount,
        totalPages,
        isLoading,

        // Pagination
        pageIndex,
        pageSize,
        setPageIndex,

        // Search
        searchTerm,
        handleSearch,

        // Sorting
        sorting,
        setSorting,

        // Actions
        refreshData,
    };
};
