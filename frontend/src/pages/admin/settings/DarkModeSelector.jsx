import React from "react";
import { Check, Moon, Sun, Monitor } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

export default function DarkModeSelector({
    currentDarkMode,
    handleDarkModeChange,
}) {
    const modes = [
        {
            id: "light",
            name: "Mode Terang",
            description: "Antarmuka cerah dan bersih",
            icon: Sun,
            bgClass: "bg-yellow-100 dark:bg-yellow-900",
            iconClass: "text-yellow-600 dark:text-yellow-400",
        },
        {
            id: "dark",
            name: "Mode Gelap",
            description: "Lebih nyaman untuk mata",
            icon: Moon,
            bgClass: "bg-slate-100 dark:bg-slate-800",
            iconClass: "text-slate-600 dark:text-slate-400",
        },
        {
            id: "system",
            name: "Sistem",
            description: "Ikuti pengaturan perangkat",
            icon: Monitor,
            bgClass: "bg-blue-100 dark:bg-blue-900",
            iconClass: "text-blue-600 dark:text-blue-400",
        },
    ];

    return (
        <div className="grid gap-3 md:grid-cols-3">
            {modes.map((mode) => {
                const Icon = mode.icon;
                const isActive = currentDarkMode === mode.id;

                return (
                    <Card
                        key={mode.id}
                        className={`cursor-pointer transition-all duration-200 hover:border-primary/50 ${
                            isActive
                                ? "border-primary ring-1 ring-primary/20"
                                : ""
                        }`}
                        onClick={() => handleDarkModeChange(mode.id)}
                    >
                        <CardContent className="space-y-3 p-4 text-center">
                            <div className="flex justify-center">
                                <div
                                    className={`rounded-full ${mode.bgClass} p-3`}
                                >
                                    <Icon
                                        className={`h-6 w-6 ${mode.iconClass}`}
                                    />
                                </div>
                            </div>
                            <div>
                                <h5 className="text-sm font-medium">
                                    {mode.name}
                                </h5>
                                <p className="text-xs text-muted-foreground">
                                    {mode.description}
                                </p>
                            </div>
                            {isActive && (
                                <Badge variant="default" className="text-xs">
                                    <Check className="mr-1 h-3 w-3" />
                                    Aktif
                                </Badge>
                            )}
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}
