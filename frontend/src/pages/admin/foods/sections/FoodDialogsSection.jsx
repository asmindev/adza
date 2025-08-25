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
    return (
        <>
            {/* Add Food Dialog */}
            <AddFoodDialog
                open={isAddDialogOpen}
                onOpenChange={setIsAddDialogOpen}
                onSuccess={refreshData}
            />

            {/* Edit Food Dialog */}
            <EditFoodDialog
                open={!!editFoodData}
                onOpenChange={(open) => !open && setEditFoodData(null)}
                foodData={editFoodData}
                onSuccess={refreshData}
            />

            {/* Delete Food Dialog */}
            <DeleteFoodDialog
                open={!!deleteFoodId}
                onOpenChange={(open) => !open && setDeleteFoodId(null)}
                foodId={deleteFoodId}
                onSuccess={refreshData}
            />
        </>
    );
}
