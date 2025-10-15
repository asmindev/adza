import React, { useState, useContext } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, Link } from "react-router";
import { UserContext } from "@/contexts/UserContextDefinition";
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, LogIn, AlertCircle, Salad } from "lucide-react";

// Define Zod validation schema
const loginSchema = z.object({
    username: z.string().min(1, { message: "Username tidak boleh kosong" }),
    password: z.string().min(1, { message: "Password tidak boleh kosong" }),
});

const Login = () => {
    const [serverError, setServerError] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const { login } = useContext(UserContext);
    const navigate = useNavigate();

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data) => {
        setServerError("");

        try {
            const result = await login(data);

            if (result.success) {
                navigate("/");
            } else {
                setServerError(
                    result.message ||
                        "Login gagal. Silakan periksa username dan password Anda."
                );
            }
        } catch (err) {
            setServerError("Terjadi kesalahan saat login. Silakan coba lagi.");
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

            <Card className="relative z-10 w-full max-w-md shadow-2xl border-0 bg-white/95 backdrop-blur-sm">
                <CardHeader className="text-center space-y-4 pb-8">
                    <div className="mx-auto w-16 h-16 bg-gradient-to-r from-orange-400 to-orange-600 rounded-full flex items-center justify-center shadow-lg">
                        <Salad
                            strokeWidth={1.2}
                            className="size-12c text-white"
                        />
                    </div>
                    <div className="space-y-2">
                        <CardTitle className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                            Selamat Datang
                        </CardTitle>
                        <p className="text-gray-600 text-sm leading-relaxed">
                            Masuk untuk menjelajahi rekomendasi makanan terbaik
                            di Kendari
                        </p>
                    </div>
                </CardHeader>

                <CardContent className="space-y-6">
                    {serverError && (
                        <div className="flex items-start gap-3 p-4 rounded-lg bg-red-50 border border-red-200">
                            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-red-700 font-medium">
                                {serverError}
                            </p>
                        </div>
                    )}

                    <form
                        onSubmit={handleSubmit(onSubmit)}
                        className="space-y-5"
                    >
                        <div className="space-y-2">
                            <Label
                                htmlFor="username"
                                className="text-sm font-semibold text-gray-700"
                            >
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

                        <div className="space-y-2">
                            <Label
                                htmlFor="password"
                                className="text-sm font-semibold text-gray-700"
                            >
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

                        <Button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full h-11 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-70"
                        >
                            {isSubmitting ? (
                                <div className="flex items-center gap-2">
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Memproses...
                                </div>
                            ) : (
                                <div className="flex items-center gap-2">
                                    <LogIn className="w-4 h-4" />
                                    Masuk
                                </div>
                            )}
                        </Button>
                    </form>
                </CardContent>

                <CardFooter className="pt-6">
                    <div className="w-full text-center space-y-4">
                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-gray-200" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-white px-3 text-gray-500 font-medium">
                                    atau
                                </span>
                            </div>
                        </div>

                        <p className="text-sm text-gray-600">
                            Belum memiliki akun?{" "}
                            <Link
                                to="/register"
                                className="font-semibold text-orange-600 hover:text-orange-700 transition-colors"
                            >
                                Daftar sekarang
                            </Link>
                        </p>
                    </div>
                </CardFooter>
            </Card>
        </div>
    );
};

export default Login;
