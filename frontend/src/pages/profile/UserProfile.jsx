import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";
import { UserContext } from "@/contexts/UserContextDefinition";
import { useProfile } from "./hooks/useProfile";
import { ProfileHeader } from "./components/ProfileHeader";
import { ProfileEditForm } from "./components/ProfileEditForm";
import { PasswordChangeForm } from "./components/PasswordChangeForm";
import { LogoutSection } from "./components/LogoutSection";
import { RatedFoods } from "./components/RatedFoods";
import { ReviewedFoods } from "./components/ReviewedFoods";
import PreferencesSection from "./components/PreferencesSection";

export default function UserProfile() {
    const {
        user: contextUser,
        logout,
        isAuthenticated,
    } = useContext(UserContext);
    const navigate = useNavigate();
    const { user, stats, isLoading, error, mutate } = useProfile();
    const [activeTab, setActiveTab] = useState("overview");

    // Validasi user dari context dan handle error/missing data
    useEffect(() => {
        if (!isAuthenticated()) {
            // Jika user tidak terautentikasi, hapus token dan redirect ke login
            toast.error("Sesi Anda telah berakhir. Silakan login kembali.");
            logout();
            navigate("/login", { replace: true });
            return;
        }

        if (error) {
            // Hapus token dan redirect ke login jika ada error
            toast.error(
                "Terjadi kesalahan dalam memuat profile. Silakan login kembali."
            );
            logout();
            navigate("/login", { replace: true });
            return;
        }

        if (!isLoading && (!user || !contextUser)) {
            // Jika loading selesai tapi tidak ada data user
            toast.error("Data profile tidak ditemukan. Silakan login kembali.");
            logout();
            navigate("/login", { replace: true });
            return;
        }
    }, [
        isAuthenticated,
        logout,
        navigate,
        error,
        isLoading,
        user,
        contextUser,
    ]);

    // Loading state
    if (isLoading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="flex items-center gap-3">
                    <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                    <span className="text-muted-foreground">
                        Memuat profile...
                    </span>
                </div>
            </div>
        );
    }

    // Error state - akan redirect via useEffect
    if (error) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center max-w-md mx-auto px-4">
                    <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-foreground mb-2">
                        Gagal Memuat Profile
                    </h2>
                    <p className="text-muted-foreground mb-6">
                        Terjadi kesalahan saat memuat data profile. Redirecting
                        ke login...
                    </p>
                    <div className="flex items-center justify-center">
                        <Loader2 className="w-4 h-4 animate-spin" />
                    </div>
                </div>
            </div>
        );
    }

    // No user data - akan redirect via useEffect
    if (!user || !contextUser) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center">
                    <p className="text-muted-foreground">
                        Data profile tidak ditemukan, redirecting ke login...
                    </p>
                    <div className="flex items-center justify-center mt-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                    </div>
                </div>
            </div>
        );
    }
    const handleProfileUpdate = () => {
        mutate(); // Refresh data setelah update
        setActiveTab("overview"); // Kembali ke tab overview
    };

    const handlePasswordUpdate = () => {
        setActiveTab("overview"); // Kembali ke tab overview setelah update password
    };

    return (
        <div className="min-h-screen bg-background">
            <div className="container mx-auto px-4 py-6 max-w-5xl">
                {/* Profile Header */}
                <div className="mb-6">
                    <ProfileHeader user={user} stats={stats} />
                </div>

                {/* Navigation Tabs */}
                <Tabs
                    value={activeTab}
                    onValueChange={setActiveTab}
                    className="space-y-6"
                >
                    <div className="flex justify-center">
                        <TabsList className="grid w-full max-w-md grid-cols-4">
                            <TabsTrigger value="overview">Overview</TabsTrigger>
                            <TabsTrigger value="ratings">Rating</TabsTrigger>
                            <TabsTrigger value="reviews">Review</TabsTrigger>
                            <TabsTrigger value="settings">Setting</TabsTrigger>
                        </TabsList>
                    </div>

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="space-y-6">
                        <div className="grid gap-6 lg:grid-cols-2">
                            <RatedFoods
                                foodRatings={user.food_ratings || []}
                                showAll={false}
                            />
                            <ReviewedFoods
                                reviews={user.reviews || []}
                                showAll={false}
                            />
                        </div>
                    </TabsContent>

                    {/* Ratings Tab */}
                    <TabsContent value="ratings">
                        <RatedFoods
                            foodRatings={user.food_ratings || []}
                            showAll={true}
                        />
                    </TabsContent>

                    {/* Reviews Tab */}
                    <TabsContent value="reviews">
                        <ReviewedFoods
                            reviews={user.reviews || []}
                            showAll={true}
                        />
                    </TabsContent>

                    {/* Settings Tab */}
                    <TabsContent value="settings" className="space-y-6">
                        <div className="grid gap-6 lg:grid-cols-2">
                            <ProfileEditForm
                                user={user}
                                onSuccess={handleProfileUpdate}
                            />
                            <PasswordChangeForm
                                onSuccess={handlePasswordUpdate}
                            />
                        </div>
                        <div className="grid gap-6 lg:grid-cols-2">
                            <PreferencesSection />
                            <LogoutSection />
                        </div>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
