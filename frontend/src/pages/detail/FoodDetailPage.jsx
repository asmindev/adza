import React, { useContext } from "react";
import { useParams } from "react-router";
import FoodDetail from "./FoodDetail";
import { toast } from "sonner";
import { UserContext } from "@/contexts/UserContextDefinition";

export default function FoodDetailPage() {
    const params = useParams();
    const id = params.id;
    const { user } = useContext(UserContext);

    const handleRateFood = async (foodId, data) => {
        if (!user) {
            toast.error("Autentikasi Diperlukan", {
                description:
                    "Silakan masuk untuk menilai atau mengulas makanan ini",
            });
            return false;
        }

        try {
            if (data.rating) {
                toast.success("Penilaian berhasil dikirim");
            }

            if (data.content) {
                toast.success("Ulasan berhasil dikirim");
            }

            return true;
        } catch (error) {
            console.error("Error submitting rating/review:", error);
            toast.error("Gagal mengirim", {
                description: error.message || "Silakan coba lagi nanti",
            });
            return false;
        }
    };

    return <FoodDetail foodId={id} onRateFood={handleRateFood} />;
}
