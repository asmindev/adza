import React, { useState } from "react";
import { Link } from "react-router";
import { Heart, ChefHat, MessageSquare, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import StarRating from "./StarRating";

function FoodItem({ food, index }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="h-full"
        >
            <Card className="h-full overflow-hidden hover:shadow-lg transition-all duration-300 p-0">
                <CardContent className="p-0 h-full">
                    {/* Mobile-optimized layout */}
                    <div className="p-3 sm:p-4 h-full">
                        {/* Food header - stacked on mobile */}
                        <div className="h-full flex flex-col sm:flex-row gap-3 sm:gap-4 relative pt-4 sm:pt-0">
                            {/* Food Image */}
                            {food.main_image ? (
                                <img
                                    src={food.main_image.image_url}
                                    alt={food.name}
                                    className="w-full h-32 sm:w-1/2 sm:h-full object-cover rounded-lg mb-3 sm:mb-0"
                                />
                            ) : (
                                <div className="w-full h-32 sm:w-20 sm:h-20 bg-gradient-to-br from-orange-200 via-red-200 to-pink-200 rounded-lg relative overflow-hidden flex-shrink-0">
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent"></div>
                                    <div className="absolute top-2 right-2 sm:top-1 sm:right-1">
                                        <TooltipProvider>
                                            <Tooltip>
                                                <TooltipTrigger asChild>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-7 w-7 sm:h-6 sm:w-6 p-0 bg-background/80 hover:bg-background rounded-full"
                                                    >
                                                        <Heart className="h-4 w-4 sm:h-3 sm:w-3 text-muted-foreground" />
                                                    </Button>
                                                </TooltipTrigger>
                                                <TooltipContent>
                                                    <p>Add to favorites</p>
                                                </TooltipContent>
                                            </Tooltip>
                                        </TooltipProvider>
                                    </div>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <ChefHat className="h-12 w-12 sm:h-8 sm:w-8 text-white/60" />
                                    </div>
                                    {/* Category badge on image for mobile */}
                                    <div className="absolute bottom-2 left-2 sm:hidden">
                                        <Badge
                                            variant="secondary"
                                            className="text-xs px-2 py-1"
                                        >
                                            {food.category}
                                        </Badge>
                                    </div>
                                </div>
                            )}

                            {/* Food Info */}
                            <div className="flex-1 min-w-0 h-full flex flex-col justify-between">
                                <div className="flex sm:flex-col flex-row justify-between items-start mb-2 ">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-medium sm:font-bold text-sm sm:text-base text-foreground leading-tight">
                                            {food.name}
                                        </h3>
                                        <div className="absolute sm:static -top-3 -right-1 flex gap-2 items-center text-sm text-muted-foreground mt-1">
                                            <StarRating
                                                rating={
                                                    food.ratings?.average || 0
                                                }
                                                showRating={false}
                                            />
                                            <span className="text-sm font-medium text-foreground">
                                                {food.ratings?.average?.toFixed(
                                                    1
                                                ) || 0}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="absolute -top-2 -left-3 sm:static text-right ml-2 sm:block">
                                        <div className="text-sm sm:text-lg font-bold text-green-600">
                                            Rp
                                            {food.price.toLocaleString("id-ID")}
                                        </div>
                                    </div>
                                </div>
                                <Link
                                    to={`/food/${food.id}`}
                                    className="w-full flex bg-primary hover:bg-primary/90 text-primary-foreground py-2 gap-2 rounded-lg justify-center items-center text-sm font-medium transition-all duration-300 group"
                                >
                                    Lihat Detail
                                    <ArrowRight className="size-4 group-hover:translate-x-1 transition-all duration-300" />
                                </Link>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}

export default FoodItem;
