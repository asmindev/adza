import React from "react";
import { Store, Home } from "lucide-react";
import { Link, useLocation } from "react-router";
import ThemeSwitcher from "@/components/ui/ThemeSwitcher";
import { Footer } from "@/components/ui/footer";

export default function RootLayout({ children }) {
    const location = useLocation();

    return (
        <div className={`min-h-screen flex flex-col`}>
            <header className="backdrop-blur-sm py-4 sticky top-0 z-20 shadow">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    {/* Logo */}
                    <Link to="/" className="text-2xl font-bold text-primary">
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
                    <ThemeSwitcher />
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

            <main className="w-full mx-auto flex-grow">{children}</main>

            <Footer
                logo={
                    <span className="text-2xl font-bold text-primary">
                        Foodie
                    </span>
                }
                socialLinks={[
                    {
                        href: "https://twitter.com/yourprofile",
                        label: "Twitter",
                    },
                    {
                        href: "https://facebook.com/yourprofile",
                        label: "Facebook",
                    },
                    {
                        href: "https://instagram.com/yourprofile",
                        label: "Instagram",
                    },
                ]}
                mainLinks={[{ href: "/", label: "Home" }]}
                legalLinks={[
                    { href: "/terms", label: "Terms of Service" },
                    { href: "/privacy", label: "Privacy Policy" },
                ]}
                copyright={{
                    text: `© ${new Date().getFullYear()} Awesome Corp`,
                    license: "All rights reserved",
                }}
            />
        </div>
    );
}
