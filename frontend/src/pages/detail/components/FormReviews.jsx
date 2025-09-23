import { useState, useContext } from "react";
import { toast } from "sonner";
import { mutate } from "swr";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    Drawer,
    DrawerClose,
    DrawerContent,
    DrawerDescription,
    DrawerFooter,
    DrawerHeader,
    DrawerTitle,
    DrawerTrigger,
} from "@/components/ui/drawer";
import { Label } from "@/components/ui/label";
import { useIsMobile } from "@/hooks/use-mobile";
import { Star } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { UserContext } from "@/contexts/UserContextDefinition";
import { useSubmitReview } from "@/lib/api";

export default function FormReviews({ foodId, onReviewSubmitted }) {
    const [open, setOpen] = useState(false);
    const isMobile = useIsMobile();
    const { user } = useContext(UserContext);

    const handleFormSubmit = (rating, content, ratingDetails) => {
        setOpen(false);
        if (onReviewSubmitted) {
            onReviewSubmitted({ rating, content, ratingDetails });
        }
    };

    if (!isMobile) {
        return (
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogTrigger asChild>
                    <button
                        type="button"
                        className="w-full text-primary cursor-pointer underline"
                    >
                        Tulis Ulasan
                    </button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Tulis Ulasan & Rating</DialogTitle>
                        <DialogDescription>
                            Berikan rating dan tulis ulasan Anda untuk makanan
                            ini. Kedua field wajib diisi untuk membantu pengguna
                            lain.
                        </DialogDescription>
                    </DialogHeader>
                    <ProfileForm
                        foodId={foodId}
                        user={user}
                        onSubmit={handleFormSubmit}
                    />
                </DialogContent>
            </Dialog>
        );
    }

    return (
        <Drawer open={open} onOpenChange={setOpen}>
            <DrawerTrigger asChild>
                <button
                    type="button"
                    className="w-full text-foreground cursor-pointer underline"
                >
                    Tulis Ulasan
                </button>
            </DrawerTrigger>
            <DrawerContent>
                <DrawerHeader className="text-left">
                    <DrawerTitle>Ulasan & Rating</DrawerTitle>
                    <DrawerDescription>
                        Berikan rating dan tulis ulasan Anda untuk makanan ini.
                        Kedua field wajib diisi untuk membantu pengguna lain.
                    </DrawerDescription>
                </DrawerHeader>
                <ProfileForm
                    className="px-4"
                    foodId={foodId}
                    user={user}
                    onSubmit={handleFormSubmit}
                />
                <DrawerFooter className="pt-2">
                    <DrawerClose asChild>
                        <Button variant="outline">Cancel</Button>
                    </DrawerClose>
                </DrawerFooter>
            </DrawerContent>
        </Drawer>
    );
}

