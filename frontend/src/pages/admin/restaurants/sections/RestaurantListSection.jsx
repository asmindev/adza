import React from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import RestaurantSearchBar from "../components/RestaurantSearchBar";
import RestaurantTable from "../components/RestaurantTable";
import { createRestaurantColumns } from "../components/RestaurantTableColumns";

export default function RestaurantListSection({
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
    setDeleteRestaurantId,
    setEditRestaurantData,
}) {
    // Create table columns with delete and edit handlers
    const columns = createRestaurantColumns(
        setDeleteRestaurantId,
        setEditRestaurantData
    );

    return (
        <Card>
            <CardHeader>
                <CardTitle>Rumah Makan</CardTitle>
                <CardDescription>
                    Kelola koleksi restoran Anda. Anda dapat melihat, mengedit,
                    atau menghapus restoran.
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
    );
}
