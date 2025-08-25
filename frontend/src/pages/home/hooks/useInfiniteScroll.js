import { useState, useEffect, useCallback } from "react";
import { useThrottle } from "@/hooks/useThrottle";

/**
 * Hook untuk infinite scroll functionality
 * @param {Function} fetchMore - Function untuk fetch data selanjutnya
 * @param {Object} options - Options untuk infinite scroll
 * @param {number} options.threshold - Threshold untuk trigger load more (default: 200px)
 * @param {number} options.throttleDelay - Delay untuk throttle scroll event (default: 100ms)
 * @param {boolean} options.hasMore - Apakah masih ada data yang bisa di-load
 * @param {boolean} options.loading - Status loading
 * @returns {Object} - Object dengan loading state dan ref untuk container
 */
export function useInfiniteScroll(fetchMore, options = {}) {
    const {
        threshold = 200,
        throttleDelay = 100,
        hasMore = true,
        loading = false,
    } = options;

    const [isLoadingMore, setIsLoadingMore] = useState(false);

    const handleScroll = useCallback(() => {
        if (loading || isLoadingMore || !hasMore) return;

        const scrollTop =
            window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = window.innerHeight;

        if (scrollTop + clientHeight >= scrollHeight - threshold) {
            setIsLoadingMore(true);
            fetchMore().finally(() => {
                setIsLoadingMore(false);
            });
        }
    }, [fetchMore, loading, isLoadingMore, hasMore, threshold]);

    const throttledHandleScroll = useThrottle(handleScroll, throttleDelay);

    useEffect(() => {
        window.addEventListener("scroll", throttledHandleScroll);
        return () =>
            window.removeEventListener("scroll", throttledHandleScroll);
    }, [throttledHandleScroll]);

    return {
        isLoadingMore,
        setIsLoadingMore,
    };
}
