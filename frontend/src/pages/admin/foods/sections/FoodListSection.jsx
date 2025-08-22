import React from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import FoodFilters from "./FoodFilters";
import FoodTable from "./FoodTable";
import FoodPagination from "./FoodPagination";

export default function FoodListSection({
    foods,
    restaurantMap,
    isLoading,
    error,
    pagination,
    page,
    setPage,
    searchTerm,
    statusFilter,
    categoryFilter,
    handleSearch,
    handleStatusFilter,
    handleCategoryFilter,
    setDeleteFoodId,
    setEditFoodData,
}) {
    // Handler for edit button click
    const handleEdit = (food) => {
        setEditFoodData({ ...food });
    };

    // Handler for delete button click
    const handleDelete = (food) => {
        setDeleteFoodId(food.id);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Daftar Makanan</CardTitle>
                <CardDescription>
                    Kelola koleksi makanan Anda. Anda dapat melihat, mengedit,
                    atau menghapus makanan.
                </CardDescription>
                <FoodFilters
                    searchTerm={searchTerm}
                    setSearchTerm={handleSearch}
                    statusFilter={statusFilter}
                    setStatusFilter={handleStatusFilter}
                    categoryFilter={categoryFilter}
                    setCategoryFilter={handleCategoryFilter}
                />
            </CardHeader>
            <CardContent>
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

                    <FoodPagination
                        pagination={pagination}
                        page={page}
                        setPage={setPage}
                    />
                </div>
            </CardContent>
        </Card>
    );
}
