import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/id"; // Indonesian locale

dayjs.extend(relativeTime);
dayjs.locale("id");

/**
 * Format a date to a relative time string in Indonesian.
 * @param {string|Date} time - The date to format.
 * @returns {string} A localized relative time string.
 * @example
 * formatTimeAgo("2022-01-01T00:00:00.000Z") // "sebulan yang lalu"
 * formatTimeAgo(new Date()) // "Baru saja"
 */
export const formatTimeAgo = (time) => {
    if (!time) return "";

    try {
        const date = dayjs(time);
        const now = dayjs();
        const diffInSeconds = now.diff(date, "second");
        const diffInDays = now.diff(date, "day");

        // Very recent - within 5 seconds
        if (diffInSeconds < 5) {
            return "Baru saja";
        }

        // More than 2 days - show the actual date
        if (diffInDays > 2) {
            return date.format("DD MMM YYYY");
        }

        // Otherwise show relative time (e.g., "5 menit yang lalu")
        return date.fromNow();
    } catch (error) {
        console.error("Error formatting date:", error);
        return "Invalid date";
    }
};

// Price formatting
export const formatPrice = (price) => {
    return new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(price);
};

// Rating utilities
export const formatRating = (rating) => {
    return Number(rating).toFixed(1);
};

export const getRatingColor = (rating) => {
    if (rating >= 4.5) return "text-green-600";
    if (rating >= 4.0) return "text-green-500";
    if (rating >= 3.5) return "text-yellow-500";
    if (rating >= 3.0) return "text-orange-500";
    return "text-red-500";
};

// Text utilities
export const truncateText = (text, maxLength = 100) => {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
};

// Array utilities
export const groupBy = (array, key) => {
    return array.reduce((result, item) => {
        const group = item[key];
        if (!result[group]) {
            result[group] = [];
        }
        result[group].push(item);
        return result;
    }, {});
};

// URL utilities
export const getImageUrl = (imagePath) => {
    if (!imagePath) return "/images/placeholder-food.jpg";
    if (imagePath.startsWith("http")) return imagePath;
    return `/images/${imagePath}`;
};

// Local storage utilities
export const getFromLocalStorage = (key, defaultValue = null) => {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error(`Error reading from localStorage key "${key}":`, error);
        return defaultValue;
    }
};

export const setToLocalStorage = (key, value) => {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error(`Error writing to localStorage key "${key}":`, error);
    }
};

export const removeFromLocalStorage = (key) => {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error(`Error removing from localStorage key "${key}":`, error);
    }
};
