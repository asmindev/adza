import React from "react";
import { Skeleton } from "@/components/ui/skeleton";

function LoadingState() {
    return (
        <div className="min-h-screen bg-background">
            <div className="max-w-6xl mx-auto p-4">
                <Skeleton className="h-8 w-32 mb-6" />
                <Skeleton className="h-64 w-full mb-8 rounded-2xl" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[...Array(6)].map((_, i) => (
                        <Skeleton key={i} className="h-80 rounded-xl" />
                    ))}
                </div>
            </div>
        </div>
    );
}

export default LoadingState;
