import React, { useState } from "react";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import apiService from "@/lib/api";

export default function DeleteRestaurantDialog({
    open,
    onOpenChange,
    restaurantId,
    onSuccess,
}) {
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDelete = async () => {
        if (!restaurantId) return;

        setIsDeleting(true);
        try {
            await apiService.restaurants.delete(restaurantId);
            toast.success("Restoran berhasil dihapus");
            onSuccess?.();
            onOpenChange(false);
        } catch (error) {
            toast.error(
                error?.response?.data?.message || "Gagal menghapus restoran"
            );
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>
                        Apakah Anda yakin ingin menghapus?
                    </AlertDialogTitle>
                    <AlertDialogDescription>
                        Tindakan ini tidak dapat dibatalkan. Ini akan secara
                        permanen menghapus restoran ini dari database.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isDeleting}>
                        Batal
                    </AlertDialogCancel>
                    <AlertDialogAction
                        onClick={handleDelete}
                        className="bg-red-600 hover:bg-red-700"
                        disabled={isDeleting}
                    >
                        {isDeleting ? "Menghapus..." : "Hapus"}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}
