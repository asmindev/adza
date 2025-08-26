import React from "react";
import { Link } from "react-router";
import { MapPin, Phone, Clock } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import StarRating from "./StarRating";

function RestaurantHero({ restaurant }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="overflow-hidden rounded-xl"
        >
            <Card className="border-0 shadow-lg p-0">
                <div className="h-48 sm:h-64 bg-gradient-to-br from-primary/20 to-primary/40 relative overflow-hidden">
                    <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-6 right-4 sm:right-6 text-foreground">
                        <h1 className="text-2xl sm:text-4xl font-bold mb-1 sm:mb-2 text-white drop-shadow-lg">
                            {restaurant.name}
                        </h1>
                        <div className="flex justify-between items-end sm:items-center ">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                                <div className="flex items-center gap-2 bg-background/90 backdrop-blur-sm rounded-full px-3 py-1 self-start">
                                    <StarRating
                                        rating={restaurant.rating?.average || 0}
                                        showRating={false}
                                    />
                                    <span className="font-semibold text-sm sm:text-base text-foreground">
                                        {restaurant.rating?.average?.toFixed(
                                            1
                                        ) || "0.0"}
                                    </span>
                                    <span className="text-xs sm:text-sm text-muted-foreground">
                                        ({restaurant.rating?.total || 0})
                                    </span>
                                </div>
                                <Badge
                                    variant={
                                        restaurant.is_active
                                            ? "default"
                                            : "destructive"
                                    }
                                >
                                    {restaurant.is_active ? "Buka" : "Tutup"}
                                </Badge>
                            </div>
                            {/* mapping categories */}
                            <div className="flex flex-wrap gap-2">
                                {restaurant.categories.map((category) => (
                                    <Badge
                                        key={category.id}
                                        className={"text-xs"}
                                    >
                                        {category.name}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <CardContent className="p-4 sm:p-5">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 text-sm mb-4">
                        <div className="flex items-center gap-2 bg-muted/50 rounded-xl px-3 py-2">
                            <MapPin className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <span className="line-clamp-1 text-foreground">
                                {restaurant.address}
                            </span>
                        </div>
                        <div className="flex items-center gap-2 bg-muted/50 rounded-xl px-3 py-2">
                            <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <span className="text-foreground">
                                09:00 - 22:00
                            </span>
                        </div>
                    </div>

                    <Separator className="my-4" />

                    {/* Location Button */}
                    <Button asChild className="w-full sm:w-auto">
                        <Link to={`/navigation/restaurant/${restaurant.id}`}>
                            <MapPin className="mr-2 h-4 w-4" />
                            Lihat Lokasi & Rute
                        </Link>
                    </Button>
                </CardContent>
            </Card>
        </motion.div>
    );
}

export default RestaurantHero;
