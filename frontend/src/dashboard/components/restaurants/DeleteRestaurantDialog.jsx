import React from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import apiService from "@/dashboard/services/api";

export default function DeleteRestaurantDialog({
    open,
    onOpenChange,
    restaurantId,
    onSuccess,
}) {
    const handleDeleteRestaurant = async () => {
        if (!restaurantId) return;

        try {
            await apiService.restaurants.delete(restaurantId);
            toast.success("Restoran berhasil dihapus");
            onSuccess();
            onOpenChange(false);
        } catch (error) {
            toast.error(
                error?.response?.data?.message || "Gagal menghapus restoran"
            );
        }
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-md mx-4">
                <h3 className="text-lg font-semibold mb-2">Konfirmasi Hapus</h3>
                <p className="text-muted-foreground mb-4">
                    Apakah Anda yakin ingin menghapus restoran ini? Tindakan ini
                    tidak dapat dibatalkan.
                </p>
                <div className="flex justify-end space-x-2">
                    <Button
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                    >
                        Batal
                    </Button>
                    <Button
                        variant="destructive"
                        onClick={handleDeleteRestaurant}
                    >
                        Hapus
                    </Button>
                </div>
            </div>
        </div>
    );
}
