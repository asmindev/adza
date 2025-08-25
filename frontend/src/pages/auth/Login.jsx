import React, { useState, useContext } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, Link } from "react-router";
import { UserContext } from "@/contexts/UserContextDefinition";

// Define Zod validation schema
const loginSchema = z.object({
    username: z.string().min(1, { message: "Username tidak boleh kosong" }),
    password: z.string().min(1, { message: "Password tidak boleh kosong" }),
});

const Login = () => {
    const [serverError, setServerError] = useState("");
    const { login, user } = useContext(UserContext);
    const navigate = useNavigate();

    if (user?.email) {
        navigate("/");
    }

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
        <div className="min-h-screen flex items-center justify-center bg-cover bg-center bg-[url('https://akcdn.detik.net.id/community/media/visual/2022/02/03/masakan-indonesia.jpeg?w=1000&q=100')]">
            {/* Full page overlay */}
            <div className="absolute inset-0 bg-black/30"></div>

            {/* Login Form - Glassmorphism */}
            <div className="w-full max-w-md z-10 px-8 py-12 bg-black/10 sm:bg-white/10 sm:rounded-2xl sm:shadow-lg backdrop-blur-sm sm:backdrop-blur-md sm:border border-white/20">
                <div className="text-center mb-10">
                    <div className="inline-block p-4 bg-orange-500/10 backdrop-blur-sm rounded-full mb-3 border border-orange-500/30">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="text-orange-500 size-24"
                        >
                            <path d="M12 21a9 9 0 0 0 9-9H3a9 9 0 0 0 9 9Z" />
                            <path d="M7 21h10" />
                            <path d="M19.5 12 22 6" />
                            <path d="M16.25 3c.27.1.8.53.75 1.36-.06.83-.93 1.2-1 2.02-.05.78.34 1.24.73 1.62" />
                            <path d="M11.25 3c.27.1.8.53.74 1.36-.05.83-.93 1.2-.98 2.02-.06.78.33 1.24.72 1.62" />
                            <path d="M6.25 3c.27.1.8.53.75 1.36-.06.83-.93 1.2-1 2.02-.05.78.34 1.24.74 1.62" />
                        </svg>
                    </div>
                    <h2 className="text-3xl font-bold text-white">
                        Selamat Datang
                    </h2>
                    <p className="mt-2 text-sm text-gray-200">
                        Masuk untuk menjelajahi rekomendasi makanan di kota
                        Kendari
                    </p>
                </div>

                {serverError && (
                    <div className="mb-6 rounded-md bg-red-400/20 backdrop-blur-sm p-4 border border-red-500/50">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <svg
                                    className="h-5 w-5 text-red-300"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <h3 className="text-sm font-medium text-white">
                                    {serverError}
                                </h3>
                            </div>
                        </div>
                    </div>
                )}

                <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
                    <div>
                        <label
                            htmlFor="username"
                            className="block text-sm font-medium text-white"
                        >
                            Username
                        </label>
                        <div className="mt-1">
                            <input
                                placeholder="Username"
                                id="username"
                                type="text"
                                autoComplete="username"
                                className="block w-full rounded-md border border-white/30 bg-white/10 py-3 px-4 text-white placeholder-gray-300 backdrop-blur-sm focus:border-orange-300 focus:ring-orange-300"
                                {...register("username")}
                            />
                            {errors.username && (
                                <p className="mt-2 text-sm text-red-300">
                                    {errors.username.message}
                                </p>
                            )}
                        </div>
                    </div>

                    <div>
                        <label
                            htmlFor="password"
                            className="block text-sm font-medium text-white"
                        >
                            Password
                        </label>
                        <div className="mt-1">
                            <input
                                id="password"
                                type="password"
                                placeholder="Password"
                                autoComplete="current-password"
                                className="block w-full rounded-md border border-white/30 bg-white/10 py-3 px-4 text-white placeholder-gray-300 backdrop-blur-sm focus:border-orange-300 focus:ring-orange-300"
                                {...register("password")}
                            />
                            {errors.password && (
                                <p className="mt-2 text-sm text-red-300">
                                    {errors.password.message}
                                </p>
                            )}
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="group relative flex w-full justify-center rounded-md bg-orange-500 py-3 px-4 text-sm font-medium text-white hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-300 focus:ring-offset-2 disabled:opacity-70 transition-colors"
                        >
                            {isSubmitting ? (
                                <>
                                    <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                                        <svg
                                            className="h-5 w-5 animate-spin text-white"
                                            xmlns="http://www.w3.org/2000/svg"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                        >
                                            <circle
                                                className="opacity-25"
                                                cx="12"
                                                cy="12"
                                                r="10"
                                                stroke="currentColor"
                                                strokeWidth="4"
                                            ></circle>
                                            <path
                                                className="opacity-75"
                                                fill="currentColor"
                                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                            ></path>
                                        </svg>
                                    </span>
                                    Memproses...
                                </>
                            ) : (
                                "Masuk"
                            )}
                        </button>
                    </div>
                </form>

                <div className="mt-6">
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

                    <div className="mt-6 text-center">
                        <p className="text-sm text-gray-200">
                            Belum memiliki akun?{" "}
                            <Link
                                to="/register"
                                className="font-medium text-orange-300 hover:text-orange-200"
                            >
                                Daftar sekarang
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
