import React, { useState, useEffect } from "react";
import { Edit2, Check, X, Loader2 } from "lucide-react";
import { useUpdateProfile } from "@/lib/api";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatTimeAgo } from "@/utils";

export default function ProfileInfo({ userData, mutate }) {
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: userData?.name || "",
        username: userData?.username || "",
        email: userData?.email || "",
    });

    // Update form data when userData changes
    useEffect(() => {
        setFormData({
            name: userData?.name || "",
            username: userData?.username || "",
            email: userData?.email || "",
        });
    }, [userData]);

    const { trigger: updateProfileMutation, isMutating } = useUpdateProfile();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async () => {
        // Basic validation
        if (!formData.name?.trim()) {
            toast.error("Name is required");
            return;
        }

        if (!formData.username?.trim()) {
            toast.error("Username is required");
            return;
        }

        if (!formData.email?.trim()) {
            toast.error("Email is required");
            return;
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            toast.error("Please enter a valid email address");
            return;
        }

        // Check if data actually changed
        const hasChanges =
            formData.name !== userData?.name ||
            formData.username !== userData?.username ||
            formData.email !== userData?.email;

        if (!hasChanges) {
            toast.info("No changes detected");
            setIsEditing(false);
            return;
        }

        try {
            await updateProfileMutation(formData);
            toast.success("Profile updated successfully");
            mutate(); // Revalidate the profile data
            // update(formData);
            setIsEditing(false);
        } catch (error) {
            console.error("Update profile error:", error);
            const errorMessage =
                error?.response?.data?.message ||
                error?.message ||
                "Please try again later";
            toast.error("Failed to update profile", {
                description: errorMessage,
            });
        }
    };

    const handleCancel = () => {
        // Reset form data to original values
        setFormData({
            name: userData?.name || "",
            username: userData?.username || "",
            email: userData?.email || "",
        });
        setIsEditing(false);
    };

    return (
        <Card>
            <CardHeader className="flex flex-row justify-between items-center">
                <CardTitle>Informasi Pribadi</CardTitle>
                {!isEditing ? (
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsEditing(true)}
                        className="flex items-center gap-1"
                    >
                        <Edit2 size={16} />
                        <span>Edit</span>
                    </Button>
                ) : (
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleCancel}
                            disabled={isMutating}
                            className="flex items-center gap-1"
                        >
                            <X size={16} />
                            <span>Batal</span>
                        </Button>
                        <Button
                            variant="default"
                            size="sm"
                            onClick={handleSubmit}
                            disabled={isMutating}
                            className="flex items-center gap-1"
                        >
                            {isMutating ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Check size={16} />
                            )}
                            <span>
                                {isMutating ? "Menyimpan..." : "Simpan"}
                            </span>
                        </Button>
                    </div>
                )}
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="text-sm font-medium text-muted-foreground">
                            Nama
                        </label>
                        {isEditing ? (
                            <Input
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                disabled={isMutating}
                                className="mt-1"
                                placeholder="Enter your name"
                            />
                        ) : (
                            <p className="text-foreground mt-1">
                                {userData?.name || "-"}
                            </p>
                        )}
                    </div>
                    <div>
                        <label className="text-sm font-medium text-muted-foreground">
                            Nama Pengguna
                        </label>
                        {isEditing ? (
                            <Input
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                disabled={isMutating}
                                className="mt-1"
                                placeholder="Enter your username"
                            />
                        ) : (
                            <p className="text-foreground mt-1">
                                {userData?.username || "-"}
                            </p>
                        )}
                    </div>
                    <div>
                        <label className="text-sm font-medium text-muted-foreground">
                            Email
                        </label>
                        {isEditing ? (
                            <Input
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleChange}
                                disabled={isMutating}
                                className="mt-1"
                                placeholder="Enter your email"
                            />
                        ) : (
                            <p className="text-foreground mt-1">
                                {userData?.email || "-"}
                            </p>
                        )}
                    </div>
                    <div>
                        <label className="text-sm font-medium text-muted-foreground">
                            Peran
                        </label>
                        <div className="mt-1">
                            <Badge variant="secondary" className="capitalize">
                                {userData?.role || "User"}
                            </Badge>
                        </div>
                    </div>
                    <div>
                        <label className="text-sm font-medium text-muted-foreground">
                            Anggota Sejak
                        </label>
                        <p className="text-foreground mt-1">
                            {userData?.created_at
                                ? formatTimeAgo(userData.created_at)
                                : "-"}
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6 pt-4 border-t">
                    <div>
                        <h3 className="text-lg font-medium mb-1">Penilaian</h3>
                        <p className="text-3xl font-bold">
                            {userData.food_ratings?.length || 0}
                        </p>
                    </div>
                    <div>
                        <h3 className="text-lg font-medium mb-1">Ulasan</h3>
                        <p className="text-3xl font-bold">
                            {userData.reviews?.length || 0}
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
