import React from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function RestaurantPageHeader({ onAddRestaurant }) {
    const handleAddClick = () => {
        if (onAddRestaurant) {
            onAddRestaurant();
        } else {
            toast.info("Fitur tambah restoran akan segera tersedia");
        }
    };

    return (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
            <h1 className="text-3xl font-bold tracking-tight">
                Manajemen Restoran
            </h1>
            <Button onClick={handleAddClick} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Tambah Restoran
            </Button>
        </div>
    );
}
