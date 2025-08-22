import React, { useState } from "react";

// Import custom hooks

// Import sections
import RestaurantPageHeader from "./components/RestaurantPageHeader";
import RestaurantListSection from "./sections/RestaurantListSection";
import RestaurantDialogsSection from "./sections/RestaurantDialogsSection";
import { useRestaurants } from "./hooks/useRestaurants";

export default function RestaurantsPage() {
    // Dialog state
    const [deleteRestaurantId, setDeleteRestaurantId] = useState(null);
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [editRestaurantData, setEditRestaurantData] = useState(null);

    // Use custom hook for restaurant data management
    const {
        restaurants,
        totalCount,
        totalPages,
        isLoading,
        pageIndex,
        pageSize,
        setPageIndex,
        searchTerm,
        handleSearch,
        sorting,
        setSorting,
        refreshData,
    } = useRestaurants();

    return (
        <div className="space-y-6">
            <RestaurantPageHeader
                onAddRestaurant={() => setIsAddDialogOpen(true)}
            />

            <RestaurantListSection
                restaurants={restaurants}
                totalCount={totalCount}
                totalPages={totalPages}
                isLoading={isLoading}
                pageIndex={pageIndex}
                pageSize={pageSize}
                setPageIndex={setPageIndex}
                searchTerm={searchTerm}
                handleSearch={handleSearch}
                sorting={sorting}
                setSorting={setSorting}
                setDeleteRestaurantId={setDeleteRestaurantId}
                setEditRestaurantData={setEditRestaurantData}
            />

            <RestaurantDialogsSection
                isAddDialogOpen={isAddDialogOpen}
                setIsAddDialogOpen={setIsAddDialogOpen}
                editRestaurantData={editRestaurantData}
                setEditRestaurantData={setEditRestaurantData}
                deleteRestaurantId={deleteRestaurantId}
                setDeleteRestaurantId={setDeleteRestaurantId}
                refreshData={refreshData}
            />
        </div>
    );
}
