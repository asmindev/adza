import React from "react";
import { useTheme } from "@/contexts/ThemeContext";
import { Moon, Sun, Store, Home } from "lucide-react";
import { Link, useLocation } from "react-router";

export default function RootLayout({ children }) {
    const { theme, toggleTheme } = useTheme();
    const location = useLocation();

    return (
        <div
            className={`min-h-screen flex flex-col ${
                theme === "dark"
                    ? "bg-gray-900 bg-[url('/images/dark-pattern.png')] bg-fixed bg-opacity-95"
                    : "bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-100 bg-[url('/images/food-pattern.png')] bg-fixed bg-opacity-95"
            }`}
        >
            <header className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm py-4 sticky top-0 z-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    {/* Logo */}
                    <Link
                        to="/"
                        className="text-2xl font-bold text-accent dark:text-red-400"
                    >
                        Foodie
                    </Link>

                    {/* Navigation Menu */}
                    {/* <nav className="hidden md:flex items-center space-x-6">
                        <Link
                            to="/"
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                                location.pathname === "/"
                                    ? "bg-accent text-white"
                                    : "text-gray-700 dark:text-gray-300 hover:bg-accent/10"
                            }`}
                        >
                            <Home size={18} />
                            <span>Beranda</span>
                        </Link>
                        <Link
                            to="/restaurants"
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                                location.pathname === "/restaurants"
                                    ? "bg-accent text-white"
                                    : "text-gray-700 dark:text-gray-300 hover:bg-accent/10"
                            }`}
                        >
                            <Store size={18} />
                            <span>Restaurant</span>
                        </Link>
                    </nav> */}

                    {/* Theme Toggle */}
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                        aria-label={`Beralih ke mode ${
                            theme === "light" ? "gelap" : "terang"
                        }`}
                    >
                        {theme === "light" ? (
                            <Moon size={20} className="text-gray-800" />
                        ) : (
                            <Sun size={20} className="text-yellow-300" />
                        )}
                    </button>
                </div>

                {/* Mobile Navigation */}
                <div className="md:hidden mt-4 px-4">
                    <nav className="flex items-center justify-center space-x-4">
                        <Link
                            to="/"
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                                location.pathname === "/"
                                    ? "bg-accent text-white"
                                    : "text-gray-700 dark:text-gray-300 hover:bg-accent/10"
                            }`}
                        >
                            <Home size={18} />
                            <span>Beranda</span>
                        </Link>
                        <Link
                            to="/restaurants"
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                                location.pathname === "/restaurants"
                                    ? "bg-accent text-white"
                                    : "text-gray-700 dark:text-gray-300 hover:bg-accent/10"
                            }`}
                        >
                            <Store size={18} />
                            <span>Restaurant</span>
                        </Link>
                    </nav>
                </div>
            </header>

            <main className="w-full lg:w-10/12 mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-grow">
                {children}
            </main>

            <footer className="bg-white dark:bg-gray-800 shadow-inner py-4 mt-auto">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 dark:text-gray-400 text-sm">
                    &copy; {new Date().getFullYear()} Foodie Explorer. Hak Cipta
                    Dilindungi.
                </div>
            </footer>
        </div>
    );
}
