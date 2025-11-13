import React from "react";

/**
 * Loading Section Component
 * Menampilkan skeleton loading untuk section
 */
export function SectionLoading({ title }) {
    return (
        <div className="container mx-auto px-4 py-8">
            {/* Section Title Skeleton */}
            {title && (
                <div className="mb-6">
                    <div className="h-8 w-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                </div>
            )}

            {/* Food Grid Skeleton */}
            <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {[...Array(8)].map((_, index) => (
                    <div
                        key={index}
                        className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-md"
                    >
                        {/* Image Skeleton */}
                        <div className="w-full h-48 bg-gray-200 dark:bg-gray-700 animate-pulse"></div>

                        {/* Content Skeleton */}
                        <div className="p-4 space-y-3">
                            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 animate-pulse"></div>
                            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 animate-pulse"></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
