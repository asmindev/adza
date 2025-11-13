import React from "react";
import { useNavigate } from "react-router";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import FoodSearchBar from "../components/FoodSearchBar";
import FoodTable from "../components/FoodTable";
import PageSizeSelector from "../components/PageSizeSelector";
import { createFoodColumns } from "../components/FoodTableColumns";

export default function FoodListSection({
    foods,
    totalCount,
    totalPages,
    isLoading,
    pageIndex,
    pageSize,
    setPageIndex,
    handlePageSizeChange,
    searchTerm,
    handleSearch,
    sorting,
    setSorting,
    setDeleteFoodId,
    setEditFoodData,
}) {
    const navigate = useNavigate();

    // Create table columns with delete and edit handlers
    const columns = createFoodColumns(
        setDeleteFoodId,
        setEditFoodData,
        navigate
    );

    return (
        <Card>
            <CardHeader>
                <CardTitle>Daftar Makanan</CardTitle>
                <CardDescription>
                    Kelola koleksi makanan Anda. Anda dapat melihat, mengedit,
                    atau menghapus makanan.
                </CardDescription>
                <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mt-4">
                    <FoodSearchBar
                        searchTerm={searchTerm}
                        onSearch={handleSearch}
                    />
                    <PageSizeSelector
                        pageSize={pageSize}
                        onPageSizeChange={handlePageSizeChange}
                    />
                </div>
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
