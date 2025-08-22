import { useState, useCallback } from "react";

export const useFavorites = (storageKey = "foodFavorites") => {
    const [favorites, setFavorites] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem(storageKey)) || [];
        } catch {
            return [];
        }
    });

    const toggleFavorite = useCallback(
        (itemId) => {
            const newFavorites = favorites.includes(itemId)
                ? favorites.filter((id) => id !== itemId)
                : [...favorites, itemId];

            setFavorites(newFavorites);
            localStorage.setItem(storageKey, JSON.stringify(newFavorites));
        },
        [favorites, storageKey]
    );

    const isFavorite = useCallback(
        (itemId) => {
            return favorites.includes(itemId);
        },
        [favorites]
    );

    const clearFavorites = useCallback(() => {
        setFavorites([]);
        localStorage.removeItem(storageKey);
    }, [storageKey]);

    return {
        favorites,
        toggleFavorite,
        isFavorite,
        clearFavorites,
    };
};
