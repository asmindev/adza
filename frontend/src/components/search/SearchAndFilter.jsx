import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Heart, X } from "lucide-react";
import CategoryBadge from "./CategoryBadge";

export default function SearchAndFilter({
    onSearch,
    onToggleFavorites,
    onClearFilters,
    filter = {
        searchQuery: "",
    },
    showFavoritesOnly = false,
    categories = [],
}) {
    const [localSearchQuery, setLocalSearchQuery] = useState(
        filter?.searchQuery || ""
    );
    const [selectedCategory, setSelectedCategory] = useState("");
    // Add a ref for the scrollable container
    const scrollContainerRef = React.useRef(null);
    // Object to store refs for each category item
    const categoryRefs = React.useRef({});

    // Effect to update localSearchQuery if filter.searchQuery changes from parent
    // and it's not a category selection
    useEffect(() => {
        if (filter?.searchQuery !== selectedCategory) {
            setLocalSearchQuery(filter?.searchQuery || "");
        }
        // If filter.searchQuery is empty, it might mean filters were cleared externally
        if (!filter?.searchQuery) {
            setSelectedCategory("");
        }
    }, [filter?.searchQuery]);

    const handleSearchChange = (e) => {
        const value = e.target.value;
        setLocalSearchQuery(value);
        setSelectedCategory(""); // Clear category if user types in search
        if (onSearch) onSearch(value);
    };

    const handleCategoryClick = (category) => {
        // Center the clicked category in the scroll container
        if (categoryRefs.current[category] && scrollContainerRef.current) {
            const container = scrollContainerRef.current;
            const element = categoryRefs.current[category];

            // Calculate positions
            const containerWidth = container.offsetWidth;
            const elementWidth = element.offsetWidth;
            const elementOffsetLeft = element.offsetLeft;

            // Calculate the scroll position to center the element
            const scrollPosition =
                elementOffsetLeft - containerWidth / 2 + elementWidth / 2;

            // Smoothly scroll to the calculated position
            container.scrollTo({
                left: scrollPosition,
                behavior: "smooth",
            });
        }

        if (selectedCategory === category) {
            setSelectedCategory("");
            setLocalSearchQuery(""); // Clear text search when deselecting category
            if (onSearch) onSearch(""); // Clear search in parent
        } else {
            setSelectedCategory(category);
            setLocalSearchQuery(category); // Set text search to category name
            if (onSearch) onSearch(category);
        }
    };

    const internalClearFilters = () => {
        setLocalSearchQuery("");
        setSelectedCategory("");
        if (onClearFilters) {
            onClearFilters(); // Call parent's clear function
        } else if (onSearch) {
            onSearch(""); // Fallback if onClearFilters is not provided
        }
    };

    // Use safe access with optional chaining and fallback values
    const hasActiveFilters = !!filter?.searchQuery || !!selectedCategory;

    return (
        <motion.div
            className="w-full sm:p-4 mb-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
        >
            <div className="flex flex-col sm:flex-row-reverse items-center gap-4 sm:justify-between">
                <div className="flex flex-col sm:flex-row items-center sm:w-62 w-full">
                    <div className="relative w-full">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 h-4 w-4" />
                        <Input
                            type="text"
                            placeholder="Cari makanan, kategori..."
                            className="pl-10 pr-4 py-2 w-full text-gray-600"
                            value={localSearchQuery}
                            onChange={handleSearchChange}
                        />
                    </div>

                    {/* {onToggleFavorites && (
                    <Button
                        variant="outline"
                        className={`min-w-24 ${
                            showFavoritesOnly
                                ? "bg-pink-100 hover:bg-pink-200 border-pink-300 text-pink-700 dark:bg-pink-900/30 dark:hover:bg-pink-900/50 dark:border-pink-800 dark:text-pink-300"
                                : "bg-orange-50 hover:bg-orange-100 border-orange-200 text-orange-700 dark:bg-orange-900/30 dark:hover:bg-orange-900/50 dark:border-orange-800 dark:text-orange-300"
                        }`}
                        onClick={onToggleFavorites}
                    >
                        <Heart
                            className={`mr-2 h-4 w-4 ${
                                showFavoritesOnly ? "fill-pink-500" : ""
                            }`}
                        />
                        {showFavoritesOnly ? "All Recipes" : "Favorites Only"}
                    </Button>
                )} */}

                    {/* {hasActiveFilters && ( // Use internalClearFilters for the button
                        <Button
                            variant="ghost"
                            className="min-w-24 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
                            onClick={internalClearFilters}
                        >
                            <X className="mr-2 h-4 w-4" />
                            Clear
                        </Button>
                    )} */}
                </div>

                <motion.div
                    ref={scrollContainerRef}
                    className="flex flex-nowrap gap-2 items-center overflow-x-auto py-1 w-full max-w-full no-scrollbar sm:w-1/2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ staggerChildren: 0.05 }}
                    drag="x"
                    dragConstraints={{ left: 0, right: 0 }}
                    dragElastic={0.2}
                    whileTap={{ cursor: "grabbing" }}
                >
                    {categories.map((category, index) => (
                        <motion.div
                            key={category}
                            ref={(el) => (categoryRefs.current[category] = el)}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{
                                opacity: 1,
                                x: 0,
                                scale: selectedCategory === category ? 1.05 : 1,
                            }}
                            whileHover={{ scale: 1.05 }}
                            transition={{
                                delay: index * 0.05,
                                type: "spring",
                                stiffness: 120,
                            }}
                        >
                            <CategoryBadge
                                category={category}
                                onClick={handleCategoryClick}
                                isActive={selectedCategory === category}
                            />
                        </motion.div>
                    ))}
                </motion.div>
            </div>
        </motion.div>
    );
}
