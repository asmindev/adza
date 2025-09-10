import React, { useState, useContext, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle2, Circle, ChefHat } from "lucide-react";
import { toast } from "sonner";
import { UserContext } from "@/contexts/UserContextDefinition";
import useSWR from "swr";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
    HoverCard,
    HoverCardContent,
    HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Progress } from "@/components/ui/progress";
import { AnimatePresence, motion } from "framer-motion";
import { apiService } from "@/lib/api";
import { useNavigate } from "react-router";

export default function OnboardingPage() {
    const { user, setUser } = useContext(UserContext);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    let navigate = useNavigate();

    // Fetch categories data using SWR
    const { data, error, isLoading } = useSWR(
        "/api/v1/categories?include_stats=true"
    );

    const categories = data?.data || [];

    // Handle category selection toggle
    const toggleCategory = (categoryId) => {
        setSelectedCategories((prev) => {
            if (prev.includes(categoryId)) {
                return prev.filter((id) => id !== categoryId);
            } else {
                return [...prev, categoryId];
            }
        });
    };

    // Submit selected categories
    const handleSubmit = async () => {
        console.log("Selected categories:", selectedCategories);
        if (selectedCategories.length === 0) {
            toast.error("Silakan pilih minimal 1 kategori makanan");
            return;
        }

        setIsSubmitting(true);

        try {
            // Add all selected categories at once using the API service
            const result = await apiService.userFavoriteCategories.addFavorites(
                selectedCategories
            );

            // Check if there were any partial failures
            if (
                result.data &&
                result.data.errors &&
                result.data.errors.length > 0
            ) {
                const errorMessages = result.data.errors
                    .map((e) => `${e.category_id}: ${e.error}`)
                    .join(", ");

                toast.warning(
                    `Beberapa kategori gagal ditambahkan: ${errorMessages}`
                );
            } else {
                const msg = `Berhasil menambahkan ${selectedCategories.length} kategori!`;
                toast.success(msg);
                // Mark onboarding as completed using the API service
                await apiService.onboarding.complete();

                // Update user in context and localStorage
                const updatedUser = { ...user, onboarding_completed: true };
                setUser(updatedUser);
                localStorage.setItem("user", JSON.stringify(updatedUser));

                toast.success("Preferensi berhasil disimpan! Selamat datang!");

                // Redirect to home page
                setTimeout(() => {
                    navigate("/");
                }, 1500);
            }
        } catch (error) {
            console.error("Error completing onboarding:", error);
            toast.error(
                error.response?.data?.message ||
                    error.message ||
                    "Gagal menyimpan preferensi"
            );
        } finally {
            setIsSubmitting(false);
        }
    };

    // Calculate progress based on selected categories
    const progress = Math.min(
        (selectedCategories.length / categories.length) * 100,
        100
    );

    useEffect(() => {
        if (user && user.onboarding_completed) {
            navigate("/");
        }
    }, [user, navigate]);

    // Loading state
    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-background to-muted flex items-center justify-center">
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="text-center"
                >
                    <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
                    <p className="text-lg text-muted-foreground font-medium">
                        Memuat kategori makanan...
                    </p>
                </motion.div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-background to-muted flex items-center justify-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-center"
                >
                    <p className="text-destructive text-lg font-medium mb-4">
                        Gagal memuat kategori makanan
                    </p>
                    <Button
                        variant="outline"
                        onClick={() => window.location.reload()}
                        className="hover:bg-primary hover:text-primary-foreground transition-colors"
                    >
                        Coba Lagi
                    </Button>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-background to-muted py-12">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="max-w-4xl mx-auto"
                >
                    {/* Header */}
                    <div className="text-center mb-10">
                        <motion.div
                            className="bg-primary/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4"
                            whileHover={{ scale: 1.1 }}
                            transition={{ type: "spring", stiffness: 300 }}
                        >
                            <ChefHat className="h-10 w-10 text-primary" />
                        </motion.div>
                        <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3">
                            Selamat Datang di Adza!
                        </h1>
                        <p className="text-muted-foreground text-base max-w-md mx-auto">
                            Pilih kategori makanan favoritmu untuk mendapatkan
                            rekomendasi yang sesuai dengan selera kamu
                        </p>
                        <Progress
                            value={progress}
                            className="w-1/2 mx-auto mt-4"
                        />
                        <p className="text-sm text-muted-foreground mt-2">
                            {selectedCategories.length} dari {categories.length}{" "}
                            kategori dipilih
                        </p>
                    </div>

                    <Separator className="my-8" />

                    {/* Categories Selection */}
                    <ScrollArea className="h-[400px] rounded-lg border p-4">
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                            <AnimatePresence>
                                {categories.map((category) => (
                                    <motion.div
                                        key={category.id}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.9 }}
                                        transition={{ duration: 0.3 }}
                                    >
                                        <HoverCard>
                                            <HoverCardTrigger>
                                                <Card
                                                    className={`cursor-pointer transition-all duration-300 hover:shadow-lg border-2 ${
                                                        selectedCategories.includes(
                                                            category.id
                                                        )
                                                            ? "border-primary bg-primary/10"
                                                            : "border-border hover:border-primary/50"
                                                    }`}
                                                    onClick={() =>
                                                        toggleCategory(
                                                            category.id
                                                        )
                                                    }
                                                >
                                                    <CardContent className="p-4 text-center">
                                                        <div className="flex justify-center mb-3">
                                                            {selectedCategories.includes(
                                                                category.id
                                                            ) ? (
                                                                <CheckCircle2 className="h-6 w-6 text-primary" />
                                                            ) : (
                                                                <Circle className="h-6 w-6 text-muted-foreground" />
                                                            )}
                                                        </div>

                                                        {/* Category Icon (if available) */}
                                                        {category.icon && (
                                                            <div className="mb-3 text-2xl">
                                                                {category.icon}
                                                            </div>
                                                        )}

                                                        <h3 className="font-semibold text-foreground text-base mb-2">
                                                            {category.name}
                                                        </h3>

                                                        {/* Show favorite count if available */}
                                                        {category.favorite_count >
                                                            0 && (
                                                            <Badge
                                                                variant="secondary"
                                                                className="text-xs px-2 py-1"
                                                            >
                                                                {
                                                                    category.favorite_count
                                                                }{" "}
                                                                penggemar
                                                            </Badge>
                                                        )}
                                                    </CardContent>
                                                </Card>
                                            </HoverCardTrigger>
                                            <HoverCardContent className="w-64">
                                                <div className="text-sm">
                                                    <h4 className="font-semibold">
                                                        {category.name}
                                                    </h4>
                                                    <p className="text-muted-foreground">
                                                        {category.description ||
                                                            `Explore berbagai resep dan rekomendasi untuk ${category.name.toLowerCase()}.`}
                                                    </p>
                                                </div>
                                            </HoverCardContent>
                                        </HoverCard>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </ScrollArea>

                    {/* Selected categories summary */}
                    {selectedCategories.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                            className="my-8 text-center"
                        >
                            <p className="text-sm text-muted-foreground mb-3">
                                Kategori yang kamu pilih:
                            </p>
                            <div className="flex flex-wrap justify-center gap-2">
                                {selectedCategories.map((categoryId) => {
                                    const category = categories.find(
                                        (c) => c.id === categoryId
                                    );
                                    return category ? (
                                        <Badge
                                            key={categoryId}
                                            variant="default"
                                            className="text-sm px-3 py-1"
                                        >
                                            {category.name}
                                        </Badge>
                                    ) : null;
                                })}
                            </div>
                        </motion.div>
                    )}

                    <Separator className="my-8" />

                    {/* Submit Button */}
                    <div className="text-center">
                        <motion.div
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <Button
                                onClick={handleSubmit}
                                disabled={
                                    selectedCategories.length === 0 ||
                                    isSubmitting
                                }
                                className="px-10 py-3 text-lg font-semibold bg-primary hover:bg-primary/90"
                                size="lg"
                            >
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                        Menyimpan...
                                    </>
                                ) : (
                                    "Simpan Preferensi"
                                )}
                            </Button>
                        </motion.div>
                        <p className="text-xs text-muted-foreground mt-3">
                            Kamu bisa mengubah preferensi kapan saja di
                            pengaturan profil
                        </p>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
