import React, { useState } from "react";
import { motion } from "framer-motion";

// Import modular components
import RestaurantHeader from "./components/RestaurantHeader";
import RestaurantFilters from "./components/RestaurantFilters";
import RestaurantSummary from "./components/RestaurantSummary";
import {
    RestaurantLoadingSkeleton,
    RestaurantErrorState,
    RestaurantEmptyState,
    RestaurantGrid,
} from "./components/RestaurantStates";

// Import hooks
import { useRestaurantFilters } from "./hooks/useRestaurantFilters";
import { useRestaurantData } from "@/hooks/useApiData";

export default function RestaurantsPage() {
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [sortBy, setSortBy] = useState("name");

    // Fetch restaurants data using custom hook
    const { restaurants, totalCount, isLoading, error, refetch } =
        useRestaurantData();

    // Filter and sort restaurants using custom hook
    const filteredAndSortedRestaurants = useRestaurantFilters(
        restaurants,
        searchTerm,
        statusFilter,
        sortBy
    );

    // Reset filters function
    const handleResetFilters = () => {
        setSearchTerm("");
        setStatusFilter("all");
        setSortBy("name");
    };

    // Retry function for error state
    const handleRetry = () => {
        refetch();
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
                filteredCount={filteredAndSortedRestaurants.length}
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
                ) : filteredAndSortedRestaurants.length === 0 ? (
                    <RestaurantEmptyState
                        searchTerm={searchTerm}
                        statusFilter={statusFilter}
                    />
                ) : (
                    <RestaurantGrid
                        restaurants={filteredAndSortedRestaurants}
                    />
                )}
            </motion.div>
        </div>
    );
}
