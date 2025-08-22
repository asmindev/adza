import React from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function RestaurantSummary({
    filteredCount,
    searchTerm,
    onResetFilters,
}) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex items-center justify-between"
        >
            <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-sm">
                    {filteredCount} restoran ditemukan
                </Badge>
                {searchTerm && (
                    <Badge variant="secondary" className="text-sm">
                        "{searchTerm}"
                    </Badge>
                )}
            </div>

            {filteredCount > 0 && (
                <Button variant="outline" size="sm" onClick={onResetFilters}>
                    Reset Filter
                </Button>
            )}
        </motion.div>
    );
}
