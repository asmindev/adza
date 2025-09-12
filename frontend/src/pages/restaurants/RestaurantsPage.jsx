import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

// Import modular components
import RestaurantHeader from "./components/RestaurantHeader";
import RestaurantFilters from "./components/RestaurantFilters";
import RestaurantSummary from "./components/RestaurantSummary";
import {
    RestaurantLoadingSkeleton,
    RestaurantLoadingMore,
    RestaurantErrorState,
    RestaurantEmptyState,
    RestaurantGrid,
    InfiniteScrollTrigger,
    LoadMoreButton,
} from "./components/RestaurantStates";

// Import hooks
import { useInfiniteRestaurants } from "@/hooks/useInfiniteRestaurants";
import { useInfiniteScroll } from "@/hooks/useInfiniteScroll";
import { useDebounce } from "@/hooks/useDebounce";

export default function RestaurantsPage() {
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [sortBy, setSortBy] = useState("name");
    const [showFallbackButton, setShowFallbackButton] = useState(false);
    const [lastLoadTime, setLastLoadTime] = useState(Date.now());

    // Debounce search term to reduce API calls
    const debouncedSearchTerm = useDebounce(searchTerm, 300);

    // Create filters object for the API
    const filters = {
        search: debouncedSearchTerm,
        status: statusFilter,
        sortBy: sortBy,
    };

    // Fetch restaurants data using infinite pagination hook with server-side filtering
    const {
        restaurants,
        totalCount,
        isLoading,
        isLoadingMore,
        error,
        hasMore,
        loadMore,
        refresh,
    } = useInfiniteRestaurants(20, filters);

    // Infinite scroll trigger ref
    const loadMoreRef = useInfiniteScroll(loadMore, hasMore, isLoadingMore);

    // Track when data changes to reset fallback timer
    useEffect(() => {
        if (restaurants.length > 0) {
            setLastLoadTime(Date.now());
            setShowFallbackButton(false);
        }
    }, [restaurants.length]);

    // Show fallback button after 5 seconds if hasMore but no new data loaded
    useEffect(() => {
        if (hasMore && !isLoading && !isLoadingMore && restaurants.length > 0) {
            const timer = setTimeout(() => {
                setShowFallbackButton(true);
            }, 5000); // Show fallback after 5 seconds

            return () => clearTimeout(timer);
        } else {
            setShowFallbackButton(false);
        }
    }, [hasMore, isLoading, isLoadingMore, restaurants.length, lastLoadTime]);

    // Manual load more function for fallback button
    const handleManualLoadMore = () => {
        setShowFallbackButton(false);
        setLastLoadTime(Date.now());
        loadMore();
    };

    // Reset filters function
    const handleResetFilters = () => {
        setSearchTerm("");
        setStatusFilter("all");
        setSortBy("name");
    };

    // Retry function for error state
    const handleRetry = () => {
        refresh();
    };

    return (
        <div className="max-w-7xl mx-auto p-4 space-y-6">
            {/* Header */}
            <RestaurantHeader totalCount={totalCount} />

            {/* Filters */}
            <RestaurantFilters
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                statusFilter={statusFilter}
                setStatusFilter={setStatusFilter}
                sortBy={sortBy}
                setSortBy={setSortBy}
            />

            {/* Results Summary */}
            <RestaurantSummary
                filteredCount={restaurants.length}
                searchTerm={searchTerm}
                onResetFilters={handleResetFilters}
            />

            {/* Restaurant Grid */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
            >
                {isLoading ? (
                    <RestaurantLoadingSkeleton />
                ) : error ? (
                    <RestaurantErrorState onRetry={handleRetry} />
                ) : restaurants.length === 0 ? (
                    <RestaurantEmptyState
                        searchTerm={searchTerm}
                        statusFilter={statusFilter}
                    />
                ) : (
                    <>
                        <RestaurantGrid restaurants={restaurants} />

                        {/* Loading more skeleton */}
                        {isLoadingMore && <RestaurantLoadingMore />}

                        {/* Infinite scroll trigger */}
                        {hasMore && !showFallbackButton && (
                            <InfiniteScrollTrigger
                                ref={loadMoreRef}
                                hasMore={hasMore}
                                isLoading={isLoadingMore}
                            />
                        )}

                        {/* Fallback Load More Button */}
                        {hasMore && showFallbackButton && (
                            <LoadMoreButton
                                onLoadMore={handleManualLoadMore}
                                isLoading={isLoadingMore}
                                hasMore={hasMore}
                            />
                        )}

                        {/* End of results indicator */}
                        {!hasMore && restaurants.length > 0 && (
                            <div className="text-center py-8">
                                <p className="text-muted-foreground">
                                    Semua restoran telah dimuat (
                                    {restaurants.length} restoran)
                                </p>
                            </div>
                        )}
                    </>
                )}
            </motion.div>
        </div>
    );
}
