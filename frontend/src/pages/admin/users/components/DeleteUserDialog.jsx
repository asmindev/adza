import React from "react";
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

export default function DeleteUserDialog({
    open,
    onOpenChange,
    userId,
    onSuccess,
}) {
    const [isDeleting, setIsDeleting] = React.useState(false);

    const handleDelete = async () => {
        if (!userId) return;

        setIsDeleting(true);
        try {
            await apiService.users.delete(userId);
            toast.success("Pengguna berhasil dihapus");
            onOpenChange(false);
            if (onSuccess) onSuccess();
        } catch (error) {
            toast.error(error.message || "Gagal menghapus pengguna");
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Apakah Anda yakin?</AlertDialogTitle>
                    <AlertDialogDescription>
                        Ini akan menghapus permanen pengguna dan semua data
                        terkait. Tindakan ini tidak dapat dibatalkan.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isDeleting}>
                        Batal
                    </AlertDialogCancel>
                    <AlertDialogAction
                        onClick={handleDelete}
                        disabled={isDeleting}
                        className="bg-red-600 hover:bg-red-700"
                    >
                        {isDeleting ? "Menghapus..." : "Hapus"}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}
