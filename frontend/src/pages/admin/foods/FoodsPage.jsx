import React, { useState } from "react";

// Import sections
import FoodPageHeader from "./sections/FoodPageHeader";
import FoodListSection from "./sections/FoodListSection";
import FoodDialogsSection from "./sections/FoodDialogsSection";

// Custom hook
import { useFoods } from "./hooks/useFoods";

export default function FoodsPage() {
    // Dialog states
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [editFoodData, setEditFoodData] = useState(null);
    const [deleteFoodId, setDeleteFoodId] = useState(null);

    // Use custom hook for food data management
    const {
        foods,
        pagination,
        restaurantMap,
        isLoading,
        error,
        page,
        setPage,
        searchTerm,
        statusFilter,
        categoryFilter,
        handleSearch,
        handleStatusFilter,
        handleCategoryFilter,
        refreshData,
    } = useFoods();

    return (
        <div className="space-y-6">
            {/* Header Section */}
            <FoodPageHeader onAddFood={() => setIsAddDialogOpen(true)} />

            {/* Food List Section (includes filters, table, and pagination) */}
            <FoodListSection
                foods={foods}
                restaurantMap={restaurantMap}
                isLoading={isLoading}
                error={error}
                pagination={pagination}
                page={page}
                setPage={setPage}
                searchTerm={searchTerm}
                statusFilter={statusFilter}
                categoryFilter={categoryFilter}
                handleSearch={handleSearch}
                handleStatusFilter={handleStatusFilter}
                handleCategoryFilter={handleCategoryFilter}
                setEditFoodData={setEditFoodData}
                setDeleteFoodId={setDeleteFoodId}
            />

            <FoodDialogsSection
                isAddDialogOpen={isAddDialogOpen}
                setIsAddDialogOpen={setIsAddDialogOpen}
                editFoodData={editFoodData}
                setEditFoodData={setEditFoodData}
                deleteFoodId={deleteFoodId}
                setDeleteFoodId={setDeleteFoodId}
                refreshData={refreshData}
            />
        </div>
    );
}
