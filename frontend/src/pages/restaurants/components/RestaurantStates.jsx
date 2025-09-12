import React from "react";
import { motion } from "framer-motion";
import { Store, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import RestaurantCard from "../RestaurantCard";

export const RestaurantLoadingSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array(6)
            .fill()
            .map((_, index) => (
                <Card key={index} className="h-80">
                    <CardContent className="p-6">
                        <div className="space-y-4">
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <Skeleton className="h-6 w-3/4 mb-2" />
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-2/3" />
                                </div>
                                <Skeleton className="h-6 w-16" />
                            </div>
                            <Skeleton className="h-4 w-1/2" />
                            <div className="space-y-2">
                                <Skeleton className="h-4 w-full" />
                                <Skeleton className="h-4 w-3/4" />
                                <Skeleton className="h-4 w-2/3" />
                            </div>
                            <Skeleton className="h-10 w-full" />
                        </div>
                    </CardContent>
                </Card>
            ))}
    </div>
);

export const RestaurantLoadingMore = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array(3)
            .fill()
            .map((_, index) => (
                <Card key={index} className="h-80">
                    <CardContent className="p-6">
                        <div className="space-y-4">
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <Skeleton className="h-6 w-3/4 mb-2" />
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-2/3" />
                                </div>
                                <Skeleton className="h-6 w-16" />
                            </div>
                            <Skeleton className="h-4 w-1/2" />
                            <div className="space-y-2">
                                <Skeleton className="h-4 w-full" />
                                <Skeleton className="h-4 w-3/4" />
                                <Skeleton className="h-4 w-2/3" />
                            </div>
                            <Skeleton className="h-10 w-full" />
                        </div>
                    </CardContent>
                </Card>
            ))}
    </div>
);

export const RestaurantErrorState = ({ onRetry }) => (
    <Card className="p-12 text-center">
        <CardContent>
            <Store className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="text-xl font-medium text-foreground mb-2">
                Gagal Memuat Restoran
            </h3>
            <p className="text-muted-foreground mb-4">
                Terjadi kesalahan saat memuat daftar restoran
            </p>
            <Button onClick={onRetry} variant="default">
                Coba Lagi
            </Button>
        </CardContent>
    </Card>
);

export const RestaurantEmptyState = ({ searchTerm, statusFilter }) => (
    <Card className="p-12 text-center">
        <CardContent>
            <Store className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
            <h3 className="text-xl font-medium text-foreground mb-2">
                {searchTerm || statusFilter !== "all"
                    ? "Tidak Ada Restoran Ditemukan"
                    : "Belum Ada Restoran"}
            </h3>
            <p className="text-muted-foreground">
                {searchTerm || statusFilter !== "all"
                    ? "Coba ubah kriteria pencarian atau filter Anda"
                    : "Belum ada restoran yang terdaftar di sistem"}
            </p>
        </CardContent>
    </Card>
);

export const RestaurantGrid = ({ restaurants }) => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {restaurants.map((restaurant, index) => (
            <motion.div
                key={restaurant.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
            >
                <RestaurantCard restaurant={restaurant} />
            </motion.div>
        ))}
    </div>
);

export const LoadMoreButton = ({ onLoadMore, isLoading, hasMore }) => {
    if (!hasMore) {
        return (
            <div className="text-center py-8">
                <p className="text-muted-foreground">
                    Semua restoran telah dimuat
                </p>
            </div>
        );
    }

    return (
        <div className="text-center py-8">
            <Button
                onClick={onLoadMore}
                disabled={isLoading}
                variant="outline"
                size="lg"
                className="min-w-32"
            >
                {isLoading ? (
                    <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Memuat...
                    </>
                ) : (
                    "Muat Lebih Banyak"
                )}
            </Button>
        </div>
    );
};

export const InfiniteScrollTrigger = React.forwardRef(
    ({ hasMore, isLoading }, ref) => (
        <div ref={ref} className="py-8">
            {hasMore && (
                <div className="flex justify-center">
                    {isLoading ? (
                        <div className="flex items-center gap-2 text-muted-foreground">
                            <Loader2 className="h-5 w-5 animate-spin" />
                            <span className="text-sm">Memuat restoran...</span>
                        </div>
                    ) : (
                        <div className="flex items-center gap-2 text-muted-foreground/60">
                            <div className="h-1 w-8 bg-border rounded-full"></div>
                            <span className="text-xs">
                                Scroll untuk memuat lebih banyak
                            </span>
                            <div className="h-1 w-8 bg-border rounded-full"></div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
);

InfiniteScrollTrigger.displayName = "InfiniteScrollTrigger";
