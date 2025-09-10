import { useState } from "react";
import { Settings, Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { useProfile } from "../hooks/useProfile";
import PreferencesModal from "@/components/preferences/PreferencesModal";

const PreferencesSection = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const { user, isLoading, error } = useProfile();

    const userFavorites = user?.favorite_categories || [];

    const handleOpenModal = () => {
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
    };

    if (error) {
        toast.error("Gagal memuat preferensi");
    }

    return (
        <>
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                        <Settings className="w-5 h-5" />
                        Preferensi Kategori
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">
                        Atur kategori makanan favorit Anda untuk mendapatkan
                        rekomendasi yang lebih personal
                    </p>
                </CardHeader>
                <CardContent className="space-y-4">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="text-center">
                                <div className="w-6 h-6 mx-auto mb-2 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                                <p className="text-sm text-muted-foreground">
                                    Memuat preferensi...
                                </p>
                            </div>
                        </div>
                    ) : userFavorites.length > 0 ? (
                        <>
                            <div className="space-y-3">
                                <div className="text-sm font-medium text-foreground">
                                    Kategori Favorit ({userFavorites.length})
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {userFavorites.map((category) => (
                                        <Badge
                                            key={category.id}
                                            variant="secondary"
                                            className="text-sm py-1 px-3"
                                        >
                                            {category.name ||
                                                "Unknown Category"}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                            <Button
                                onClick={handleOpenModal}
                                variant="outline"
                                className="w-full"
                            >
                                <Settings className="w-4 h-4 mr-2" />
                                Edit Preferensi
                            </Button>
                        </>
                    ) : (
                        <div className="text-center py-8 space-y-4">
                            <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center">
                                <Settings className="w-8 h-8 text-muted-foreground" />
                            </div>
                            <div className="space-y-2">
                                <h3 className="font-medium text-foreground">
                                    Belum Ada Preferensi
                                </h3>
                                <p className="text-sm text-muted-foreground">
                                    Atur kategori favorit Anda untuk mendapatkan
                                    rekomendasi makanan yang lebih sesuai
                                </p>
                            </div>
                            <Button
                                onClick={handleOpenModal}
                                className="w-full"
                            >
                                <Plus className="w-4 h-4 mr-2" />
                                Atur Preferensi
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Preferences Modal/Drawer */}
            <PreferencesModal isOpen={isModalOpen} onClose={handleCloseModal} />
        </>
    );
};

export default PreferencesSection;
