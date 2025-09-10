import React, { useState, useCallback } from "react";
import { Search, X } from "lucide-react";

/**
 * Search Bar Component untuk mencari makanan
 * @param {Object} props - Component props
 * @param {Function} props.onSearch - Callback ketika pencarian dilakukan
 * @param {string} props.placeholder - Placeholder text untuk input
 * @param {string} props.value - Current search value
 * @param {boolean} props.disabled - Whether search is disabled
 */
export function SearchBar({
    onSearch,
    placeholder = "Cari makanan...",
    value = "",
    disabled = false,
}) {
    const [searchValue, setSearchValue] = useState(value);

    const handleSubmit = useCallback(
        (e) => {
            e.preventDefault();
            onSearch?.(searchValue.trim());
        },
        [searchValue, onSearch]
    );

    const handleClear = useCallback(() => {
        setSearchValue("");
        onSearch?.("");
    }, [onSearch]);

    const handleInputChange = useCallback((e) => {
        setSearchValue(e.target.value);
    }, []);

    return (
        <div className="relative w-full max-w-md mx-auto">
            <form onSubmit={handleSubmit} className="relative">
                <div className="relative">
                    {/* Search Icon */}
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />

                    {/* Search Input */}
                    <input
                        type="text"
                        value={searchValue}
                        onChange={handleInputChange}
                        placeholder={placeholder}
                        disabled={disabled}
                        className="w-full pl-10 pr-10 py-2 rounded-lg disabled:cursor-not-allowed border"
                    />

                    {/* Clear Button */}
                    {searchValue && (
                        <button
                            type="button"
                            onClick={handleClear}
                            disabled={disabled}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2
                                       text-gray-400 hover:text-gray-600 dark:hover:text-gray-300
                                       disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    )}
                </div>

                {/* Hidden submit button for form submission */}
                <button type="submit" className="sr-only">
                    Search
                </button>
            </form>
        </div>
    );
}

/**
 * Search Section Component dengan title dan search bar
 * @param {Object} props - Component props
 * @param {Function} props.onSearch - Callback ketika pencarian dilakukan
 * @param {string} props.searchValue - Current search value
 * @param {boolean} props.isLoading - Whether search is in progress
 */
export function SearchSection({
    onSearch,
    searchValue = "",
    isLoading = false,
}) {
    return (
        <div className="container mx-auto px-4">
            <div className="text-center">
                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-4">
                    Cari Makanan Favorit Anda
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Temukan berbagai pilihan makanan lezat di Kendari
                </p>

                <SearchBar
                    onSearch={onSearch}
                    value={searchValue}
                    disabled={isLoading}
                    placeholder="Cari nama makanan..."
                />

                {/* Search Results Info */}
                {searchValue && (
                    <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                        {isLoading ? (
                            <span>Mencari "{searchValue}"...</span>
                        ) : (
                            <span>Hasil pencarian untuk "{searchValue}"</span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
