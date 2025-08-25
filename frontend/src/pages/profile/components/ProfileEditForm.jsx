import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Save, User, Mail, FileText, Image } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { profileSchema, defaultProfileValues } from "../schemas/profile.schema";
import { useUpdateProfile } from "../hooks/useProfile";
import { useEffect } from "react";

export const ProfileEditForm = ({ user, onSuccess }) => {
    const { updateProfile, isUpdating } = useUpdateProfile();

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isDirty },
    } = useForm({
        resolver: zodResolver(profileSchema),
        defaultValues: defaultProfileValues,
    });

    // Reset form dengan data user saat user berubah
    useEffect(() => {
        if (user) {
            reset({
                name: user.name || "",
                email: user.email || "",
                bio: user.bio || "",
                avatar: user.avatar || "",
            });
        }
    }, [user, reset]);

    const onSubmit = async (data) => {
        try {
            await updateProfile(data);
            onSuccess?.();
        } catch {
            // Error sudah dihandle di hook
        }
    };

    return (
        <Card>
            <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <User className="w-5 h-5 text-primary" />
                    Edit Profile
                </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {/* Name */}
                    <div className="space-y-2">
                        <Label
                            htmlFor="name"
                            className="flex items-center gap-2 text-sm font-medium"
                        >
                            <User className="w-4 h-4 text-muted-foreground" />
                            Nama Lengkap
                        </Label>
                        <Input
                            id="name"
                            {...register("name")}
                            placeholder="Masukkan nama lengkap"
                            className={errors.name ? "border-destructive" : ""}
                        />
                        {errors.name && (
                            <p className="text-sm text-destructive">
                                {errors.name.message}
                            </p>
                        )}
                    </div>

                    {/* Email */}
                    <div className="space-y-2">
                        <Label
                            htmlFor="email"
                            className="flex items-center gap-2 text-sm font-medium"
                        >
                            <Mail className="w-4 h-4 text-muted-foreground" />
                            Email
                        </Label>
                        <Input
                            id="email"
                            type="email"
                            {...register("email")}
                            placeholder="Masukkan alamat email"
                            className={errors.email ? "border-destructive" : ""}
                        />
                        {errors.email && (
                            <p className="text-sm text-destructive">
                                {errors.email.message}
                            </p>
                        )}
                    </div>

                    {/* Bio */}
                    <div className="space-y-2">
                        <Label
                            htmlFor="bio"
                            className="flex items-center gap-2 text-sm font-medium"
                        >
                            <FileText className="w-4 h-4 text-muted-foreground" />
                            Bio
                        </Label>
                        <Textarea
                            id="bio"
                            {...register("bio")}
                            placeholder="Ceritakan tentang diri Anda..."
                            rows={3}
                            className={`resize-none ${
                                errors.bio ? "border-destructive" : ""
                            }`}
                        />
                        {errors.bio && (
                            <p className="text-sm text-destructive">
                                {errors.bio.message}
                            </p>
                        )}
                        <p className="text-xs text-muted-foreground">
                            Maksimal 500 karakter
                        </p>
                    </div>

                    {/* Avatar URL */}
                    <div className="space-y-2">
                        <Label
                            htmlFor="avatar"
                            className="flex items-center gap-2 text-sm font-medium"
                        >
                            <Image className="w-4 h-4 text-muted-foreground" />
                            URL Avatar
                        </Label>
                        <Input
                            id="avatar"
                            {...register("avatar")}
                            placeholder="https://example.com/avatar.jpg"
                            className={
                                errors.avatar ? "border-destructive" : ""
                            }
                        />
                        {errors.avatar && (
                            <p className="text-sm text-destructive">
                                {errors.avatar.message}
                            </p>
                        )}
                        <p className="text-xs text-muted-foreground">
                            URL gambar untuk foto profile Anda
                        </p>
                    </div>

                    {/* Submit Button */}
                    <div className="pt-2">
                        <Button
                            type="submit"
                            disabled={!isDirty || isUpdating}
                            className="w-full"
                        >
                            {isUpdating ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Menyimpan...
                                </>
                            ) : (
                                <>
                                    <Save className="w-4 h-4 mr-2" />
                                    Simpan Perubahan
                                </>
                            )}
                        </Button>

                        {!isDirty && (
                            <p className="text-xs text-muted-foreground text-center mt-2">
                                Tidak ada perubahan untuk disimpan
                            </p>
                        )}
                    </div>
                </form>
            </CardContent>
        </Card>
    );
};
