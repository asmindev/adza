import React from "react";
import { motion } from "framer-motion";

/**
 * Hero Section Component
 * Menampilkan section hero dengan background image dan teks utama
 */
export function HeroSection() {
    const heroVariants = {
        hidden: { opacity: 0, y: 50 },
        visible: { opacity: 1, y: 0 },
    };

    const titleVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0 },
    };

    return (
        <div className="px-4 md:px-10 py-8">
            <section className="relative text-white overflow-hidden w-full h-96 md:h-120 flex items-center rounded-2xl shadow-2xl">
                {/* Background Image */}
                <div
                    className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                    style={{
                        backgroundImage:
                            "url('https://cdn.rri.co.id/berita/10/images/1706597617604-6/ols2xpnjja8j69y.jpeg')",
                    }}
                />

                {/* Dark Overlay */}
                <div className="absolute inset-0 bg-black/50" />

                {/* Content */}
                <div className="relative container mx-auto px-4 py-20 md:py-32">
                    <motion.div
                        className="mx-auto text-center max-w-4xl"
                        variants={heroVariants}
                        initial="hidden"
                        animate="visible"
                        transition={{ duration: 0.8 }}
                    >
                        <motion.h1
                            className="text-4xl md:text-6xl font-bold mb-6 leading-tight"
                            variants={titleVariants}
                            transition={{ delay: 0.2, duration: 0.8 }}
                        >
                            Lapar?
                        </motion.h1>

                        <motion.p
                            className="text-xl md:text-2xl mb-8 text-white/90 max-w-2xl mx-auto leading-relaxed"
                            variants={titleVariants}
                            transition={{ delay: 0.4, duration: 0.8 }}
                        >
                            Cari rekomendasi kuliner di Kendari
                        </motion.p>
                    </motion.div>
                </div>
            </section>
        </div>
    );
}
