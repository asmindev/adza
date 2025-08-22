import React, { useState } from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";

// Import modular components
import RestaurantPageHeader from "@/dashboard/components/restaurants/RestaurantPageHeader";
import RestaurantSearchBar from "@/dashboard/components/restaurants/RestaurantSearchBar";
import RestaurantTable from "@/dashboard/components/restaurants/RestaurantTable";
import DeleteRestaurantDialog from "@/dashboard/components/restaurants/DeleteRestaurantDialog";
import AddRestaurantDialog from "@/dashboard/components/restaurants/AddRestaurantDialog";
import EditRestaurantDialog from "@/dashboard/components/restaurants/EditRestaurantDialog";
import { createRestaurantColumns } from "@/dashboard/components/restaurants/RestaurantTableColumns";
import { useRestaurants } from "@/dashboard/hooks/useRestaurants";

export default function RestaurantsPage() {
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

    // Create table columns with delete and edit handlers
    const columns = createRestaurantColumns(
        setDeleteRestaurantId,
        setEditRestaurantData
    );

    return (
        <div className="space-y-6">
            <RestaurantPageHeader
                onAddRestaurant={() => setIsAddDialogOpen(true)}
            />

            <Card>
                <CardHeader>
                    <CardTitle>Rumah Makan</CardTitle>
                    <CardDescription>
                        Kelola koleksi restoran Anda. Anda dapat melihat,
                        mengedit, atau menghapus restoran.
                    </CardDescription>
                    <RestaurantSearchBar
                        searchTerm={searchTerm}
                        onSearch={handleSearch}
                    />
                </CardHeader>
                <CardContent>
                    <RestaurantTable
                        data={restaurants}
                        columns={columns}
                        sorting={sorting}
                        setSorting={setSorting}
                        pageIndex={pageIndex}
                        pageSize={pageSize}
                        totalPages={totalPages}
                        isLoading={isLoading}
                        setPageIndex={setPageIndex}
                        totalCount={totalCount}
                    />
                </CardContent>
            </Card>

            {/* Add Restaurant Dialog */}
            <AddRestaurantDialog
                open={isAddDialogOpen}
                onOpenChange={setIsAddDialogOpen}
                onSuccess={refreshData}
            />

            {/* Edit Restaurant Dialog */}
            <EditRestaurantDialog
                open={!!editRestaurantData}
                onOpenChange={(open) => !open && setEditRestaurantData(null)}
                restaurantData={editRestaurantData}
                onSuccess={refreshData}
            />

            {/* Delete Restaurant Dialog */}
            <DeleteRestaurantDialog
                open={!!deleteRestaurantId}
                onOpenChange={(open) => !open && setDeleteRestaurantId(null)}
                restaurantId={deleteRestaurantId}
                onSuccess={refreshData}
            />
        </div>
    );
}
