import React from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function RouteNavigationSkeleton() {
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header Skeleton */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Skeleton className="h-8 w-20" />
                            <div>
                                <Skeleton className="h-6 w-40 mb-2" />
                                <Skeleton className="h-4 w-60" />
                            </div>
                        </div>
                        <Skeleton className="h-8 w-32 hidden sm:block" />
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Map Skeleton */}
                <div className="lg:col-span-2 order-2 lg:order-1">
                    <Card className="h-[500px] lg:h-[600px]">
                        <CardContent className="p-0 h-full flex items-center justify-center bg-gray-100 rounded-lg">
                            <div className="text-center">
                                <div className="animate-pulse">
                                    <div className="w-12 h-12 bg-gray-300 rounded-full mx-auto mb-4"></div>
                                    <Skeleton className="h-4 w-32 mx-auto" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Side Panel Skeleton */}
                <div className="order-1 lg:order-2 space-y-6">
                    {/* Destination Card */}
                    <Card>
                        <CardHeader>
                            <Skeleton className="h-6 w-20" />
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <Skeleton className="h-5 w-full" />
                            <Skeleton className="h-4 w-3/4" />
                            <Skeleton className="h-4 w-1/2" />
                        </CardContent>
                    </Card>

                    {/* Navigation Card */}
                    <Card>
                        <CardHeader>
                            <Skeleton className="h-6 w-24" />
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <Skeleton className="h-10 w-full" />
                            <Skeleton className="h-10 w-full" />
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
