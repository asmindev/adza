import React from "react";
import { Badge } from "@/components/ui/badge";
import {
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
} from "@/components/ui/card";
import { Sparkles } from "lucide-react";
import { getAllThemeColors } from "@/lib/theme";

export default function CurrentThemeInfo({ currentTheme }) {
    const themeColors = getAllThemeColors();
    const activeTheme = themeColors.find((theme) => theme.key === currentTheme);

    if (!activeTheme) return null;

    return (
        <>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div className="space-y-2">
                        <CardTitle className="flex items-center gap-2">
                            <Sparkles className="h-5 w-5 text-primary" />
                            Tema Aktif Saat Ini
                        </CardTitle>
                        <CardDescription>
                            Tema yang Anda pilih mempengaruhi seluruh antarmuka
                            admin
                        </CardDescription>
                    </div>
                    <Badge
                        variant="secondary"
                        className="bg-primary/10 text-primary"
                    >
                        Aktif
                    </Badge>
                </div>
            </CardHeader>
            <CardContent>
                <div className="flex items-center space-x-4">
                    {/* Color Preview */}
                    <div className="flex space-x-2">
                        <div
                            className={`h-8 w-8 rounded-lg border-2 border-white shadow-lg ${activeTheme.colorClass}`}
                            title="Primary Color"
                        />
                        <div
                            className={`h-8 w-8 rounded-lg border-2 border-white shadow-lg ${activeTheme.secondaryClass}`}
                            title="Secondary Color"
                        />
                        <div
                            className={`h-8 w-8 rounded-lg border-2 border-white shadow-lg ${activeTheme.accentClass}`}
                            title="Accent Color"
                        />
                    </div>

                    {/* Theme Info */}
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold">
                            {activeTheme.name}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                            {activeTheme.description}
                        </p>
                    </div>
                </div>
            </CardContent>
        </>
    );
}
