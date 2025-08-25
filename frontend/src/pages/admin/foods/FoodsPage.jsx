import React, { useState } from "react";

// Import sections
import FoodPageHeader from "./components/FoodPageHeader";
import FoodListSection from "./sections/FoodListSection";
import FoodDialogsSection from "./sections/FoodDialogsSection";
import { useFoods } from "./hooks/useFoods";

export default function FoodsPage() {
    // Dialog state
    const [deleteFoodId, setDeleteFoodId] = useState(null);
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [editFoodData, setEditFoodData] = useState(null);

    // Use custom hook for food data management
    const {
        foods,
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
    } = useFoods();

    return (
        <div className="space-y-6">
            <FoodPageHeader onAddFood={() => setIsAddDialogOpen(true)} />

            <FoodListSection
                foods={foods}
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
                setDeleteFoodId={setDeleteFoodId}
                setEditFoodData={setEditFoodData}
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

FoodsPage.breadcrumbs = [{ label: "Foods" }];
