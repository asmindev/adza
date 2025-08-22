import React, { createContext, useContext, useState, useEffect } from "react";
import {
    initializeTheme,
    getEffectiveDarkMode,
    getCurrentTheme,
    setTheme as setLibTheme,
    setDarkMode as setLibDarkMode,
    getCurrentDarkMode,
    getSystemDarkMode,
} from "@/lib/theme";

const ThemeContext = createContext(null);

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error("useTheme must be used within a ThemeProvider");
    }
    return context;
};

export const ThemeProvider = ({ children }) => {
    // Initialize theme
    useEffect(() => {
        initializeTheme();
    }, []);

    // State for light/dark mode
    const [theme, setThemeState] = useState(() => getEffectiveDarkMode());

    // State for theme preference (system, light, dark)
    const [themePreference, setThemePreferenceState] = useState(() => {
        return getCurrentDarkMode();
    });

    // State for color theme
    const [activeColorTheme, setActiveColorThemeState] = useState(() => {
        return getCurrentTheme();
    });

    // Listen for system theme changes if preference is set to system
    useEffect(() => {
        if (themePreference === "system") {
            const mediaQuery = window.matchMedia(
                "(prefers-color-scheme: dark)"
            );

            const handleChange = () => {
                setThemeState(getSystemDarkMode() ? "dark" : "light");
            };

            mediaQuery.addEventListener("change", handleChange);

            return () => {
                mediaQuery.removeEventListener("change", handleChange);
            };
        } else {
            setThemeState(themePreference);
        }
    }, [themePreference]);

    const toggleTheme = () => {
        const newTheme = theme === "light" ? "dark" : "light";
        setThemeState(newTheme);
        setLibDarkMode(newTheme);
        setThemePreferenceState(newTheme);
    };

    const setThemePreference = (preference) => {
        setThemePreferenceState(preference);
        setLibDarkMode(preference);
        if (preference === "system") {
            setThemeState(getSystemDarkMode() ? "dark" : "light");
        } else {
            setThemeState(preference);
        }
    };

    const setColorTheme = (newColorTheme) => {
        setActiveColorThemeState(newColorTheme);
        setLibTheme(newColorTheme);
    };

    return (
        <ThemeContext.Provider
            value={{
                theme,
                toggleTheme,
                themePreference,
                setThemePreference,
                colorTheme: activeColorTheme,
                setColorTheme,
            }}
        >
            {children}
        </ThemeContext.Provider>
    );
};

export default ThemeContext;
