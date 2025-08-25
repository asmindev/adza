import React from "react";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function FoodPageHeader({ onAddFood }) {
    return (
        <div className="flex items-center justify-between">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Foods</h2>
                <p className="text-muted-foreground">
                    Kelola koleksi makanan di platform Anda.
                </p>
            </div>
            <Button onClick={onAddFood}>
                <Plus className="mr-2 h-4 w-4" /> Tambah Makanan
            </Button>
        </div>
    );
}
