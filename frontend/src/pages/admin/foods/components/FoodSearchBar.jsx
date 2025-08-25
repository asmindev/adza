import React from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

export default function FoodSearchBar({ searchTerm, onSearch }) {
    return (
        <div className="relative">
            <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
                placeholder="Cari makanan..."
                value={searchTerm}
                onChange={onSearch}
                className="pl-8"
            />
        </div>
    );
}
