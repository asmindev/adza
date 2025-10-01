import React from "react";
import { Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { getAllThemeColors } from "@/pages/detail/components/lib/theme";

export default function ThemeSelector({
    currentTheme,
    handleThemeChange,
    isChanging,
}) {
    const themeColors = getAllThemeColors();

    return (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {themeColors.map((theme) => {
                const isActive = currentTheme === theme.key;

                return (
                    <Card
                        key={theme.key}
                        className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                            isActive
                                ? "border-primary/50 shadow-lg ring-2 ring-primary"
                                : "hover:border-primary/30"
                        } ${
                            isChanging ? "pointer-events-none opacity-50" : ""
                        }`}
                        onClick={() =>
                            !isActive && handleThemeChange(theme.key)
                        }
                    >
                        <CardHeader className="pb-4">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-lg font-semibold">
                                    {theme.name}
                                </CardTitle>
                                {isActive && (
                                    <Badge
                                        variant="default"
                                        className="bg-primary"
                                    >
                                        <Check className="mr-1 h-3 w-3" />
                                        Aktif
                                    </Badge>
                                )}
                            </div>
                            <CardDescription className="text-xs">
                                {theme.description}
                            </CardDescription>
                        </CardHeader>

                        <CardContent className="space-y-4">
                            {/* Large Color Preview */}
                            <div className="space-y-3">
                                <div className="flex space-x-2">
                                    <div
                                        className={`h-16 flex-1 rounded-lg border shadow-sm ${theme.colorClass} flex items-center justify-center`}
                                    >
                                        <span className="text-xs font-medium text-white">
                                            Primary
                                        </span>
                                    </div>
                                    <div className="space-y-2">
                                        <div
                                            className={`h-7 w-14 rounded border shadow-sm ${theme.secondaryClass} flex items-center justify-center`}
                                        >
                                            <span className="text-xs opacity-70">
                                                2nd
                                            </span>
                                        </div>
                                        <div
                                            className={`h-7 w-14 rounded border shadow-sm ${theme.accentClass} flex items-center justify-center`}
                                        >
                                            <span className="text-xs opacity-70">
                                                Acc
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Theme Actions */}
                            <div className="pt-2">
                                {isActive ? (
                                    <Button
                                        disabled
                                        className="w-full"
                                        variant="default"
                                    >
                                        <Check className="mr-2 h-4 w-4" />
                                        Sedang Aktif
                                    </Button>
                                ) : (
                                    <Button
                                        variant="outline"
                                        className="w-full hover:bg-primary hover:text-primary-foreground"
                                        onClick={() =>
                                            handleThemeChange(theme.key)
                                        }
                                    >
                                        <span className="mr-2">🎨</span>
                                        Terapkan Tema
                                    </Button>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}