function ProfileForm({ className = "", foodId, user, onSubmit }) {
    // Change from single rating to detailed rating criteria
    const [ratingDetails, setRatingDetails] = useState({
        flavor: 0, // Rasa
        serving: 0, // Porsi
        price: 0, // Harga
        place: 0, // Tempat
    });
    const [hoveredRating, setHoveredRating] = useState({
        flavor: 0,
        serving: 0,
        price: 0,
        place: 0,
    });
    const [content, setContent] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { trigger: submitReview } = useSubmitReview();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!user) {
            toast.error("Autentikasi Diperlukan", {
                description:
                    "Silakan masuk untuk menilai atau mengulas makanan ini",
            });
            return;
        }

        // Require all rating criteria and content for review submission
        const allRatingsGiven = Object.values(ratingDetails).every(
            (rating) => rating > 0
        );
        if (!allRatingsGiven) {
            toast.error("Rating diperlukan", {
                description:
                    "Silakan berikan rating untuk semua kriteria (Rasa, Porsi, Harga, Tempat)",
            });
            return;
        }

        if (!content.trim()) {
            toast.error("Ulasan diperlukan", {
                description: "Silakan tulis ulasan Anda",
            });
            return;
        }

        setIsSubmitting(true);

        try {
            console.log("Submitting review:", {
                food_id: foodId,
                content: content.trim(),
                rating_details: ratingDetails,
            });
            // Submit review with detailed rating in single request
            await submitReview({
                food_id: foodId,
                content: content.trim(),
                rating_details: ratingDetails,
            });

            toast.success("Berhasil!", {
                description: "Rating dan ulasan Anda telah dikirim",
            });

            // Revalidate the food data to show updated reviews
            mutate(`/api/v1/foods/${foodId}`);

            // Call the onSubmit callback with rating details
            if (onSubmit) {
                const averageRating =
                    Object.values(ratingDetails).reduce(
                        (sum, rating) => sum + rating,
                        0
                    ) / 4;
                onSubmit(averageRating, content, ratingDetails);
            }

            // Reset form
            setRatingDetails({
                flavor: 0,
                serving: 0,
                price: 0,
                place: 0,
            });
            setContent("");
            setHoveredRating({
                flavor: 0,
                serving: 0,
                price: 0,
                place: 0,
            });
        } catch (error) {
            console.error("Error submitting review:", error);
            toast.error("Gagal mengirim", {
                description: error.message || "Silakan coba lagi nanti",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleStarClick = (criteria, starRating) => {
        setRatingDetails((prev) => ({
            ...prev,
            [criteria]: starRating,
        }));
    };

    const handleStarHover = (criteria, starRating) => {
        setHoveredRating((prev) => ({
            ...prev,
            [criteria]: starRating,
        }));
    };

    const handleStarLeave = (criteria) => {
        setHoveredRating((prev) => ({
            ...prev,
            [criteria]: 0,
        }));
    };

    return (
        <form
            className={`grid items-start gap-6 ${className}`}
            onSubmit={handleSubmit}
        >
            {/* Detailed Rating Criteria */}
            <div className="space-y-4">
                <Label>
                    Rating Kriteria <span className="text-red-500">*</span>
                </Label>
                <p className="text-sm text-muted-foreground">
                    Berikan penilaian untuk setiap aspek makanan ini
                </p>

                {/* Rating criteria */}
                {[
                    { key: "flavor", label: "Rasa", icon: "🍽️" },
                    { key: "serving", label: "Porsi", icon: "🥄" },
                    { key: "price", label: "Harga", icon: "💰" },
                    { key: "place", label: "Tempat", icon: "🏪" },
                ].map((criteria) => (
                    <div key={criteria.key} className="space-y-2">
                        <div className="flex items-center gap-2">
                            <span className="text-sm">{criteria.icon}</span>
                            <Label className="text-sm font-medium">
                                {criteria.label}
                            </Label>
                        </div>
                        <div className="flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map((star) => {
                                const isFilled =
                                    star <=
                                    (hoveredRating[criteria.key] ||
                                        ratingDetails[criteria.key]);
                                return (
                                    <button
                                        key={star}
                                        type="button"
                                        className="p-1 rounded hover:bg-accent transition-colors"
                                        onClick={() =>
                                            handleStarClick(criteria.key, star)
                                        }
                                        onMouseEnter={() =>
                                            handleStarHover(criteria.key, star)
                                        }
                                        onMouseLeave={() =>
                                            handleStarLeave(criteria.key)
                                        }
                                        disabled={isSubmitting}
                                    >
                                        <Star
                                            className={`w-4 h-4 transition-colors ${
                                                isFilled
                                                    ? "text-yellow-400 fill-yellow-400"
                                                    : "text-muted-foreground"
                                            }`}
                                        />
                                    </button>
                                );
                            })}
                            <span className="ml-2 text-xs text-muted-foreground">
                                {ratingDetails[criteria.key] > 0
                                    ? `${ratingDetails[criteria.key]}/5`
                                    : "Belum dinilai"}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid gap-3">
                <Label htmlFor="content">
                    Tulis Ulasan <span className="text-red-500">*</span>
                </Label>
                <Textarea
                    id="content"
                    placeholder="Bagikan pengalaman Anda dengan hidangan ini... (Wajib diisi)"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    disabled={isSubmitting}
                    rows={4}
                />
            </div>

            <Button
                type="submit"
                disabled={
                    isSubmitting ||
                    !Object.values(ratingDetails).every(
                        (rating) => rating > 0
                    ) ||
                    !content.trim()
                }
            >
                {isSubmitting ? "Mengirim..." : "Simpan Review & Rating"}
            </Button>
        </form>
    );
}
