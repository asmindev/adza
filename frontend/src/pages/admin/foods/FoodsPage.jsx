import React, { useState } from "react";

// Component imports
import FoodPageHeader from "./sections/FoodPageHeader";
import FoodFilters from "./sections/FoodFilters";
import FoodTable from "./sections/FoodTable";
import FoodPagination from "./sections/FoodPagination";

// Dialog imports
import AddFoodDialog from "./components/AddFoodDialog";
import EditFoodDialog from "./components/EditFoodDialog";
import DeleteFoodDialog from "./components/DeleteFoodDialog";

// Custom hook
import { useFoods } from "./hooks/useFoods";

export default function FoodsPage() {
    // Dialog states
    const [addDialogOpen, setAddDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedFood, setSelectedFood] = useState(null);

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

    const handleEdit = (food) => {
        setSelectedFood(food);
        setEditDialogOpen(true);
    };

    const handleDelete = (food) => {
        setSelectedFood(food);
        setDeleteDialogOpen(true);
    };

    const handleSuccess = () => {
        refreshData(); // Revalidate the data
    };

    return (
        <div className="space-y-6">
            {/* Header Section */}
            <FoodPageHeader onAddFood={() => setAddDialogOpen(true)} />

            {/* Filters Section */}
            <FoodFilters
                searchTerm={searchTerm}
                setSearchTerm={handleSearch}
                statusFilter={statusFilter}
                setStatusFilter={handleStatusFilter}
                categoryFilter={categoryFilter}
                setCategoryFilter={handleCategoryFilter}
            />

            {/* Table Section */}
            <div>
                <FoodTable
                    foods={foods}
                    restaurantMap={restaurantMap}
                    isLoading={isLoading}
                    error={error}
                    pagination={pagination}
                    handleEdit={handleEdit}
                    handleDelete={handleDelete}
                />

                {/* Pagination */}
                <FoodPagination
                    pagination={pagination}
                    page={page}
                    setPage={setPage}
                />
            </div>

            {/* Dialogs */}
            <AddFoodDialog
                open={addDialogOpen}
                onOpenChange={setAddDialogOpen}
                onSuccess={handleSuccess}
            />

            <EditFoodDialog
                open={editDialogOpen}
                onOpenChange={setEditDialogOpen}
                foodData={selectedFood}
                onSuccess={handleSuccess}
            />

            <DeleteFoodDialog
                open={deleteDialogOpen}
                onOpenChange={setDeleteDialogOpen}
                food={selectedFood}
                onSuccess={handleSuccess}
            />
        </div>
    );
}
