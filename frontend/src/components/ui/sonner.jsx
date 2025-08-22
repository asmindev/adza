import { useTheme } from "@/contexts/ThemeContext"; // Updated import
import { Toaster as Sonner } from "sonner";

const Toaster = ({ ...props }) => {
    const { theme = "light" } = useTheme(); // Use 'light' as default if theme is somehow undefined

    return (
        <Sonner
            theme={theme}
            className="toaster group"
            style={{
                "--normal-bg": "var(--popover)",
                "--normal-text": "var(--popover-foreground)",
                "--normal-border": "var(--border)",
            }}
            {...props}
        />
    );
};

export { Toaster };
