import React from "react";
import { motion } from "framer-motion";
import { Utensils, Search, Heart } from "lucide-react";

export default function HomeHeader() {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-8 space-y-4"
        >
            <div className="flex items-center justify-center gap-3">
                <Utensils className="h-12 w-12 text-primary" />
                <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    Foodie Explorer
                </h1>
            </div>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Temukan makanan terbaik dari restaurant pilihan. Jelajahi cita
                rasa yang menggugah selera dan bagikan pengalaman kuliner Anda.
            </p>

            {/* Features */}
            <div className="flex items-center justify-center gap-8 mt-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                    <Search className="h-4 w-4" />
                    <span>Pencarian Mudah</span>
                </div>
                <div className="flex items-center gap-2">
                    <Heart className="h-4 w-4" />
                    <span>Favorit Personal</span>
                </div>
                <div className="flex items-center gap-2">
                    <Utensils className="h-4 w-4" />
                    <span>Rekomendasi Terbaik</span>
                </div>
            </div>
        </motion.div>
    );
}
