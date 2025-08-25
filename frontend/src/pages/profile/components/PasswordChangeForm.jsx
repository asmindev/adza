import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Lock, Shield, Eye, EyeOff } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import {
    passwordSchema,
    defaultPasswordValues,
} from "../schemas/profile.schema";
import { useUpdatePassword } from "../hooks/useProfile";

export const PasswordChangeForm = ({ onSuccess }) => {
    const { updatePassword, isUpdating } = useUpdatePassword();
    const [showPasswords, setShowPasswords] = useState({
        current: false,
        new: false,
        confirm: false,
    });

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isValid },
        watch,
    } = useForm({
        resolver: zodResolver(passwordSchema),
        defaultValues: defaultPasswordValues,
        mode: "onChange",
    });

    const watchNewPassword = watch("newPassword");

    const onSubmit = async (data) => {
        try {
            await updatePassword(data);
            reset();
            onSuccess?.();
        } catch {
            // Error sudah dihandle di hook
        }
    };

    const togglePasswordVisibility = (field) => {
        setShowPasswords((prev) => ({
            ...prev,
            [field]: !prev[field],
        }));
    };

    const getPasswordStrength = (password) => {
        if (!password) return { score: 0, text: "", color: "" };

        let score = 0;
        if (password.length >= 8) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[a-z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;

        const strength = {
            0: { text: "Sangat Lemah", color: "text-destructive" },
            1: { text: "Lemah", color: "text-destructive" },
            2: { text: "Sedang", color: "text-primary" },
            3: { text: "Kuat", color: "text-primary" },
            4: { text: "Sangat Kuat", color: "text-primary" },
            5: { text: "Sangat Kuat", color: "text-primary" },
        };

        return { score, ...strength[score] };
    };

    const passwordStrength = getPasswordStrength(watchNewPassword);

    return (
        <Card>
            <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <Shield className="w-5 h-5 text-primary" />
                    Ubah Password
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                    Pastikan password baru Anda aman dan mudah diingat
                </p>
            </CardHeader>
            <CardContent className="pt-0">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {/* Current Password */}
                    <div className="space-y-2">
                        <Label
                            htmlFor="currentPassword"
                            className="flex items-center gap-2 text-sm font-medium"
                        >
                            <Lock className="w-4 h-4 text-muted-foreground" />
                            Password Saat Ini
                        </Label>
                        <div className="relative">
                            <Input
                                id="currentPassword"
                                type={
                                    showPasswords.current ? "text" : "password"
                                }
                                {...register("currentPassword")}
                                placeholder="Masukkan password saat ini"
                                className={`pr-10 ${
                                    errors.currentPassword
                                        ? "border-destructive"
                                        : ""
                                }`}
                            />
                            <button
                                type="button"
                                onClick={() =>
                                    togglePasswordVisibility("current")
                                }
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                            >
                                {showPasswords.current ? (
                                    <EyeOff className="w-4 h-4" />
                                ) : (
                                    <Eye className="w-4 h-4" />
                                )}
                            </button>
                        </div>
                        {errors.currentPassword && (
                            <p className="text-sm text-destructive">
                                {errors.currentPassword.message}
                            </p>
                        )}
                    </div>

                    {/* New Password */}
                    <div className="space-y-2">
                        <Label
                            htmlFor="newPassword"
                            className="flex items-center gap-2 text-sm font-medium"
                        >
                            <Lock className="w-4 h-4 text-muted-foreground" />
                            Password Baru
                        </Label>
                        <div className="relative">
                            <Input
                                id="newPassword"
                                type={showPasswords.new ? "text" : "password"}
                                {...register("newPassword")}
                                placeholder="Masukkan password baru"
                                className={`pr-10 ${
                                    errors.newPassword
                                        ? "border-destructive"
                                        : ""
                                }`}
                            />
                            <button
                                type="button"
                                onClick={() => togglePasswordVisibility("new")}
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                            >
                                {showPasswords.new ? (
                                    <EyeOff className="w-4 h-4" />
                                ) : (
                                    <Eye className="w-4 h-4" />
                                )}
                            </button>
                        </div>

                        {/* Password Strength Indicator */}
                        {watchNewPassword && (
                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-muted-foreground">
                                        Kekuatan Password:
                                    </span>
                                    <span
                                        className={`text-xs font-medium ${passwordStrength.color}`}
                                    >
                                        {passwordStrength.text}
                                    </span>
                                </div>
                                <div className="w-full bg-muted rounded-full h-2">
                                    <div
                                        className={`h-2 rounded-full transition-all duration-300 ${
                                            passwordStrength.score <= 2
                                                ? "bg-destructive"
                                                : "bg-primary"
                                        }`}
                                        style={{
                                            width: `${
                                                (passwordStrength.score / 5) *
                                                100
                                            }%`,
                                        }}
                                    ></div>
                                </div>
                            </div>
                        )}

                        {errors.newPassword && (
                            <p className="text-sm text-destructive">
                                {errors.newPassword.message}
                            </p>
                        )}
                    </div>

                    {/* Confirm Password */}
                    <div className="space-y-2">
                        <Label
                            htmlFor="confirmPassword"
                            className="flex items-center gap-2 text-sm font-medium"
                        >
                            <Lock className="w-4 h-4 text-muted-foreground" />
                            Konfirmasi Password
                        </Label>
                        <div className="relative">
                            <Input
                                id="confirmPassword"
                                type={
                                    showPasswords.confirm ? "text" : "password"
                                }
                                {...register("confirmPassword")}
                                placeholder="Konfirmasi password baru"
                                className={`pr-10 ${
                                    errors.confirmPassword
                                        ? "border-destructive"
                                        : ""
                                }`}
                            />
                            <button
                                type="button"
                                onClick={() =>
                                    togglePasswordVisibility("confirm")
                                }
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                            >
                                {showPasswords.confirm ? (
                                    <EyeOff className="w-4 h-4" />
                                ) : (
                                    <Eye className="w-4 h-4" />
                                )}
                            </button>
                        </div>
                        {errors.confirmPassword && (
                            <p className="text-sm text-destructive">
                                {errors.confirmPassword.message}
                            </p>
                        )}
                    </div>

                    {/* Password Requirements */}
                    <div className="bg-muted rounded-lg p-3">
                        <p className="text-xs font-medium text-foreground mb-2">
                            Persyaratan Password:
                        </p>
                        <ul className="text-xs text-muted-foreground space-y-1">
                            <li className="flex items-center gap-2">
                                <span
                                    className={
                                        watchNewPassword?.length >= 8
                                            ? "text-primary"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {watchNewPassword?.length >= 8 ? "✓" : "○"}
                                </span>
                                Minimal 8 karakter
                            </li>
                            <li className="flex items-center gap-2">
                                <span
                                    className={
                                        /[A-Z]/.test(watchNewPassword || "")
                                            ? "text-primary"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {/[A-Z]/.test(watchNewPassword || "")
                                        ? "✓"
                                        : "○"}
                                </span>
                                Huruf besar
                            </li>
                            <li className="flex items-center gap-2">
                                <span
                                    className={
                                        /[a-z]/.test(watchNewPassword || "")
                                            ? "text-primary"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {/[a-z]/.test(watchNewPassword || "")
                                        ? "✓"
                                        : "○"}
                                </span>
                                Huruf kecil
                            </li>
                            <li className="flex items-center gap-2">
                                <span
                                    className={
                                        /[0-9]/.test(watchNewPassword || "")
                                            ? "text-primary"
                                            : "text-muted-foreground"
                                    }
                                >
                                    {/[0-9]/.test(watchNewPassword || "")
                                        ? "✓"
                                        : "○"}
                                </span>
                                Angka
                            </li>
                        </ul>
                    </div>

                    {/* Submit Button */}
                    <div className="pt-2">
                        <Button
                            type="submit"
                            disabled={!isValid || isUpdating}
                            className="w-full"
                        >
                            {isUpdating ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Mengubah Password...
                                </>
                            ) : (
                                <>
                                    <Shield className="w-4 h-4 mr-2" />
                                    Ubah Password
                                </>
                            )}
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    );
};
