import React from "react";
import AddFoodDialog from "../components/AddFoodDialog";
import EditFoodDialog from "../components/EditFoodDialog";
import DeleteFoodDialog from "../components/DeleteFoodDialog";

export default function FoodDialogsSection({
    isAddDialogOpen,
    setIsAddDialogOpen,
    editFoodData,
    setEditFoodData,
    deleteFoodId,
    setDeleteFoodId,
    refreshData,
}) {
    // Explicit handlers for dialog state management
    const handleDeleteDialogChange = (open) => {
        if (!open) {
            setDeleteFoodId(null);
        }
    };

    const handleEditDialogChange = (open) => {
        if (!open) {
            setEditFoodData(null);
        }
    };

    return (
        <>
            {/* Add Food Dialog */}
            <AddFoodDialog
                open={isAddDialogOpen}
                onOpenChange={setIsAddDialogOpen}
                onSuccess={refreshData}
            />

            {/* Edit Food Dialog */}
            {editFoodData && (
                <EditFoodDialog
                    key={`edit-${editFoodData.id}`}
                    open={true}
                    onOpenChange={handleEditDialogChange}
                    foodData={editFoodData}
                    onSuccess={refreshData}
                />
            )}

            {/* Delete Food Dialog */}
            {deleteFoodId && (
                <DeleteFoodDialog
                    key={`delete-${deleteFoodId}`}
                    open={true}
                    onOpenChange={handleDeleteDialogChange}
                    foodId={deleteFoodId}
                    onSuccess={refreshData}
                />
            )}
        </>
    );
}
