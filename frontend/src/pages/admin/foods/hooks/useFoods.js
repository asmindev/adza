import { useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { useDebounce } from "@/hooks/useDebounce";
import apiService from "@/lib/api";

export const useFoods = () => {
    const [pageIndex, setPageIndex] = useState(0);
    const [pageSize] = useState(10);
    const [searchTerm, setSearchTerm] = useState("");
    const [sorting, setSorting] = useState([]);

    // Apply debounce to search term to prevent excessive API calls
    const debouncedSearchTerm = useDebounce(searchTerm, 500);

    // Fetch foods with SWR using real API
    const { data, error, mutate } = useSWR(
        [`/foods`, pageIndex, pageSize, debouncedSearchTerm],
        () =>
            apiService.foods.getAll(
                pageIndex + 1,
                pageSize,
                debouncedSearchTerm
            ),
        {
            revalidateOnFocus: false,
            onError: (err) => {
                toast.error(err.message || "Gagal mengambil data makanan");
            },
        }
    );

    const foods = data?.data?.data?.foods || [];
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
        foods,
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
