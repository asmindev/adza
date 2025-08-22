import React, { useState, useEffect } from "react";
import { toast } from "sonner";
import useSWR from "swr";
import apiService from "@/dashboard/services/api";

// Component imports
import FoodPageHeader from "./sections/FoodPageHeader";
import FoodFilters from "./sections/FoodFilters";
import FoodTable from "./sections/FoodTable";
import FoodPagination from "./sections/FoodPagination";

// Dialog imports
import AddFoodDialog from "./components/AddFoodDialog";
import EditFoodDialog from "./components/EditFoodDialog";
import DeleteFoodDialog from "./components/DeleteFoodDialog";

export default function FoodsPage() {
    // State management
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [categoryFilter, setCategoryFilter] = useState("all");
    const [page, setPage] = useState(1);
    const pageSize = 50;

    // Dialog states
    const [addDialogOpen, setAddDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedFood, setSelectedFood] = useState(null);

    // Fetch foods data
    const { data, error, mutate, isLoading } = useSWR(
        [`/foods`, page, pageSize, searchTerm, statusFilter, categoryFilter],
        () =>
            apiService.foods.getAll(
                page,
                pageSize,
                searchTerm,
                statusFilter === "all" ? "" : statusFilter,
                categoryFilter === "all" ? "" : categoryFilter
            ),
        {
            revalidateOnFocus: false,
            onError: () => {
                toast.error("Gagal memuat data makanan");
            },
        }
    );

    const foods = data?.data?.data?.foods || [];
    const pagination = data?.data?.data?.pagination || {};

    // Fetch restaurants for restaurant name display
    const { data: restaurantsData } = useSWR(
        ["/restaurants/list"],
        () => apiService.restaurants.getAll(1, 1000, ""),
        {
            revalidateOnFocus: false,
        }
    );

    const restaurants = restaurantsData?.data?.data?.restaurants || [];

    // Create a restaurant lookup map for quick access
    const restaurantMap = restaurants.reduce((acc, restaurant) => {
        acc[restaurant.id] = restaurant.name;
        return acc;
    }, {});

    // Handle search with debounce
    useEffect(() => {
        const timer = setTimeout(() => {
            setPage(1); // Reset to first page when searching
        }, 300);

        return () => clearTimeout(timer);
    }, [searchTerm, statusFilter, categoryFilter]);

    const handleEdit = (food) => {
        setSelectedFood(food);
        setEditDialogOpen(true);
    };

    const handleDelete = (food) => {
        setSelectedFood(food);
        setDeleteDialogOpen(true);
    };

    const handleSuccess = () => {
        mutate(); // Revalidate the data
    };

    return (
        <div className="space-y-6">
            {/* Header Section */}
            <FoodPageHeader onAddFood={() => setAddDialogOpen(true)} />

            {/* Filters Section */}
            <FoodFilters
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                statusFilter={statusFilter}
                setStatusFilter={setStatusFilter}
                categoryFilter={categoryFilter}
                setCategoryFilter={setCategoryFilter}
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
