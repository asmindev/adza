import React from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function FoodPageHeader({ onAddFood }) {
    return (
        <div className="flex items-center justify-between">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">
                    Manajemen Makanan
                </h1>
                <p className="text-muted-foreground">
                    Kelola koleksi makanan Anda
                </p>
            </div>
            <Button onClick={onAddFood}>
                <Plus className="h-4 w-4 mr-2" />
                Tambah Makanan
            </Button>
        </div>
    );
}
