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

    const handleFormSubmit = (rating, content) => {
        setOpen(false);
        if (onReviewSubmitted) {
            onReviewSubmitted({ rating, content });
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
    const [rating, setRating] = useState(0);
    const [hoveredRating, setHoveredRating] = useState(0);
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

        // Require both rating and content for review submission
        if (rating === 0) {
            toast.error("Rating diperlukan", {
                description: "Silakan berikan rating untuk makanan ini",
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
                rating: rating,
            });
            // Submit review with rating in single request
            await submitReview({
                food_id: foodId,
                content: content.trim(),
                rating: rating,
            });

            toast.success("Berhasil!", {
                description: "Rating dan ulasan Anda telah dikirim",
            });

            // Revalidate the food data to show updated reviews
            mutate(`/api/v1/foods/${foodId}`);

            // Call the onSubmit callback
            if (onSubmit) {
                onSubmit(rating, content);
            }

            // Reset form
            setRating(0);
            setContent("");
            setHoveredRating(0);
        } catch (error) {
            console.error("Error submitting review:", error);
            toast.error("Gagal mengirim", {
                description: error.message || "Silakan coba lagi nanti",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleStarClick = (starRating) => {
        setRating(starRating);
    };

    const handleStarHover = (starRating) => {
        setHoveredRating(starRating);
    };

    const handleStarLeave = () => {
        setHoveredRating(0);
    };

    return (
        <form
            className={`grid items-start gap-6 ${className}`}
            onSubmit={handleSubmit}
        >
            {/* Rating */}
            <div className="space-y-2">
                <Label>
                    Rating <span className="text-red-500">*</span>
                </Label>
                <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => {
                        const isFilled = star <= (hoveredRating || rating);
                        return (
                            <button
                                key={star}
                                type="button"
                                className="p-1 rounded hover:bg-accent transition-colors"
                                onClick={() => handleStarClick(star)}
                                onMouseEnter={() => handleStarHover(star)}
                                onMouseLeave={handleStarLeave}
                                disabled={isSubmitting}
                            >
                                <Star
                                    className={`w-5 h-5 transition-colors ${
                                        isFilled
                                            ? "text-yellow-400 fill-yellow-400"
                                            : "text-muted-foreground"
                                    }`}
                                />
                            </button>
                        );
                    })}
                </div>
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
                disabled={isSubmitting || rating === 0 || !content.trim()}
            >
                {isSubmitting ? "Mengirim..." : "Simpan Review & Rating"}
            </Button>
        </form>
    );
}
