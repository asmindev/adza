import React from "react";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

export default function UserSearchBar({ searchTerm, onSearch }) {
    return (
        <div className="flex w-full max-w-sm items-center space-x-2 mt-4">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
                placeholder="Cari pengguna..."
                value={searchTerm}
                onChange={onSearch}
                className="h-9"
            />
        </div>
    );
}
