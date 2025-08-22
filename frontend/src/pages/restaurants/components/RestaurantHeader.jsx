import React from "react";
import { motion } from "framer-motion";
import { Store, MapPin } from "lucide-react";

export default function RestaurantHeader({ totalCount }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-4"
        >
            <div className="flex items-center justify-center gap-3">
                <Store className="h-8 w-8 text-primary" />
                <h1 className="text-4xl font-bold text-foreground">Restoran</h1>
            </div>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Temukan Restoran terbaik dan jelajahi menu makanan lezat yang
                mereka tawarkan
            </p>

            {/* Stats */}
            <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                    <Store className="h-4 w-4" />
                    <span>{totalCount} Restoran</span>
                </div>
                <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    <span>Seluruh Indonesia</span>
                </div>
            </div>
        </motion.div>
    );
}
