import React, { useContext } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, Link } from "react-router";
import { UserContext } from "@/contexts/UserContextDefinition";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Mail, User, Lock, UserPlus } from "lucide-react";
import { toast } from "sonner";

// Define Zod validation schema
const registerSchema = z
    .object({
        name: z.string().min(2, { message: "Nama minimal 2 karakter" }),
        username: z.string()
            .min(3, { message: "Username minimal 3 karakter" })
            .regex(/^[a-zA-Z0-9_]+$/, { message: "Username hanya boleh mengandung huruf, angka, dan underscore" }),
        email: z.string().email({ message: "Format email tidak valid" }),
        password: z.string().min(6, { message: "Password minimal 6 karakter" }),
        confirmPassword: z
            .string()
            .min(6, { message: "Konfirmasi password minimal 6 karakter" }),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "Password dan konfirmasi password tidak sama",
        path: ["confirmPassword"],
    });

export default function Register() {
    const { user } = useContext(UserContext);
    const navigate = useNavigate();

    // Redirect if already logged in
    if (user?.email) {
        navigate("/");
    }

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data) => {
        try {
            // Use the actual username from the form
            const registerData = {
                username: data.username,
                email: data.email,
                password: data.password,
                name: data.name,
            };

            // Make actual API call to register endpoint
            const response = await fetch(
                `${import.meta.env.VITE_BASE_API_URL}/api/v1/auth/register`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(registerData),
                }
            );

            const result = await response.json();

            if (response.ok) {
                // Registration successful, show success toast and redirect
                toast.success(
                    "Registrasi berhasil! Silakan login dengan akun Anda."
                );
                navigate("/login");
            } else {
                // Handle different types of errors
                if (result.error_code === "VALIDATION_ERROR") {
                    // Show specific validation error details
                    const errorMessage =
                        result.details || result.message || "Validasi gagal";
                    toast.error(errorMessage);
                } else {
                    // Generic error
                    toast.error(
                        result.message || "Registrasi gagal. Silakan coba lagi."
                    );
                }
            }
        } catch (err) {
            toast.error(
                "Terjadi kesalahan saat registrasi. Silakan coba lagi."
            );
            console.error(err);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-cover bg-center bg-[url('https://akcdn.detik.net.id/community/media/visual/2022/02/03/masakan-indonesia.jpeg?w=1000&q=100')] p-4">
            {/* Full page overlay */}
            <div className="absolute inset-0 bg-black/30"></div>

            {/* Register Form - Modern Glassmorphism Card */}
            <Card className="w-full max-w-md z-10 bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
                <CardHeader className="text-center pb-6">
                    <div className="inline-block p-4 bg-orange-500/10 backdrop-blur-sm rounded-full mb-3 border border-orange-500/30 mx-auto">
                        <UserPlus className="text-orange-500 w-8 h-8" />
                    </div>
                    <CardTitle className="text-2xl font-bold text-white">
                        Daftar Akun Baru
                    </CardTitle>
                    <p className="text-sm text-gray-200 mt-2">
                        Bergabunglah untuk menjelajahi rekomendasi makanan
                        terbaik di Kendari
                    </p>
                </CardHeader>

                <CardContent className="space-y-6">
                    <form
                        className="space-y-4"
                        onSubmit={handleSubmit(onSubmit)}
                    >
                        {/* Name Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="name"
                                className="flex items-center gap-2 text-sm font-medium text-white"
                            >
                                <User className="w-4 h-4" />
                                Nama Lengkap
                            </Label>
                            <Input
                                id="name"
                                type="text"
                                placeholder="Masukkan nama lengkap"
                                className="bg-white/10 border-white/30 text-white placeholder-gray-300 backdrop-blur-sm focus-visible:border-orange-300 focus-visible:ring-orange-300/50"
                                {...register("name")}
                            />
                            {errors.name && (
                                <p className="text-sm text-red-300">
                                    {errors.name.message}
                                </p>
                            )}
                        </div>

                        {/* Username Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="username"
                                className="flex items-center gap-2 text-sm font-medium text-white"
                            >
                                <User className="w-4 h-4" />
                                Username
                            </Label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Masukkan username"
                                className="bg-white/10 border-white/30 text-white placeholder-gray-300 backdrop-blur-sm focus-visible:border-orange-300 focus-visible:ring-orange-300/50"
                                {...register("username")}
                            />
                            {errors.username && (
                                <p className="text-sm text-red-300">
                                    {errors.username.message}
                                </p>
                            )}
                        </div>

                        {/* Email Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="email"
                                className="flex items-center gap-2 text-sm font-medium text-white"
                            >
                                <Mail className="w-4 h-4" />
                                Email
                            </Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="Masukkan alamat email"
                                className="bg-white/10 border-white/30 text-white placeholder-gray-300 backdrop-blur-sm focus-visible:border-orange-300 focus-visible:ring-orange-300/50"
                                {...register("email")}
                            />
                            {errors.email && (
                                <p className="text-sm text-red-300">
                                    {errors.email.message}
                                </p>
                            )}
                        </div>

                        {/* Password Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="password"
                                className="flex items-center gap-2 text-sm font-medium text-white"
                            >
                                <Lock className="w-4 h-4" />
                                Password
                            </Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="Masukkan password"
                                className="bg-white/10 border-white/30 text-white placeholder-gray-300 backdrop-blur-sm focus-visible:border-orange-300 focus-visible:ring-orange-300/50"
                                {...register("password")}
                            />
                            {errors.password && (
                                <p className="text-sm text-red-300">
                                    {errors.password.message}
                                </p>
                            )}
                        </div>

                        {/* Confirm Password Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="confirmPassword"
                                className="flex items-center gap-2 text-sm font-medium text-white"
                            >
                                <Lock className="w-4 h-4" />
                                Konfirmasi Password
                            </Label>
                            <Input
                                id="confirmPassword"
                                type="password"
                                placeholder="Masukkan ulang password"
                                className="bg-white/10 border-white/30 text-white placeholder-gray-300 backdrop-blur-sm focus-visible:border-orange-300 focus-visible:ring-orange-300/50"
                                {...register("confirmPassword")}
                            />
                            {errors.confirmPassword && (
                                <p className="text-sm text-red-300">
                                    {errors.confirmPassword.message}
                                </p>
                            )}
                        </div>

                        <Button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full bg-orange-500 hover:bg-orange-600 text-white font-medium py-3 disabled:opacity-70 transition-colors"
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Mendaftar...
                                </>
                            ) : (
                                <>
                                    <UserPlus className="w-4 h-4 mr-2" />
                                    Daftar
                                </>
                            )}
                        </Button>
                    </form>

                    {/* Login Link */}
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/20"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-white/10 backdrop-blur-sm text-white rounded-md">
                                atau
                            </span>
                        </div>
                    </div>

                    <div className="text-center">
                        <p className="text-sm text-gray-200">
                            Sudah memiliki akun?{" "}
                            <Link
                                to="/login"
                                className="font-medium text-orange-300 hover:text-orange-200 transition-colors"
                            >
                                Masuk sekarang
                            </Link>
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
