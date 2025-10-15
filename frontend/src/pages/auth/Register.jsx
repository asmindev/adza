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
import {
    Loader2,
    Mail,
    User,
    Lock,
    UserPlus,
    Eye,
    EyeOff,
    AlertCircle,
    CheckCircle,
} from "lucide-react";
import { toast } from "sonner";

// Define Zod validation schema
const registerSchema = z
    .object({
        name: z.string().min(2, { message: "Nama minimal 2 karakter" }),
        username: z
            .string()
            .min(3, { message: "Username minimal 3 karakter" })
            .regex(/^[a-zA-Z0-9_]+$/, {
                message:
                    "Username hanya boleh mengandung huruf, angka, dan underscore",
            }),
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
    const [showPassword, setShowPassword] = React.useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = React.useState(false);

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
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 via-white to-orange-50 p-4">
            {/* Background Image Overlay */}
            <div
                className="absolute inset-0 bg-cover bg-center opacity-10"
                style={{
                    backgroundImage: `url('https://akcdn.detik.net.id/community/media/visual/2022/02/03/masakan-indonesia.jpeg?w=1000&q=100')`,
                }}
            />

            <Card className="relative z-10 w-full max-w-lg shadow-2xl border-0 bg-white/95 backdrop-blur-sm">
                <CardHeader className="text-center space-y-4 pb-8">
                    <div className="mx-auto w-16 h-16 bg-gradient-to-r from-orange-400 to-orange-600 rounded-full flex items-center justify-center shadow-lg">
                        <UserPlus className="w-8 h-8 text-white" />
                    </div>
                    <div className="space-y-2">
                        <CardTitle className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                            Daftar Akun Baru
                        </CardTitle>
                        <p className="text-gray-600 text-sm leading-relaxed">
                            Bergabunglah untuk menjelajahi rekomendasi makanan
                            terbaik di Kendari
                        </p>
                    </div>
                </CardHeader>

                <CardContent className="space-y-6">
                    <form
                        className="space-y-5"
                        onSubmit={handleSubmit(onSubmit)}
                    >
                        {/* Name Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="name"
                                className="text-sm font-semibold text-gray-700 flex items-center gap-2"
                            >
                                <User className="w-4 h-4" />
                                Nama Lengkap
                            </Label>
                            <Input
                                id="name"
                                type="text"
                                placeholder="Masukkan nama lengkap Anda"
                                className="h-11 border-gray-200 focus:border-orange-400 focus:ring-orange-400/20 transition-all duration-200"
                                {...register("name")}
                            />
                            {errors.name && (
                                <p className="text-sm text-red-600 font-medium flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4" />
                                    {errors.name.message}
                                </p>
                            )}
                        </div>

                        {/* Username Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="username"
                                className="text-sm font-semibold text-gray-700 flex items-center gap-2"
                            >
                                <User className="w-4 h-4" />
                                Username
                            </Label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Masukkan username Anda"
                                className="h-11 border-gray-200 focus:border-orange-400 focus:ring-orange-400/20 transition-all duration-200"
                                {...register("username")}
                            />
                            {errors.username && (
                                <p className="text-sm text-red-600 font-medium flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4" />
                                    {errors.username.message}
                                </p>
                            )}
                        </div>

                        {/* Email Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="email"
                                className="text-sm font-semibold text-gray-700 flex items-center gap-2"
                            >
                                <Mail className="w-4 h-4" />
                                Email
                            </Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="Masukkan alamat email Anda"
                                className="h-11 border-gray-200 focus:border-orange-400 focus:ring-orange-400/20 transition-all duration-200"
                                {...register("email")}
                            />
                            {errors.email && (
                                <p className="text-sm text-red-600 font-medium flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4" />
                                    {errors.email.message}
                                </p>
                            )}
                        </div>

                        {/* Password Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="password"
                                className="text-sm font-semibold text-gray-700 flex items-center gap-2"
                            >
                                <Lock className="w-4 h-4" />
                                Password
                            </Label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="Masukkan password Anda"
                                    className="h-11 pr-10 border-gray-200 focus:border-orange-400 focus:ring-orange-400/20 transition-all duration-200"
                                    {...register("password")}
                                />
                                <button
                                    type="button"
                                    onClick={() =>
                                        setShowPassword(!showPassword)
                                    }
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    {showPassword ? (
                                        <EyeOff className="w-5 h-5" />
                                    ) : (
                                        <Eye className="w-5 h-5" />
                                    )}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="text-sm text-red-600 font-medium flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4" />
                                    {errors.password.message}
                                </p>
                            )}
                        </div>

                        {/* Confirm Password Field */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="confirmPassword"
                                className="text-sm font-semibold text-gray-700 flex items-center gap-2"
                            >
                                <Lock className="w-4 h-4" />
                                Konfirmasi Password
                            </Label>
                            <div className="relative">
                                <Input
                                    id="confirmPassword"
                                    type={
                                        showConfirmPassword
                                            ? "text"
                                            : "password"
                                    }
                                    placeholder="Masukkan ulang password Anda"
                                    className="h-11 pr-10 border-gray-200 focus:border-orange-400 focus:ring-orange-400/20 transition-all duration-200"
                                    {...register("confirmPassword")}
                                />
                                <button
                                    type="button"
                                    onClick={() =>
                                        setShowConfirmPassword(
                                            !showConfirmPassword
                                        )
                                    }
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                                >
                                    {showConfirmPassword ? (
                                        <EyeOff className="w-5 h-5" />
                                    ) : (
                                        <Eye className="w-5 h-5" />
                                    )}
                                </button>
                            </div>
                            {errors.confirmPassword && (
                                <p className="text-sm text-red-600 font-medium flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4" />
                                    {errors.confirmPassword.message}
                                </p>
                            )}
                        </div>

                        <Button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full h-11 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-70"
                        >
                            {isSubmitting ? (
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Mendaftar...
                                </div>
                            ) : (
                                <div className="flex items-center gap-2">
                                    <UserPlus className="w-4 h-4" />
                                    Daftar
                                </div>
                            )}
                        </Button>
                    </form>

                    {/* Login Link */}
                    <div className="relative pt-4">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-200" />
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-white px-3 text-gray-500 font-medium">
                                atau
                            </span>
                        </div>
                    </div>

                    <div className="text-center">
                        <p className="text-sm text-gray-600">
                            Sudah memiliki akun?{" "}
                            <Link
                                to="/login"
                                className="font-semibold text-orange-600 hover:text-orange-700 transition-colors"
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
