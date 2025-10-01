import React from "react";

export default function LoadingState() {
    return (
        <div className="fixed inset-0 bg-white flex justify-center items-center min-h-screen z-50">
            <div className="flex flex-col items-center space-y-6">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent"></div>
                <div className="text-xl font-semibold text-gray-700 animate-pulse">
                    Loading recommendations...
                </div>
            </div>
        </div>
    );
}
