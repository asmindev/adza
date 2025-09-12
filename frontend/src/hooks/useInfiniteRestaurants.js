import { useState, useEffect, useCallback, useMemo } from "react";
import useSWR from "swr";
import { toast } from "sonner";

export const useInfiniteRestaurants = (limit = 20, filters = {}) => {
    const [page, setPage] = useState(1);
    const [allRestaurants, setAllRestaurants] = useState([]);
    const [hasMore, setHasMore] = useState(true);
    const [isLoadingMore, setIsLoadingMore] = useState(false);

    // Build query string from filters
    const queryParams = useMemo(() => {
        const params = new URLSearchParams();
        params.set("page", page.toString());
        params.set("limit", limit.toString());

        // Add search term if provided
        if (filters.search) {
            params.set("search", filters.search);
        }

        // Add status filter if provided
        if (filters.status && filters.status !== "all") {
            params.set("status", filters.status);
        }

        // Add sort if provided
        if (filters.sortBy) {
            params.set("sortBy", filters.sortBy);
        }

        return params.toString();
    }, [page, limit, filters]);

    // Construct the API URL with pagination parameters
    const apiUrl = `/api/v1/restaurants?${queryParams}`;

    const { data, error, isLoading, mutate } = useSWR(apiUrl, {
        revalidateOnFocus: false,
        onError: (err) => {
            toast.error("Gagal memuat data restoran", {
                description: err.message || "Silakan coba lagi nanti",
            });
        },
    });

    // Reset when filters change (except page)
    useEffect(() => {
        setPage(1);
        setAllRestaurants([]);
        setHasMore(true);
        setIsLoadingMore(false);
    }, [filters.search, filters.status, filters.sortBy]);

    // Update restaurants when new data is fetched
    useEffect(() => {
        if (data?.data) {
            const newRestaurants = data.data.restaurants || [];
            const pagination = data.data.pagination || {};

            if (page === 1) {
                // First page - replace all restaurants
                setAllRestaurants(newRestaurants);
            } else {
                // Subsequent pages - append new restaurants
                setAllRestaurants((prev) => {
                    // Prevent duplicates by filtering out restaurants that already exist
                    const existingIds = new Set(prev.map((r) => r.id));
                    const uniqueNewRestaurants = newRestaurants.filter(
                        (r) => !existingIds.has(r.id)
                    );
                    return [...prev, ...uniqueNewRestaurants];
                });
            }

            // Update hasMore based on pagination info
            setHasMore(pagination.page < pagination.pages);
            setIsLoadingMore(false);
        }
    }, [data, page]);

    // Load more restaurants with throttling to prevent rapid calls
    const loadMore = useCallback(() => {
        if (!isLoading && !isLoadingMore && hasMore) {
            setIsLoadingMore(true);
            setPage((prev) => prev + 1);
        }
    }, [isLoading, isLoadingMore, hasMore]);

    // Reset pagination (useful for filters)
    const reset = useCallback(() => {
        setPage(1);
        setAllRestaurants([]);
        setHasMore(true);
        setIsLoadingMore(false);
        mutate();
    }, [mutate]);

    // Refresh data
    const refresh = useCallback(() => {
        setPage(1);
        setAllRestaurants([]);
        setHasMore(true);
        setIsLoadingMore(false);
        mutate();
    }, [mutate]);

    return {
        restaurants: allRestaurants,
        totalCount: data?.data?.pagination?.total || 0,
        isLoading: isLoading && page === 1, // Only show loading for first page
        isLoadingMore,
        error,
        hasMore,
        loadMore,
        reset,
        refresh,
        pagination: data?.data?.pagination || null,
    };
};
