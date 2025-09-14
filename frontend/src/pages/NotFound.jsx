import React from "react";
import { Link } from "react-router";
import { Home } from "lucide-react";

export default function NotFound() {
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
            <div className="max-w-md mx-auto text-center">
                {/* 404 Number */}
                <div className="mb-8">
                    <h1 className="text-8xl font-bold text-gray-300 dark:text-gray-600">
                        404
                    </h1>
                </div>

                {/* Main Content */}
                <div className="space-y-6">
                    {/* Title */}
                    <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                        Halaman Tidak Ditemukan
                    </h2>

                    {/* Description */}
                    <p className="text-gray-600 dark:text-gray-400">
                        Halaman yang Anda cari tidak dapat ditemukan.
                    </p>

                    {/* Back to Home Button */}
                    <div className="pt-4">
                        <Link
                            to="/"
                            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                        >
                            <Home className="w-4 h-4" />
                            Kembali ke Beranda
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
