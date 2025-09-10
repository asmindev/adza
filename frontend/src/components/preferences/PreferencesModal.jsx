import { useState, useEffect, useMemo, useCallback, memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Settings, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetDescription,
    SheetFooter,
} from "@/components/ui/sheet";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { apiService } from "@/lib/api";
import { useIsMobile } from "@/hooks/use-mobile";
import useSWR, { mutate } from "swr";

// Memoized category button to prevent unnecessary re-renders
const CategoryButton = memo(({ category, isSelected, onToggle, isLoading }) => (
    <button
        key={category.id}
        onClick={() => onToggle(category.id)}
        disabled={isLoading}
        className={cn(
            "p-3 rounded-lg border transition-all duration-200 text-left hover:shadow-md min-w-0",
            isSelected
                ? "bg-primary/5 text-primary shadow-lg shadow-primary/20 border-primary"
                : "border-gray-200 hover:border-primary/30 hover:bg-primary/5",
            isLoading && "opacity-50 cursor-not-allowed"
        )}
    >
        <div className="flex items-center justify-between w-full">
            <div className="min-w-0 flex-1">
                <div className="font-medium text-xs truncate">
                    {category.name}
                </div>
            </div>
            <div className="ml-2 flex-shrink-0">
                <div
                    className={cn(
                        "w-4 h-4 rounded-full flex items-center justify-center transition-all duration-200",
                        isSelected
                            ? "bg-primary scale-100 opacity-100"
                            : "bg-gray-300 scale-0 opacity-0"
                    )}
                >
                    <Check className="w-2.5 h-2.5 text-white" />
                </div>
            </div>
        </div>
    </button>
));

CategoryButton.displayName = "CategoryButton";

