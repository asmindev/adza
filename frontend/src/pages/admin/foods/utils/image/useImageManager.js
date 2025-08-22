import { useState, useCallback } from "react";
import { toast } from "sonner";
import {
    isValidImageUrl,
    createImageFromUrl,
    createImageFromFile,
    createImageFromExisting,
    setMainImage,
    removeImage,
    addImages,
    prepareImagesForApi,
    cleanupImageUrls,
} from "./imageUtils";

/**
 * Custom hook for managing images state and operations
 * Reusable across different components that handle image management
 */
export const useImageManager = () => {
    const [images, setImages] = useState([]);
    const [deletedImageIds, setDeletedImageIds] = useState([]);
    const [isUploading, setIsUploading] = useState(false);

    // Initialize images from existing data
    const initializeImages = useCallback((imageData) => {
        if (!imageData) {
            setImages([]);
            return;
        }

        if (Array.isArray(imageData) && imageData.length > 0) {
            // Multiple images
            const existingImages = imageData.map((img, index) =>
                createImageFromExisting(img, index)
            );
            setImages(existingImages);
        } else if (imageData.main_image) {
            // Legacy: single main image
            const mainImage = createImageFromExisting(imageData.main_image, 0);
            setImages([mainImage]);
        } else {
            setImages([]);
        }
    }, []);

    // Handle file drop
    const handleFileDrop = useCallback((acceptedFiles) => {
        setIsUploading(true);

        // Process each file
        const newImages = acceptedFiles.map((file) =>
            createImageFromFile(file, false)
        );

        // Simulate upload process
        setTimeout(() => {
            setImages((prev) => addImages(prev, newImages));
            setIsUploading(false);
        }, 1000);
    }, []);

    // Handle URL addition
    const handleAddUrl = useCallback((url, form) => {
        if (!isValidImageUrl(url)) {
            toast.error("Please enter a valid image URL");
            return;
        }

        setImages((prev) => {
            const newImage = createImageFromUrl(url, prev.length === 0);
            return addImages(prev, [newImage]);
        });

        // Clear the URL input
        if (form) {
            form.setValue("imageUrl", "");
        }
    }, []);

    // Set main image
    const handleSetMainImage = useCallback((index) => {
        setImages((prev) => setMainImage(prev, index));
    }, []);

    // Remove image
    const handleRemoveImage = useCallback((index) => {
        setImages((prev) => {
            const { updatedImages, removedImage } = removeImage(prev, index);

            // If removing an existing image, add its ID to deletedImageIds
            if (removedImage.status === "existing" && removedImage.id) {
                setDeletedImageIds((prevIds) => [...prevIds, removedImage.id]);
            }

            // Cleanup object URL to prevent memory leaks
            if (removedImage.file) {
                URL.revokeObjectURL(removedImage.preview);
            }

            return updatedImages;
        });
    }, []);

    // Reset all states
    const resetImages = useCallback(() => {
        // Cleanup existing URLs
        cleanupImageUrls(images);

        setImages([]);
        setDeletedImageIds([]);
        setIsUploading(false);
    }, [images]);

    // Get images data formatted for API
    const getImagesForApi = useCallback(() => {
        return prepareImagesForApi(images, deletedImageIds);
    }, [images, deletedImageIds]);

    // Validate images
    const validateImages = useCallback(() => {
        if (images.length === 0) {
            toast.warning("Silakan tambahkan minimal satu gambar");
            return false;
        }
        return true;
    }, [images]);

    return {
        // State
        images,
        deletedImageIds,
        isUploading,

        // Actions
        initializeImages,
        handleFileDrop,
        handleAddUrl,
        handleSetMainImage,
        handleRemoveImage,
        resetImages,

        // Utilities
        getImagesForApi,
        validateImages,
    };
};
