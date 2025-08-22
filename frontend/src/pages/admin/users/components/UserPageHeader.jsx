import React from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function UserPageHeader({ onAddUser }) {
    return (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">
                    Manajemen Pengguna
                </h1>
                <p className="text-muted-foreground">
                    Kelola pengguna platform makanan Anda
                </p>
            </div>
            <Button onClick={onAddUser} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Tambah Pengguna
            </Button>
        </div>
    );
}
