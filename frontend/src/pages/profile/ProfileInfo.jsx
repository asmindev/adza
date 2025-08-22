import React, { useState } from "react";
import { Edit2, Check, X } from "lucide-react";
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
        name: userData.name,
        username: userData.username,
        email: userData.email,
    });

    const { trigger: updateProfileMutation, isMutating } = useUpdateProfile();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async () => {
        try {
            await updateProfileMutation(formData);
            toast.success("Profile updated successfully");
            mutate();
            setIsEditing(false);
        } catch (error) {
            toast.error("Failed to update profile", {
                description: error.message || "Please try again later",
            });
        }
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
                            onClick={() => setIsEditing(false)}
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
                            <Check size={16} />
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
                                name="username"
                                value={formData.name}
                                onChange={handleChange}
                                className="mt-1"
                            />
                        ) : (
                            <p className="text-foreground mt-1">
                                {userData.name}
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
                                className="mt-1"
                            />
                        ) : (
                            <p className="text-foreground mt-1">
                                {userData.username}
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
                                value={formData.email}
                                onChange={handleChange}
                                className="mt-1"
                            />
                        ) : (
                            <p className="text-foreground mt-1">
                                {userData.email}
                            </p>
                        )}
                    </div>
                    <div>
                        <label className="text-sm font-medium text-muted-foreground">
                            Peran
                        </label>
                        <div className="mt-1">
                            <Badge variant="secondary" className="capitalize">
                                {userData.role}
                            </Badge>
                        </div>
                    </div>
                    <div>
                        <label className="text-sm font-medium text-muted-foreground">
                            Anggota Sejak
                        </label>
                        <p className="text-foreground mt-1">
                            {formatTimeAgo(userData.created_at)}
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6 pt-4 border-t">
                    <div>
                        <h3 className="text-lg font-medium mb-1">Penilaian</h3>
                        <p className="text-3xl font-bold">
                            {userData.ratings?.length || 0}
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
