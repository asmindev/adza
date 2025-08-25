/**
 * Utility functions untuk profile
 */

// Generate user initials dari nama
export const getUserInitials = (name) => {
    if (!name) return "U";

    const names = name.trim().split(" ");
    if (names.length === 1) {
        return names[0].charAt(0).toUpperCase();
    }

    return (
        names[0].charAt(0) + names[names.length - 1].charAt(0)
    ).toUpperCase();
};

// Format rating dengan 1 desimal
export const formatRating = (rating) => {
    if (!rating || rating === 0) return "0.0";
    return Number(rating).toFixed(1);
};

// Format tanggal untuk display
export const formatDate = (dateString) => {
    if (!dateString) return "";

    const date = new Date(dateString);
    return new Intl.DateTimeFormat("id-ID", {
        year: "numeric",
        month: "long",
        day: "numeric",
    }).format(date);
};

// Truncate text dengan ellipsis
export const truncateText = (text, maxLength = 100) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
};

// Validate image URL
export const isValidImageUrl = (url) => {
    if (!url) return false;

    const imageExtensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"];
    const lowercaseUrl = url.toLowerCase();

    return (
        imageExtensions.some((ext) => lowercaseUrl.includes(ext)) ||
        lowercaseUrl.includes("data:image/")
    );
};
