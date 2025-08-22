// Theme management utility
export const themes = {
    blue: "theme-blue",
    green: "theme-green",
    purple: "theme-purple",
};

export const themeNames = {
    "theme-blue": "Blue Theme",
    "theme-green": "Green Theme",
    "theme-purple": "Purple Theme",
};

// Dark mode options
export const darkModes = {
    light: "light",
    dark: "dark",
    system: "system",
};

export const darkModeNames = {
    light: "Light Mode",
    dark: "Dark Mode",
    system: "System",
};

// Theme color information with primary and secondary colors
export const themeColors = {
    "theme-blue": {
        name: "Blue Theme",
        primary: "oklch(0.546 0.207 264.376)",
        secondary: "oklch(0.925 0.035 264.376)",
        accent: "oklch(0.875 0.065 264.376)",
        description: "Professional blue palette with cool tones",
        colorClass: "bg-blue-500",
        secondaryClass: "bg-blue-100",
        accentClass: "bg-blue-200",
    },
    "theme-green": {
        name: "Green Theme",
        primary: "oklch(0.596 0.141 142.495)",
        secondary: "oklch(0.935 0.025 142.495)",
        accent: "oklch(0.885 0.055 142.495)",
        description: "Natural green palette with earthy tones",
        colorClass: "bg-green-500",
        secondaryClass: "bg-green-100",
        accentClass: "bg-green-200",
    },
    "theme-purple": {
        name: "Purple Theme",
        primary: "oklch(0.627 0.265 303.9)",
        secondary: "oklch(0.925 0.045 303.9)",
        accent: "oklch(0.875 0.085 303.9)",
        description: "Vibrant purple palette with creative tones",
        colorClass: "bg-purple-500",
        secondaryClass: "bg-purple-100",
        accentClass: "bg-purple-200",
    },
};

// Get current theme from localStorage or default
export function getCurrentTheme() {
    if (typeof window !== "undefined") {
        return localStorage.getItem("app-theme") || "theme-blue";
    }
    return "theme-blue";
}

// Get current dark mode from localStorage or default
export function getCurrentDarkMode() {
    if (typeof window !== "undefined") {
        return localStorage.getItem("app-dark-mode") || "system";
    }
    return "system";
}

// Check if system prefers dark mode
export function getSystemDarkMode() {
    if (typeof window !== "undefined") {
        return window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    return false;
}

// Get effective dark mode (resolves 'system' to actual preference)
export function getEffectiveDarkMode() {
    const currentMode = getCurrentDarkMode();
    if (currentMode === "system") {
        return getSystemDarkMode() ? "dark" : "light";
    }
    return currentMode;
}

// Set theme and apply to document
export function setTheme(theme) {
    if (typeof window !== "undefined") {
        // Remove all theme classes
        document.documentElement.classList.remove(...Object.values(themes));

        // Add new theme class
        document.documentElement.classList.add(theme);

        // Save to localStorage
        localStorage.setItem("app-theme", theme);
    }
}

// Set dark mode and apply to document
export function setDarkMode(mode) {
    if (typeof window !== "undefined") {
        // Save to localStorage
        localStorage.setItem("app-dark-mode", mode);

        // Apply the mode
        applyDarkMode();
    }
}

// Apply dark mode based on current setting
export function applyDarkMode() {
    if (typeof window !== "undefined") {
        const effectiveMode = getEffectiveDarkMode();

        if (effectiveMode === "dark") {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
    }
}

// Initialize theme and dark mode on app load
export function initializeTheme() {
    if (typeof window !== "undefined") {
        const currentTheme = getCurrentTheme();
        setTheme(currentTheme);
        applyDarkMode();

        // Listen for system dark mode changes
        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
        mediaQuery.addEventListener("change", () => {
            if (getCurrentDarkMode() === "system") {
                applyDarkMode();
            }
        });
    }
}

// Get theme color information
export function getThemeColors(theme = null) {
    const currentTheme = theme || getCurrentTheme();
    return themeColors[currentTheme] || themeColors["theme-blue"];
}

// Get all available theme colors for selection UI
export function getAllThemeColors() {
    return Object.entries(themeColors).map(([key, value]) => ({
        key,
        ...value,
    }));
}

// Toggle between themes
export function cycleTheme() {
    const currentTheme = getCurrentTheme();
    const themeList = Object.values(themes);
    const currentIndex = themeList.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themeList.length;
    const nextTheme = themeList[nextIndex];

    setTheme(nextTheme);
    return nextTheme;
}
