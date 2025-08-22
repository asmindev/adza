import { useMemo } from "react";

export const useRestaurantFilters = (
    restaurants,
    searchTerm,
    statusFilter,
    sortBy
) => {
    return useMemo(() => {
        let filtered = restaurants.filter((restaurant) => {
            // Search filter
            const matchesSearch =
                restaurant.name
                    .toLowerCase()
                    .includes(searchTerm.toLowerCase()) ||
                restaurant.description
                    ?.toLowerCase()
                    .includes(searchTerm.toLowerCase()) ||
                restaurant.address
                    ?.toLowerCase()
                    .includes(searchTerm.toLowerCase());

            // Status filter
            const matchesStatus =
                statusFilter === "all" ||
                (statusFilter === "active" && restaurant.is_active) ||
                (statusFilter === "inactive" && !restaurant.is_active);

            return matchesSearch && matchesStatus;
        });

        // Sort restaurants
        filtered.sort((a, b) => {
            switch (sortBy) {
                case "name":
                    return a.name.localeCompare(b.name);
                case "rating":
                    return (b.rating?.average || 0) - (a.rating?.average || 0);
                case "foods":
                    return (b.foods?.length || 0) - (a.foods?.length || 0);
                default:
                    return 0;
            }
        });

        return filtered;
    }, [restaurants, searchTerm, statusFilter, sortBy]);
};
