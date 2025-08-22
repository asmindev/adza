import React from "react";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

export default function RestaurantSearchBar({ searchTerm, onSearch }) {
    return (
        <div className="relative mt-4">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
                type="search"
                placeholder="Cari restoran..."
                value={searchTerm}
                onChange={onSearch}
                className="pl-8"
            />
        </div>
    );
}
