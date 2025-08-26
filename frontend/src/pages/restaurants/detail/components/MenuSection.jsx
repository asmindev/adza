import React from "react";
import { ChefHat } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import FoodItem from "./FoodItem";

function MenuSection({ restaurant }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
        >
            <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
                <ChefHat className="h-5 w-5 sm:h-6 sm:w-6 text-orange-500" />
                <h2 className="text-2xl sm:text-3xl font-bold text-foreground">
                    Menu
                </h2>
                <Badge variant="secondary" className="text-xs sm:text-sm">
                    {restaurant.foods?.length || 0} items
                </Badge>
            </div>

            {restaurant.foods && restaurant.foods.length > 0 ? (
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                    {restaurant.foods.map((food, index) => (
                        <FoodItem key={food.id} food={food} index={index} />
                    ))}
                </div>
            ) : (
                <Card className="border-0 shadow-lg">
                    <CardContent className="p-8 sm:p-12 text-center">
                        <ChefHat className="h-12 w-12 sm:h-16 sm:w-16 text-muted-foreground mx-auto mb-3 sm:mb-4" />
                        <h3 className="text-lg sm:text-xl font-semibold text-foreground mb-2">
                            No Menu Available
                        </h3>
                        <p className="text-muted-foreground text-sm sm:text-base">
                            This restaurant hasn't added any menu items yet.
                        </p>
                    </CardContent>
                </Card>
            )}
        </motion.div>
    );
}

export default MenuSection;
