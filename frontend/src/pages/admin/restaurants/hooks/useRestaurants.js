import { useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import apiService from "@/dashboard/services/api";

export const useRestaurants = () => {
    const [pageIndex, setPageIndex] = useState(0);
    const [pageSize] = useState(10);
    const [searchTerm, setSearchTerm] = useState("");
    const [sorting, setSorting] = useState([]);

    // Fetch restaurants with SWR using real API
    const { data, error, mutate } = useSWR(
        [`/restaurants`, pageIndex, pageSize, searchTerm],
        () =>
            apiService.restaurants.getAll(pageIndex + 1, pageSize, searchTerm),
        {
            revalidateOnFocus: false,
            onError: (err) => {
                toast.error(err.message || "Gagal mengambil data restoran");
            },
        }
    );

    const restaurants = data?.data?.data?.restaurants || [];
    const totalCount = data?.data?.data?.count || 0;
    const totalPages = Math.ceil(totalCount / pageSize);
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
