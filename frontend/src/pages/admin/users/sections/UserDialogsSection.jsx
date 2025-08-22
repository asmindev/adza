import React from "react";
import UserDialog from "../components/UserDialog";
import DeleteUserDialog from "../components/DeleteUserDialog";

export default function UserDialogsSection({
    userDialogData,
    setUserDialogData,
    deleteUserId,
    setDeleteUserId,
    refreshData,
}) {
    return (
        <>
            {/* User Dialog (Add/Edit) */}
            {userDialogData && (
                <UserDialog
                    open={!!userDialogData}
                    onOpenChange={(open) => !open && setUserDialogData(null)}
                    isNew={userDialogData.isNew}
                    userData={userDialogData.userData}
                    onSuccess={refreshData}
                />
            )}

            {/* Delete User Dialog */}
            {deleteUserId && (
                <DeleteUserDialog
                    open={!!deleteUserId}
                    onOpenChange={(open) => !open && setDeleteUserId(null)}
                    userId={deleteUserId}
                    onSuccess={refreshData}
                />
            )}
        </>
    );
}
