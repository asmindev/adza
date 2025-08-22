import React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/contexts/ThemeContext";

export default function ThemeSwitcher() {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className={`group relative flex h-8 w-14 items-center rounded-full bg-gray-200 dark:bg-gray-800 p-1 transition-colors duration-200`}
            aria-label={`Switch to ${
                theme === "light" ? "dark" : "light"
            } mode`}
            role="switch"
            aria-checked={theme === "dark"}
        >
            {/* Toggle Background */}
            <div
                className={`absolute inset-1 flex items-center justify-between rounded-full transition-all duration-200 bg-primary`}
            >
                {/* Icons */}
                <Sun
                    size={12}
                    className={`ml-1 transition-opacity duration-200 ${
                        theme === "light"
                            ? "text-yellow-500 opacity-100"
                            : "text-gray-400 opacity-50"
                    }`}
                />
                <Moon
                    size={12}
                    className={`mr-1 transition-opacity duration-200 ${
                        theme === "dark"
                            ? "text-white opacity-100"
                            : "text-gray-400 opacity-50"
                    }`}
                />
            </div>

            {/* Toggle Dot */}
            <div
                className={`relative z-10 h-6 w-6 rounded-full bg-white shadow-md transition-transform duration-200 ${
                    theme === "dark" ? "translate-x-6" : "translate-x-0"
                }`}
            >
                {/* Active Icon */}
                <div className="flex h-full w-full items-center justify-center">
                    {theme === "light" ? (
                        <Sun size={14} className="text-yellow-500" />
                    ) : (
                        <Moon size={14} className="text-blue-500" />
                    )}
                </div>
            </div>
        </button>
    );
}
