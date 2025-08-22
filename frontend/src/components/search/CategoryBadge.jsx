import React from "react";
import { cn } from "@/lib/utils";

export default function CategoryBadge({ category, onClick, isActive }) {
    const handleClick = () => {
        if (onClick) onClick(category);
    };

    return (
        <button
            onClick={handleClick}
            className={cn(
                "px-3 py-1 rounded-full text-sm transition-colors duration-300 text-nowrap",
                isActive
                    ? "bg-accent/10 text-accent"
                    : "bg-muted text-muted-foreground"
            )}
        >
            {category}
        </button>
    );
}
