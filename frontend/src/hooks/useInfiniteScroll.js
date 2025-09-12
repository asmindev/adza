import { useEffect, useRef, useCallback } from "react";

export const useInfiniteScroll = (loadMore, hasMore, isLoading) => {
    const loadMoreRef = useRef(null);

    const handleObserver = useCallback(
        (entries) => {
            const [target] = entries;
            if (target.isIntersecting && hasMore && !isLoading) {
                loadMore();
            }
        },
        [loadMore, hasMore, isLoading]
    );

    useEffect(() => {
        const element = loadMoreRef.current;
        if (!element) return;

        const observer = new IntersectionObserver(handleObserver, {
            threshold: 0.1,
            rootMargin: "200px", // Increased margin for earlier loading
        });

        observer.observe(element);

        return () => {
            if (element) {
                observer.unobserve(element);
            }
        };
    }, [handleObserver]);

    return loadMoreRef;
};
