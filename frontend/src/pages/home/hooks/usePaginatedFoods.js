import { useState, useCallback, useEffect } from "react";
import { apiService } from "@/lib/api";

/**
 * Hook untuk mengelola pagination data makanan menggunakan API pagination
 * @param {number} initialLimit - Limit awal untuk data (default: 20)
 * @param {string} searchQuery - Query pencarian (optional)
 * @returns {Object} - Object dengan data dan functions
 */
export function usePaginatedFoods(initialLimit = 5, searchQuery = null) {
    const [foods, setFoods] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(initialLimit);
    const [search, setSearch] = useState(searchQuery);
    const [pagination, setPagination] = useState({
        limit: initialLimit,
        page: 1,
        pages: 0,
        total: 0,
    });

    // Fetch foods from API with pagination
    const fetchFoods = useCallback(
        async (
            pageNum = 1,
            limitNum = limit,
            searchTerm = search,
            isLoadMore = false
        ) => {
            setLoading(true);
            setError(null);

            try {
                const response = await apiService.foods.getAll(
                    pageNum,
                    limitNum,
                    searchTerm || ""
                );
                const data = response.data;

                if (data.error) {
                    throw new Error(data.message || "Failed to fetch foods");
                }

                // Update pagination info
                setPagination(data.data.pagination);

                if (isLoadMore) {
                    // Append new foods for infinite scroll
                    setFoods((prev) => [...prev, ...data.data.foods]);
                } else {
                    // Replace foods for initial load or page change
                    setFoods(data.data.foods);
                }
            } catch (err) {
                console.error("Error fetching foods:", err);
                setError(err);
            } finally {
                setLoading(false);
            }
        },
        [limit, search]
    );

    // Update internal search when external searchQuery changes
    useEffect(() => {
        if (searchQuery !== search) {
            setSearch(searchQuery);
        }
    }, [searchQuery, search]);

    // Load initial data when limit or search changes
    useEffect(() => {
        setPage(1);
        setFoods([]);
        fetchFoods(1, limit, search, false);
    }, [limit, search, fetchFoods]);

    // Calculate hasMore for infinite scroll
    const hasMore = page < pagination.pages;

    const loadMore = useCallback(async () => {
        if (hasMore && !loading) {
            const nextPage = page + 1;
            setPage(nextPage);
            await fetchFoods(nextPage, limit, search, true);
        }
    }, [hasMore, loading, page, limit, search, fetchFoods]);

    const reset = useCallback(() => {
        setPage(1);
        setFoods([]);
        setError(null);
        fetchFoods(1, limit, search, false);
    }, [limit, search, fetchFoods]);

    // Change limit and reload
    const changeLimit = useCallback((newLimit) => {
        setLimit(newLimit);
    }, []);

    // Change search query and reload
    const changeSearch = useCallback((searchQuery) => {
        setSearch(searchQuery);
    }, []);

    return {
        foods,
        error,
        loading,
        hasMore,
        loadMore,
        reset,
        changeLimit,
        changeSearch,
        currentPage: page,
        pagination,
        search,
        totalLoaded: foods.length,
        totalAvailable: pagination.total,
    };
}
