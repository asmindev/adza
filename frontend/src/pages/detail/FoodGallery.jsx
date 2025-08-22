import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Camera } from "lucide-react";

export default function FoodGallery({ images = [] }) {
    // Find main image or default to first image
    const mainImageIndex = images.findIndex((img) => img.is_main) || 0;
    const [activeImage, setActiveImage] = useState(mainImageIndex);

    // Reset active image when images change
    React.useEffect(() => {
        const newMainIndex = images.findIndex((img) => img.is_main) || 0;
        setActiveImage(newMainIndex);
    }, [images]);

    if (!images.length) {
        return (
            <div className="w-full h-[400px] bg-muted flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                    <Camera className="h-12 w-12 mx-auto mb-2" />
                    <p>Tidak ada gambar tersedia</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full relative">
            <AnimatePresence mode="wait">
                <motion.div
                    key={activeImage}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="relative h-[400px]"
                >
                    <img
                        src={images[activeImage]?.image_url}
                        alt={`Gambar makanan ${activeImage + 1}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                            e.target.src =
                                "https://placehold.co/600x400?text=Gambar+Makanan";
                        }}
                    />

                    {/* Main image indicator */}
                    {images[activeImage]?.is_main && (
                        <div className="absolute top-4 right-4">
                            <span className="bg-primary text-primary-foreground text-xs px-2 py-1 rounded">
                                Utama
                            </span>
                        </div>
                    )}

                    {/* Image gallery navigation */}
                    {images.length > 1 && (
                        <div className="absolute bottom-4 left-0 right-0 flex justify-center space-x-2">
                            {images.map((_, index) => (
                                <button
                                    key={index}
                                    onClick={() => setActiveImage(index)}
                                    className={`w-3 h-3 rounded-full ${
                                        index === activeImage
                                            ? "bg-white"
                                            : "bg-white/50"
                                    }`}
                                    aria-label={`Lihat gambar ${index + 1}`}
                                />
                            ))}
                        </div>
                    )}
                </motion.div>
            </AnimatePresence>

            {/* Image thumbnails */}
            {images.length > 1 && (
                <div className="absolute top-4 left-4 flex flex-col space-y-2">
                    {images.slice(0, 4).map((image, index) => (
                        <button
                            key={index}
                            onClick={() => setActiveImage(index)}
                            className={`w-12 h-12 rounded-md overflow-hidden ${
                                index === activeImage
                                    ? "ring-2 ring-primary"
                                    : "opacity-70"
                            }`}
                        >
                            <img
                                src={image.image_url}
                                alt={`Gambar Kecil ${index + 1}`}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                    // Handling error
                                }}
                            />
                        </button>
                    ))}
                    {images.length > 4 && (
                        <button className="w-12 h-12 rounded-md bg-black/60 flex items-center justify-center text-white">
                            <Camera size={16} />
                            <span className="ml-1 text-xs">
                                +{images.length - 4}
                            </span>
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
