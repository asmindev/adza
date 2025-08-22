import React from "react";
import AddRestaurantDialog from "../components/AddRestaurantDialog";
import EditRestaurantDialog from "../components/EditRestaurantDialog";
import DeleteRestaurantDialog from "../components/DeleteRestaurantDialog";

export default function RestaurantDialogsSection({
    isAddDialogOpen,
    setIsAddDialogOpen,
    editRestaurantData,
    setEditRestaurantData,
    deleteRestaurantId,
    setDeleteRestaurantId,
    refreshData,
}) {
    return (
        <>
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
        </>
    );
}
