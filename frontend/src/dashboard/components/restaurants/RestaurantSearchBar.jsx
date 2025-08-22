import React from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

export default function RestaurantSearchBar({
    searchTerm,
    onSearch,
    placeholder = "Cari restoran...",
}) {
    return (
        <div className="flex w-full max-w-sm items-center space-x-2 mt-4">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
                placeholder={placeholder}
                value={searchTerm}
                onChange={onSearch}
                className="h-9"
            />
        </div>
    );
}
