import { useCallback, useRef } from "react";

/**
 * Hook untuk throttle function calls
 * @param {Function} callback - Function yang akan di-throttle
 * @param {number} delay - Delay dalam milliseconds
 * @returns {Function} - Throttled function
 */
export function useThrottle(callback, delay) {
    const lastRun = useRef(Date.now());

    return useCallback(
        (...args) => {
            if (Date.now() - lastRun.current >= delay) {
                callback(...args);
                lastRun.current = Date.now();
            }
        },
        [callback, delay]
    );
}
