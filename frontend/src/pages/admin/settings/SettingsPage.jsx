import React, { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Check, Monitor, Moon, Palette, Sparkles, Sun } from "lucide-react";
import {
    getCurrentDarkMode,
    getCurrentTheme,
    setDarkMode,
    setTheme,
} from "@/pages/detail/components/lib/theme";
import ThemeSelector from "./ThemeSelector";
import DarkModeSelector from "./DarkModeSelector";
import CurrentThemeInfo from "./CurrentThemeInfo";

export default function SettingsPage() {
    const [currentTheme, setCurrentTheme] = useState("theme-blue");
    const [currentDarkMode, setCurrentDarkMode] = useState("system");
    const [isChanging, setIsChanging] = useState(false);

    useEffect(() => {
        setCurrentTheme(getCurrentTheme());
        setCurrentDarkMode(getCurrentDarkMode());
    }, []);

    const handleThemeChange = async (themeKey) => {
        setIsChanging(true);

        // Add a small delay for smooth transition
        setTimeout(() => {
            setTheme(themeKey);
            setCurrentTheme(themeKey);
            setIsChanging(false);
        }, 150);
    };

    const handleDarkModeChange = (mode) => {
        setDarkMode(mode);
        setCurrentDarkMode(mode);
    };

    return (
        <div className="container mx-auto max-w-6xl space-y-8 p-6">
            {/* Header Section */}
            <div className="space-y-4">
                <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/80">
                        <Palette className="h-6 w-6 text-primary-foreground" />
                    </div>
                    <div className="space-y-1">
                        <h1 className="text-3xl font-bold tracking-tight text-foreground">
                            Kustomisasi Tema
                        </h1>
                        <p className="text-muted-foreground">
                            Personalisasi panel admin Anda dengan tema warna
                            yang menarik
                        </p>
                    </div>
                </div>
                <Separator />
            </div>

            {/* Current Theme Info */}
            <Card className="border-primary/20 bg-gradient-to-r from-primary/5 to-primary/10">
                <CurrentThemeInfo currentTheme={currentTheme} />
            </Card>

            {/* Theme Selection */}
            <div className="space-y-6">
                <div>
                    <h2 className="mb-2 text-xl font-semibold">
                        Tema yang Tersedia
                    </h2>
                    <p className="mb-6 text-sm text-muted-foreground">
                        Pilih dari palet warna yang telah dirancang dengan
                        cermat untuk pengalaman pengguna yang optimal
                    </p>
                </div>

                <ThemeSelector
                    currentTheme={currentTheme}
                    handleThemeChange={handleThemeChange}
                    isChanging={isChanging}
                />
            </div>

            {/* Additional Settings */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Monitor className="h-5 w-5" />
                        Preferensi Tampilan
                    </CardTitle>
                    <CardDescription>
                        Sesuaikan tampilan antarmuka Anda
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Dark Mode Settings */}
                    <div className="space-y-4">
                        <div>
                            <h4 className="mb-2 text-sm font-medium">
                                Mode Tampilan
                            </h4>
                            <p className="mb-4 text-xs text-muted-foreground">
                                Pilih tampilan antarmuka atau biarkan mengikuti
                                preferensi sistem Anda
                            </p>
                        </div>

                        <DarkModeSelector
                            currentDarkMode={currentDarkMode}
                            handleDarkModeChange={handleDarkModeChange}
                        />
                    </div>

                    <Separator />

                    {/* Future Features */}
                    <div className="flex items-center justify-between rounded-lg border p-4 opacity-50">
                        <div className="space-y-1">
                            <h4 className="font-medium">Warna Kustom</h4>
                            <p className="text-sm text-muted-foreground">
                                Buat palet warna Anda sendiri (Segera Hadir)
                            </p>
                        </div>
                        <Button variant="outline" size="sm" disabled>
                            <Palette className="mr-2 h-4 w-4" />
                            Kustomisasi
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Help Section */}
            <Card className="bg-muted/50">
                <CardContent className="pt-6">
                    <div className="space-y-2 text-center">
                        <h3 className="font-semibold">💡 Tips Pro</h3>
                        <div className="space-y-1 text-sm text-muted-foreground">
                            <p>
                                • Perubahan tema dan mode gelap diterapkan
                                langsung dan disimpan secara otomatis
                            </p>
                            <p>
                                • Mode sistem mengikuti preferensi tampilan
                                sistem operasi Anda
                            </p>
                            <p>
                                • Semua perubahan disimpan dan akan tetap ada
                                saat Anda membuka kembali browser
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

SettingsPage.breadcrumbs = [{ label: "Settings" }];
