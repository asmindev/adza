// src/components/layout/RootLayout.tsx
import React, { useContext, useState } from "react";
import { Link, Outlet, useLocation } from "react-router";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, ChefHat, User } from "lucide-react";
import ThemeSwitcher from "@/components/ui/ThemeSwitcher";
import { Footer } from "@/components/ui/footer";
import { UserContext } from "@/contexts/UserContextDefinition";

export default function RootLayout() {
    const [open, setOpen] = useState(false);
    const { user } = useContext(UserContext);
    const location = useLocation();

    /* ---------- Desktop Nav ---------- */
    const navLinks = [
        { label: "Beranda", href: "/" },
        { label: "Restoran", href: "/restaurants", icon: ChefHat },
        { label: "Rekomendasi", href: "/recommendation" },
        { label: "Populer", href: "/popular" },
        ...(user ? [{ label: "Profile", href: "/profile", icon: User }] : []),
    ];

    const renderDesktopNav = () => (
        <nav className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => {
                const isActive = location.pathname === link.href;
                const IconComponent = link.icon;
                return (
                    <Link
                        key={link.label}
                        to={link.href}
                        className={`
                            relative text-sm font-medium transition-all duration-300 group flex items-center gap-1.5
                            ${
                                isActive
                                    ? "text-primary"
                                    : "text-foreground/70 hover:text-foreground"
                            }
                        `}
                    >
                        {IconComponent && <IconComponent size={16} />}
                        {link.label}
                        <span
                            className={`
                                absolute -bottom-1 left-0 h-0.5 bg-primary transition-all duration-300
                                ${
                                    isActive
                                        ? "w-full"
                                        : "w-0 group-hover:w-full"
                                }
                            `}
                        />
                    </Link>
                );
            })}
        </nav>
    );

    /* ---------- Mobile Drawer ---------- */
    const drawerVariants = {
        closed: { x: "-100%" },
        open: { x: 0 },
    };

    const linkVariants = {
        hidden: { opacity: 0, x: -20 },
        visible: { opacity: 1, x: 0 },
        exit: { opacity: 0, x: -20 },
    };

    const containerVariants = {
        hidden: {},
        visible: {
            transition: {
                staggerChildren: 0.15,
                delayChildren: 0.1,
            },
        },
    };

    const renderMobileDrawer = () => (
        <AnimatePresence mode="wait">
            {open && (
                <>
                    {/* Overlay */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setOpen(false)}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
                    />

                    {/* Drawer */}
                    <motion.div
                        variants={drawerVariants}
                        initial="closed"
                        animate="open"
                        exit="closed"
                        transition={{
                            type: "spring",
                            stiffness: 300,
                            damping: 30,
                        }}
                        className="fixed top-0 left-0 h-full w-80 bg-background/95 backdrop-blur-xl border-r border-border/50 shadow-2xl z-50 flex flex-col pt-24 px-6"
                    >
                        <button
                            onClick={() => setOpen(false)}
                            className="absolute top-6 left-6 p-2 rounded-full hover:bg-accent transition-colors text-foreground/60 hover:text-foreground"
                        >
                            <X size={20} />
                        </button>

                        <motion.div
                            variants={containerVariants}
                            initial="hidden"
                            animate="visible"
                            className="space-y-2"
                        >
                            {navLinks.map((link) => {
                                const isActive =
                                    location.pathname === link.href;
                                const IconComponent = link.icon;
                                return (
                                    <motion.div
                                        key={link.label}
                                        variants={linkVariants}
                                        transition={{
                                            type: "spring",
                                            stiffness: 300,
                                            damping: 25,
                                        }}
                                    >
                                        <Link
                                            to={link.href}
                                            onClick={() => setOpen(false)}
                                            className={`
                                                py-3 px-4 rounded-lg text-3xl transition-all duration-200 font-bold flex items-center gap-3
                                                ${
                                                    isActive
                                                        ? "bg-primary/10 text-primary"
                                                        : "hover:bg-accent hover:pl-6 text-foreground/60"
                                                }
                                            `}
                                        >
                                            {IconComponent && (
                                                <IconComponent size={28} />
                                            )}
                                            {link.label}
                                        </Link>
                                    </motion.div>
                                );
                            })}
                        </motion.div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );

    /* ---------- Header ---------- */
    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-br from-background via-background to-accent/5">
            <header className="bg-background/80 backdrop-blur-md border-b border-border/50 py-4 sticky top-0 z-[90000] shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    {/* Logo */}
                    <Link
                        to="/"
                        className="flex items-center gap-2 text-2xl font-bold text-primary"
                    >
                        <span className="bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
                            Foodie
                        </span>
                    </Link>

                    {/* Desktop Nav + Theme */}
                    <div className="hidden md:flex items-center gap-8">
                        {renderDesktopNav()}
                        <div className="w-px h-6 bg-border" />
                        <ThemeSwitcher />
                    </div>

                    {/* Mobile Controls */}
                    <div className="flex md:hidden items-center gap-4">
                        <ThemeSwitcher />
                        <button
                            onClick={() => {
                                setOpen(!open);
                            }}
                            className="p-2 rounded-lg hover:bg-accent transition-colors"
                        >
                            <Menu size={20} />
                        </button>
                    </div>
                </div>
            </header>

            {renderMobileDrawer()}

            <main className="w-full mx-auto flex-grow relative">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="min-h-full"
                >
                    <Outlet />
                </motion.div>
            </main>

            <Footer
                logo={
                    <div className="flex items-center gap-2">
                        <ChefHat className="w-6 h-6 text-primary" />
                        <span className="text-xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
                            Foodie
                        </span>
                    </div>
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
