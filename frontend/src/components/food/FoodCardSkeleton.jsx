import React from "react";
import { Skeleton } from "@/components/ui/skeleton";

const FoodCardSkeleton = () => {
    return (
        <div className="flex flex-col space-y-3">
            <Skeleton className="h-[200px] w-full rounded-lg" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <div className="flex space-x-2">
                <Skeleton className="h-8 w-8 rounded-full" />
                <Skeleton className="h-8 w-16" />
            </div>
        </div>
    );
};

export default FoodCardSkeleton;
