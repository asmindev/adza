import React from "react";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import UserSearchBar from "../components/UserSearchBar";
import UserTable from "../components/UserTable";

export default function UserListSection({
    users,
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
    setUserDialogData,
    setDeleteUserId,
}) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Semua Pengguna</CardTitle>
                <CardDescription>
                    Kelola pengguna platform makanan Anda. Tambahkan pengguna
                    baru atau ubah yang sudah ada.
                </CardDescription>
                <UserSearchBar
                    searchTerm={searchTerm}
                    onSearch={handleSearch}
                />
            </CardHeader>
            <CardContent>
                <UserTable
                    data={users}
                    setEditUserData={setUserDialogData}
                    setDeleteUserId={setDeleteUserId}
                    sorting={sorting}
                    setSorting={setSorting}
                    pageIndex={pageIndex}
                    pageSize={pageSize}
                    totalPages={totalPages}
                    isLoading={isLoading}
                    setPageIndex={setPageIndex}
                    totalCount={totalCount}
                    searchTerm={searchTerm}
                />
            </CardContent>
        </Card>
    );
}
