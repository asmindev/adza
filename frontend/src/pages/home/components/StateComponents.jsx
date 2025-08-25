import React from "react";

/**
 * Loading State Component
 * Menampilkan spinner saat data sedang loading
 */
export function LoadingState() {
    return (
        <div className="container mx-auto px-4 py-8">
            <div className="text-center">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">
                    Loading food data...
                </p>
            </div>
        </div>
    );
}

/**
 * Error State Component
 * Menampilkan pesan error ketika gagal memuat data
 */
export function ErrorState({ error }) {
    return (
        <div className="container mx-auto px-4 py-8">
            <div className="text-center">
                <h2 className="text-2xl font-bold text-red-600 mb-2">
                    Error Loading Data
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                    {error?.message ||
                        "Failed to load food data. Please try again later."}
                </p>
            </div>
        </div>
    );
}

/**
 * Empty State Component
 * Menampilkan pesan ketika tidak ada data
 */
export function EmptyState() {
    return (
        <div className="container mx-auto px-4 py-8">
            <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    No Food Items Found
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                    We couldn't find any food items at the moment. Please try
                    again later.
                </p>
            </div>
        </div>
    );
}
