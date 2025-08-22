import React, { useContext, useState } from "react";
import { motion } from "framer-motion";
import useSWR from "swr";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { UserContext } from "@/contexts/UserContextDefinition";
import { Card } from "@/components/ui/card";

import ProfileInfo from "./ProfileInfo";
import RatedFoods from "./RatedFoods";
import ReviewedFoods from "./ReviewedFoods";

export default function UserProfile() {
    const { user: currentUser } = useContext(UserContext);
    const [activeTab, setActiveTab] = useState("info");

    const {
        data: profileData,
        error,
        isLoading,
        mutate,
    } = useSWR(currentUser ? "/api/v1/me" : null, {
        revalidateOnFocus: false,
    });

    const userData = profileData?.data || null;

    if (error) {
        return (
            <div className="max-w-4xl mx-auto p-4 text-center">
                <Card className="p-8">
                    <h2 className="text-2xl font-bold mb-4">
                        Gagal Memuat Profil
                    </h2>
                    <p className="text-muted-foreground mb-6">
                        {error.message ||
                            "Kami tidak dapat memuat profil Anda. Silakan coba lagi nanti."}
                    </p>
                    <button
                        onClick={() => mutate()}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
                    >
                        Coba Lagi
                    </button>
                </Card>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="max-w-4xl mx-auto p-4">
                <Card className="p-6">
                    <div className="space-y-4">
                        <Skeleton className="h-10 w-1/3" />
                        <Skeleton className="h-32 w-full" />
                        <div className="flex space-x-2">
                            <Skeleton className="h-10 w-24" />
                            <Skeleton className="h-10 w-24" />
                            <Skeleton className="h-10 w-24" />
                        </div>
                        <Skeleton className="h-64 w-full" />
                    </div>
                </Card>
            </div>
        );
    }

    if (!userData) {
        return (
            <div className="max-w-4xl mx-auto p-4 text-center">
                <Card className="p-8">
                    <h2 className="text-2xl font-bold mb-4">
                        Profil Tidak Tersedia
                    </h2>
                    <p className="text-muted-foreground">
                        Silakan masuk untuk melihat profil Anda.
                    </p>
                </Card>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-4xl mx-auto p-4"
        >
            <h1 className="text-3xl font-bold mb-6">Profil Saya</h1>

            <Tabs
                defaultValue="info"
                value={activeTab}
                onValueChange={setActiveTab}
            >
                <TabsList className="mb-6 grid grid-cols-3 w-full md:w-auto">
                    <TabsTrigger value="info">Informasi Pribadi</TabsTrigger>
                    <TabsTrigger value="ratings">Penilaian Saya</TabsTrigger>
                    <TabsTrigger value="reviews">Ulasan Saya</TabsTrigger>
                </TabsList>

                <TabsContent value="info">
                    <ProfileInfo userData={userData} mutate={mutate} />
                </TabsContent>

                <TabsContent value="ratings">
                    <RatedFoods ratings={userData.ratings} />
                </TabsContent>

                <TabsContent value="reviews">
                    <ReviewedFoods reviews={userData.reviews} />
                </TabsContent>
            </Tabs>
        </motion.div>
    );
}
