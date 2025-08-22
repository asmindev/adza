/**
 * Utility functions for image management
 * Can be reused across different components that handle images
 */

/**
 * Validates if a URL is a valid image URL
 * @param {string} url - The URL to validate
 * @returns {boolean} - Whether the URL is valid
 */
export const isValidImageUrl = (url) => {
    if (!url) return false;
    return url.match(/^https?:\/\/.+\.(jpeg|jpg|png|gif|webp)(\?.*)?$/i);
};

/**
 * Creates image object from URL
 * @param {string} url - Image URL
 * @param {boolean} isFirstImage - Whether this is the first image (will be main)
 * @returns {object} - Image object
 */
export const createImageFromUrl = (url, isFirstImage = false) => {
    return {
        url,
        preview: url,
        status: "new_url",
        isMain: isFirstImage,
    };
};

/**
 * Creates image object from file
 * @param {File} file - File object
 * @param {boolean} isFirstImage - Whether this is the first image (will be main)
 * @returns {object} - Image object
 */
export const createImageFromFile = (file, isFirstImage = false) => {
    return {
        file,
        preview: URL.createObjectURL(file),
        status: "new",
        progress: 0,
        isMain: isFirstImage,
    };
};

/**
 * Creates image object from existing image data
 * @param {object} imageData - Existing image data from API
 * @param {number} index - Image index
 * @returns {object} - Image object
 */
export const createImageFromExisting = (imageData, index) => {
    return {
        id: imageData.id,
        url: imageData.image_url,
        preview: imageData.image_url,
        status: "existing",
        isMain: imageData.is_main,
        existingIndex: index,
    };
};

/**
 * Sets main image by index
 * @param {Array} images - Current images array
 * @param {number} mainIndex - Index of image to set as main
 * @returns {Array} - Updated images array
 */
export const setMainImage = (images, mainIndex) => {
    return images.map((img, i) => ({
        ...img,
        isMain: i === mainIndex,
    }));
};

/**
 * Removes image by index and handles main image reassignment
 * @param {Array} images - Current images array
 * @param {number} removeIndex - Index of image to remove
 * @returns {object} - { updatedImages, removedImage }
 */
export const removeImage = (images, removeIndex) => {
    const imageToRemove = images[removeIndex];
    const filtered = images.filter((_, i) => i !== removeIndex);

    // If we removed the main image, set a new one
    if (imageToRemove.isMain && filtered.length > 0) {
        const newMainIndex = removeIndex < filtered.length ? removeIndex : 0;
        filtered[newMainIndex].isMain = true;
    }

    return {
        updatedImages: filtered,
        removedImage: imageToRemove,
    };
};

/**
 * Adds new images to existing array
 * @param {Array} currentImages - Current images array
 * @param {Array} newImages - New images to add
 * @returns {Array} - Updated images array
 */
export const addImages = (currentImages, newImages) => {
    const updated = [...currentImages, ...newImages];

    // Make first image the main image if none exists
    if (currentImages.length === 0 && newImages.length > 0) {
        updated[0].isMain = true;
    }

    return updated;
};

/**
 * Prepares images data for API submission
 * @param {Array} images - Images array
 * @param {Array} deletedImageIds - Array of deleted image IDs
 * @returns {object} - Formatted data for API
 */
export const prepareImagesForApi = (images, deletedImageIds = []) => {
    return {
        new_images: images
            .filter((img) => img.status === "new" || img.status === "new_url")
            .map((img) => ({
                image_url: img.url || "",
                file: img.file || null,
                is_main: img.isMain,
            })),
        deleted_image_ids: deletedImageIds,
    };
};

/**
 * Cleans up object URLs to prevent memory leaks
 * @param {Array} images - Images array
 */
export const cleanupImageUrls = (images) => {
    images.forEach((image) => {
        if (image.file && image.preview) {
            URL.revokeObjectURL(image.preview);
        }
    });
};
