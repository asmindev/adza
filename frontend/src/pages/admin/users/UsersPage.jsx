import React, { useState } from "react";

// Import custom hooks
import { useUsers } from "./hooks/useUsers";

// Import sections and components
import UserPageHeader from "./components/UserPageHeader";
import UserListSection from "./sections/UserListSection";
import UserDialogsSection from "./sections/UserDialogsSection";

export default function UsersPage() {
    // Dialog state
    const [userDialogData, setUserDialogData] = useState(null);
    const [deleteUserId, setDeleteUserId] = useState(null);

    // Use custom hook for user data management
    const {
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
        refreshData,
    } = useUsers();

    return (
        <div className="space-y-6">
            <UserPageHeader
                onAddUser={() => setUserDialogData({ isNew: true })}
            />

            <UserListSection
                users={users}
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
                setUserDialogData={setUserDialogData}
                setDeleteUserId={setDeleteUserId}
            />

            <UserDialogsSection
                userDialogData={userDialogData}
                setUserDialogData={setUserDialogData}
                deleteUserId={deleteUserId}
                setDeleteUserId={setDeleteUserId}
                refreshData={refreshData}
            />
        </div>
    );
}
