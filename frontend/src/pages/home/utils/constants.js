/**
 * Animation variants untuk komponen home
 */
export const ANIMATION_VARIANTS = {
    // Container variants for food grid
    container: {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
            },
        },
    },

    // Hero section variants
    hero: {
        hidden: { opacity: 0, y: 50 },
        visible: { opacity: 1, y: 0 },
    },

    // Title variants
    title: {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0 },
    },

    // Food card variants
    foodCard: {
        hidden: { opacity: 0, y: 15 },
        visible: {
            opacity: 1,
            y: 0,
            transition: { duration: 0.3 },
        },
    },
};

/**
 * Constants untuk pagination - mencocokkan dengan backend API
 */
export const PAGINATION_CONSTANTS = {
    DEFAULT_LIMIT: 20, // Sesuai dengan backend default
    LOAD_MORE_THRESHOLD: 200,
    THROTTLE_DELAY: 100,
    MAX_LIMIT: 100, // Sesuai dengan backend max limit
};

/**
 * Constants untuk hero section
 */
export const HERO_CONSTANTS = {
    DEFAULT_IMAGE:
        "https://cdn.rri.co.id/berita/10/images/1706597617604-6/ols2xpnjja8j69y.jpeg",
    TITLE: "Lapar?",
    SUBTITLE: "Cari rekomendasi kuliner di Kendari",
};
