import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LogOut } from "lucide-react";
import { LogoutButton } from "./LogoutButton";

export const LogoutSection = () => {
    return (
        <Card>
            <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <LogOut className="w-5 h-5 text-destructive" />
                    Keluar Akun
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                    Keluar dari akun Anda dengan aman
                </p>
            </CardHeader>
            <CardContent className="pt-0">
                <div className="space-y-4">
                    <div className="p-4 bg-muted rounded-lg">
                        <h4 className="font-medium text-foreground mb-2">
                            Logout dari Akun
                        </h4>
                        <p className="text-sm text-muted-foreground mb-4">
                            Dengan logout, Anda akan keluar dari sesi saat ini
                            dan perlu login kembali untuk mengakses akun Anda.
                        </p>
                        <LogoutButton
                            variant="destructive"
                            size="sm"
                            className="w-full sm:w-auto"
                        />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
