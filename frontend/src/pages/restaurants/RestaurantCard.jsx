import React from "react";
import { Link } from "react-router";
import { motion } from "framer-motion";
import { Star, MapPin, Phone, Utensils, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function RestaurantCard({ restaurant }) {
    if (!restaurant) return null;

    const averageRating = restaurant?.rating?.average || 0;
    const totalRatings = restaurant?.rating?.total || 0;
    const foodsCount = restaurant?.foods?.length || 0;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -5 }}
            transition={{ duration: 0.2 }}
        >
            <Card className="h-full hover:shadow-lg transition-shadow duration-300 overflow-hidden p-0">
                <CardContent className="p-6">
                    {/* Header */}
                    <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                            <Link to={`/restaurant/${restaurant.id}`}>
                                <h3 className="text-xl font-bold text-foreground hover:text-primary transition-colors line-clamp-1">
                                    {restaurant.name}
                                </h3>
                            </Link>
                        </div>
                        <Badge
                            variant={
                                restaurant.is_active ? "default" : "destructive"
                            }
                        >
                            {restaurant.is_active ? "Buka" : "Tutup"}
                        </Badge>
                    </div>

                    {/* Rating */}
                    <div className="flex items-center gap-2 mb-4">
                        <div className="flex items-center gap-1">
                            <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                            <span className="font-semibold text-sm">
                                {averageRating.toFixed(1)}
                            </span>
                        </div>
                        <span className="text-muted-foreground text-sm">
                            ({totalRatings} ulasan)
                        </span>
                        <div className="flex items-center gap-1 ml-auto">
                            <Utensils className="h-4 w-4 text-primary" />
                            <span className="text-sm font-medium">
                                {foodsCount} menu
                            </span>
                        </div>
                    </div>

                    {/* Contact Info */}
                    <div className="space-y-2 mb-4">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <MapPin className="h-4 w-4 flex-shrink-0" />
                            <span className="line-clamp-1">
                                {restaurant.address}
                            </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Clock className="h-4 w-4 flex-shrink-0" />
                            <span>Buka setiap hari</span>
                        </div>
                    </div>

                    {/* Action Button */}
                    <Link
                        to={`/restaurant/${restaurant.id}`}
                        className="block w-full"
                    >
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 px-4 rounded-md font-medium transition-colors"
                        >
                            Lihat Menu
                        </motion.button>
                    </Link>
                </CardContent>
            </Card>
        </motion.div>
    );
}
