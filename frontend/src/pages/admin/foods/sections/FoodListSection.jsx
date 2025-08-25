import React from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import FoodSearchBar from "../components/FoodSearchBar";
import FoodTable from "../components/FoodTable";
import { createFoodColumns } from "../components/FoodTableColumns";

export default function FoodListSection({
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
    setDeleteFoodId,
    setEditFoodData,
}) {
    // Create table columns with delete and edit handlers
    const columns = createFoodColumns(setDeleteFoodId, setEditFoodData);

    return (
        <Card>
            <CardHeader>
                <CardTitle>Daftar Makanan</CardTitle>
                <CardDescription>
                    Kelola koleksi makanan Anda. Anda dapat melihat, mengedit,
                    atau menghapus makanan.
                </CardDescription>
                <FoodSearchBar
                    searchTerm={searchTerm}
                    onSearch={handleSearch}
                />
            </CardHeader>
            <CardContent>
                <FoodTable
                    data={foods}
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
