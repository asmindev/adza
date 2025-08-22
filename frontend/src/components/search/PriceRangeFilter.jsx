import React, { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { X, ChevronDown, ChevronUp } from "lucide-react";

export default function PriceRangeFilter({
    onPriceChange,
    initialMinPrice = 0,
    initialMaxPrice = 100000,
    minPrice = 0,
    maxPrice = 100000,
}) {
    const [priceRange, setPriceRange] = useState([
        initialMinPrice,
        initialMaxPrice,
    ]);
    const [isExpanded, setIsExpanded] = useState(true);

    useEffect(() => {
        setPriceRange([initialMinPrice, initialMaxPrice]);
    }, [initialMinPrice, initialMaxPrice]);

    const handlePriceChange = (field, value) => {
        const numValue = parseInt(value) || 0;
        let newRange;

        if (field === "min") {
            newRange = [numValue, priceRange[1]];
        } else {
            newRange = [priceRange[0], numValue];
        }

        setPriceRange(newRange);
        if (onPriceChange) {
            onPriceChange({
                min_price: newRange[0],
                max_price: newRange[1],
            });
        }
    };

    const resetFilter = () => {
        setPriceRange([minPrice, maxPrice]);
        if (onPriceChange) {
            onPriceChange({
                min_price: minPrice,
                max_price: maxPrice,
            });
        }
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat("id-ID", {
            style: "currency",
            currency: "IDR",
            minimumFractionDigits: 0,
        }).format(price);
    };

    const hasFilter = priceRange[0] !== minPrice || priceRange[1] !== maxPrice;

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg border">
            {/* Header - Always visible */}
            <div className="flex items-center justify-between p-4 pb-3">
                <div className="flex items-center gap-2">
                    <h3 className="font-medium text-sm">Filter Harga</h3>
                    {hasFilter && (
                        <div className="h-2 w-2 rounded-full bg-primary"></div>
                    )}
                </div>
                <div className="flex items-center gap-1">
                    {hasFilter && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={resetFilter}
                            className="h-6 px-2 text-xs"
                        >
                            <X className="h-3 w-3 mr-1" />
                            Reset
                        </Button>
                    )}
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="h-6 px-2"
                    >
                        {isExpanded ? (
                            <ChevronUp className="h-4 w-4" />
                        ) : (
                            <ChevronDown className="h-4 w-4" />
                        )}
                    </Button>
                </div>
            </div>

            {/* Collapsible Content */}
            {isExpanded && (
                <div className="px-4 pb-4 space-y-3">
                    {/* Price Inputs */}
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-xs text-gray-600 dark:text-gray-400 mb-1 block">
                                Min
                            </label>
                            <Input
                                type="number"
                                placeholder="0"
                                value={priceRange[0]}
                                onChange={(e) =>
                                    handlePriceChange("min", e.target.value)
                                }
                                className="h-9"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-gray-600 dark:text-gray-400 mb-1 block">
                                Max
                            </label>
                            <Input
                                type="number"
                                placeholder="100000"
                                value={priceRange[1]}
                                onChange={(e) =>
                                    handlePriceChange("max", e.target.value)
                                }
                                className="h-9"
                            />
                        </div>
                    </div>

                    {/* Quick Options */}
                    <div className="grid grid-cols-3 gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                setPriceRange([0, 25000]);
                                onPriceChange &&
                                    onPriceChange({
                                        min_price: 0,
                                        max_price: 25000,
                                    });
                            }}
                            className="h-8 text-xs"
                        >
                            &lt; 25k
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                setPriceRange([25000, 50000]);
                                onPriceChange &&
                                    onPriceChange({
                                        min_price: 25000,
                                        max_price: 50000,
                                    });
                            }}
                            className="h-8 text-xs"
                        >
                            25k-50k
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                setPriceRange([50000, 100000]);
                                onPriceChange &&
                                    onPriceChange({
                                        min_price: 50000,
                                        max_price: 100000,
                                    });
                            }}
                            className="h-8 text-xs"
                        >
                            &gt; 50k
                        </Button>
                    </div>

                    {/* Current Range */}
                    {hasFilter && (
                        <div className="text-center text-xs text-gray-500 bg-gray-50 dark:bg-gray-700 rounded py-2">
                            {formatPrice(priceRange[0])} -{" "}
                            {formatPrice(priceRange[1])}
                        </div>
                    )}
                </div>
            )}

            {/* Collapsed state info */}
            {!isExpanded && hasFilter && (
                <div className="px-4 pb-3">
                    <div className="text-center text-xs text-gray-500 bg-gray-50 dark:bg-gray-700 rounded py-2">
                        {formatPrice(priceRange[0])} -{" "}
                        {formatPrice(priceRange[1])}
                    </div>
                </div>
            )}
        </div>
    );
}