export default function PreferencesModal({ isOpen, onClose, className }) {
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isInitialized, setIsInitialized] = useState(false);
    const isMobile = useIsMobile();

    // Fetch categories
    const { data: categoriesData, error: categoriesError } = useSWR(
        isOpen ? "/v1/categories" : null,
        () => apiService.categories.getAll(),
        {
            revalidateOnFocus: false,
        }
    );

    // Fetch user's favorite categories
    const { data: userFavoritesData, error: favoritesError } = useSWR(
        isOpen ? "/v1/me/favorite-categories" : null,
        () => apiService.userFavoriteCategories.getMyFavorites(),
        {
            revalidateOnFocus: false,
        }
    );

    const categories = categoriesData?.data?.data || [];
    const userFavorites = useMemo(() => {
        const data = userFavoritesData?.data;

        // Debug logging
        console.log("userFavoritesData raw:", userFavoritesData);
        console.log("userFavoritesData.data:", data);

        // Ensure we always return an array
        if (Array.isArray(data)) {
            console.log("userFavorites is array:", data);
            return data;
        }
        // Handle case where data might be nested
        if (data && Array.isArray(data.data)) {
            console.log("userFavorites nested array:", data.data);
            return data.data;
        }
        // Return empty array as fallback
        console.log("userFavorites fallback to empty array");
        return [];
    }, [userFavoritesData]);

    // Reset and initialize selected categories when modal opens
    useEffect(() => {
        if (isOpen) {
            setIsInitialized(false);
            setSelectedCategories([]);
        }
    }, [isOpen]);

    // Initialize selected categories when data is loaded
    useEffect(() => {
        if (
            isOpen &&
            userFavoritesData &&
            !isInitialized &&
            Array.isArray(userFavorites)
        ) {
            const favoriteIds = userFavorites
                .map((fav) => fav.id)
                .filter(Boolean);
            setSelectedCategories(favoriteIds);
            setIsInitialized(true);
        }
    }, [isOpen, userFavoritesData, userFavorites, isInitialized]);

    const handleCategoryToggle = useCallback((categoryId) => {
        setSelectedCategories((prev) =>
            prev.includes(categoryId)
                ? prev.filter((id) => id !== categoryId)
                : [...prev, categoryId]
        );
    }, []);

    const handleSave = async () => {
        if (selectedCategories.length === 0) {
            toast.error("Pilih minimal satu kategori preferensi");
            return;
        }

        setIsLoading(true);
        try {
            await apiService.userFavoriteCategories.addFavorites(
                selectedCategories
            );

            // Revalidate related data
            await mutate("/user-favorite-categories");
            await mutate("/api/v1/me"); // Refresh user profile data
            await mutate("/foods"); // Refresh foods with new preferences
            await mutate("/v1/me/favorite-categories"); // Refresh current favorites

            toast.success("Preferensi berhasil disimpan!");
            onClose();
        } catch (error) {
            console.error("Error saving preferences:", error);
            toast.error("Gagal menyimpan preferensi. Silakan coba lagi.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleClose = () => {
        if (!isLoading) {
            // Reset state when closing
            setSelectedCategories([]);
            setIsInitialized(false);
            onClose();
        }
    };

    // Show error state
    if (categoriesError || favoritesError) {
        return (
            <Dialog
                open={isOpen}
                onOpenChange={(open) => !open && handleClose()}
            >
                <DialogContent className="max-w-md">
                    <DialogHeader>
                        <DialogTitle className="text-red-600">
                            Error
                        </DialogTitle>
                        <DialogDescription>
                            Gagal memuat data. Silakan coba lagi.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button onClick={handleClose}>Tutup</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        );
    }

    // Show loading state while initializing
    const isLoadingData =
        !categoriesData || !userFavoritesData || !isInitialized;

    // Category selection component
    const CategoryGrid = ({ gridCols = "grid-cols-2" }) => (
        <div className="w-full overflow-hidden">
            {isLoadingData ? (
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                    <span className="ml-2 text-sm text-muted-foreground">
                        Memuat kategori...
                    </span>
                </div>
            ) : (
                <div className={cn("grid gap-2 w-full", gridCols)}>
                    {categories.map((category) => {
                        const isSelected = selectedCategories.includes(
                            category.id
                        );
                        return (
                            <CategoryButton
                                key={category.id}
                                category={category}
                                isSelected={isSelected}
                                onToggle={handleCategoryToggle}
                                isLoading={isLoading}
                            />
                        );
                    })}
                </div>
            )}
        </div>
    );

    // Mobile Sheet (Drawer)
    if (isMobile) {
        return (
            <Sheet
                open={isOpen}
                onOpenChange={(open) => !open && handleClose()}
            >
                <SheetContent
                    side="bottom"
                    className="p-0 gap-0 max-h-[70vh] flex flex-col"
                >
                    <div className="p-6 border-b flex-shrink-0">
                        <div className="flex items-center gap-3">
                            <Settings className="size-10 text-primary" />
                            <div>
                                <SheetTitle>Preferensi Makanan</SheetTitle>
                                <SheetDescription>
                                    Pilih kategori makanan yang kamu sukai untuk
                                    mendapatkan rekomendasi yang lebih personal.
                                </SheetDescription>
                            </div>
                        </div>
                    </div>

                    <div className="p-6 flex-1 overflow-y-auto min-h-0">
                        <CategoryGrid gridCols="grid-cols-2" />
                    </div>

                    <div className="p-6 border-t bg-gray-50/50 flex-shrink-0">
                        <div className="flex gap-3 w-full">
                            <Button
                                variant="outline"
                                onClick={handleClose}
                                disabled={isLoading || isLoadingData}
                                className="flex-1"
                            >
                                Batal
                            </Button>
                            <Button
                                onClick={handleSave}
                                disabled={
                                    isLoading ||
                                    isLoadingData ||
                                    selectedCategories.length === 0
                                }
                                className="flex-1"
                            >
                                {isLoading ? (
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <Check className="w-4 h-4 mr-2" />
                                )}
                                Simpan
                            </Button>
                        </div>
                        {selectedCategories.length > 0 && !isLoadingData && (
                            <p className="text-center text-xs text-muted-foreground mt-2">
                                {selectedCategories.length} kategori dipilih
                            </p>
                        )}
                    </div>
                </SheetContent>
            </Sheet>
        );
    }

    // Desktop Dialog
    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
            <DialogContent className="w-[480px] max-w-[90vw] p-0 gap-0 overflow-hidden">
                <div className="p-6 border-b">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Settings className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <DialogTitle className="text-lg font-semibold">
                                Preferensi Makanan
                            </DialogTitle>
                            <DialogDescription className="text-sm text-muted-foreground">
                                Pilih kategori makanan yang kamu sukai
                            </DialogDescription>
                        </div>
                    </div>
                </div>

                <div className="p-6 max-h-64 overflow-y-auto">
                    <CategoryGrid gridCols="grid-cols-2" />
                </div>

                <div className="p-6 border-t bg-gray-50/50">
                    <div className="flex items-center justify-between w-full">
                        <div className="text-sm text-muted-foreground">
                            {isLoadingData
                                ? "Memuat..."
                                : selectedCategories.length > 0
                                ? `${selectedCategories.length} kategori dipilih`
                                : "Pilih minimal 1 kategori"}
                        </div>
                        <div className="flex gap-3">
                            <Button
                                variant="outline"
                                onClick={handleClose}
                                disabled={isLoading || isLoadingData}
                            >
                                Batal
                            </Button>
                            <Button
                                onClick={handleSave}
                                disabled={
                                    isLoading ||
                                    isLoadingData ||
                                    selectedCategories.length === 0
                                }
                                className="min-w-[100px]"
                            >
                                {isLoading ? (
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                    <Check className="w-4 h-4 mr-2" />
                                )}
                                Simpan
                            </Button>
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
