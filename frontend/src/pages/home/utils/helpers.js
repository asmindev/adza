/**
 * Utility functions untuk home page
 */

/**
 * Handler untuk toggle favorite
 * @param {string} foodId - ID makanan
 */
export const handleToggleFavorite = (foodId) => {
    // TODO: Implement favorite toggle logic
    console.log("Toggle favorite for food:", foodId);
};

/**
 * Format error message
 * @param {Error} error - Error object
 * @returns {string} Formatted error message
 */
export const formatErrorMessage = (error) => {
    return (
        error?.message || "Failed to load food data. Please try again later."
    );
};

/**
 * Check if data is empty
 * @param {Array} data - Data array
 * @returns {boolean} True if data is empty
 */
export const isDataEmpty = (data) => {
    return !data || data.length === 0;
};

/**
 * Get loading state message
 * @param {boolean} isLoadingMore - Whether it's loading more data
 * @returns {string} Loading message
 */
export const getLoadingMessage = (isLoadingMore = false) => {
    return isLoadingMore ? "Memuat lebih banyak..." : "Loading food data...";
};
