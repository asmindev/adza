import useSWR from "swr";
import { useContext, useState } from "react";
import { toast } from "sonner";
import {
    fetchWithToken,
    useUpdateProfile as useUpdateProfileAPI,
} from "@/pages/detail/components/lib/api";
import { UserContext } from "@/contexts/UserContextDefinition";

// Custom hook untuk fetch profile data
export const useProfile = () => {
    const {
        data: userData,
        isLoading,
        error,
        mutate,
    } = useSWR("/api/v1/me", fetchWithToken, {
        revalidateOnFocus: false,
    });

    const user = userData?.data;
    const foodRatings = user?.food_ratings || [];
    const reviews = user?.reviews || [];

    // Calculate statistics
    const stats = {
        totalRatings: foodRatings.length,
        totalReviews: reviews.length,
        averageRating:
            foodRatings.length > 0
                ? (
                      foodRatings.reduce(
                          (sum, rating) => sum + rating.rating,
                          0
                      ) / foodRatings.length
                  ).toFixed(1)
                : 0,
    };

    return {
        user,
        stats,
        isLoading,
        error,
        mutate,
    };
};

// Custom hook untuk update profile (menggunakan lib/api.js)
export const useUpdateProfile = () => {
    const { trigger: updateProfile, isMutating: isUpdating } =
        useUpdateProfileAPI();

    const handleUpdateProfile = async (data) => {
        try {
            await updateProfile(data);
            toast.success("Profile berhasil diupdate");
        } catch (error) {
            toast.error(error.message || "Gagal mengupdate profile");
            throw error;
        }
    };

    return {
        updateProfile: handleUpdateProfile,
        isUpdating,
    };
};

// Custom hook untuk update password
export const useUpdatePassword = () => {
    const [isUpdating, setIsUpdating] = useState(false);

    const updatePassword = async (data) => {
        setIsUpdating(true);
        try {
            const body = {
                old_password: data.currentPassword,
                new_password: data.newPassword,
            };

            const options = {
                method: "PUT",
                body: JSON.stringify(body),
            };
            const endpoint = "/api/v1/auth/change-password";
            const response = await fetchWithToken(endpoint, options);

            toast.success("Password berhasil diubah");
            return response;
        } catch (error) {
            toast.error(error.message || "Gagal mengubah password");
            throw error;
        } finally {
            setIsUpdating(false);
        }
    };

    return {
        updatePassword,
        isUpdating,
    };
};

// Custom hook untuk logout (menggunakan UserContext)
export const useLogout = () => {
    const { logout: logoutFromContext } = useContext(UserContext);
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    const logout = async () => {
        setIsLoggingOut(true);
        try {
            // Call API logout if endpoint exists
            try {
                await fetchWithToken("/auth/logout", {
                    method: "POST",
                });
            } catch (error) {
                // If API logout fails, still proceed with local logout
                console.warn("API logout failed:", error);
            }

            // Use logout from UserContext
            const result = logoutFromContext();

            if (result.success) {
                toast.success("Logout berhasil");

                // Redirect to login page
                window.location.href = "/login";

                return true;
            } else {
                throw new Error("Logout gagal");
            }
        } catch (error) {
            toast.error(error.message || "Gagal logout");
            throw error;
        } finally {
            setIsLoggingOut(false);
        }
    };

    return {
        logout,
        isLoggingOut,
    };
};
