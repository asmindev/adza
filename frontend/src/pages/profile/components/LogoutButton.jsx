import { Button } from "@/components/ui/button";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { LogOut, Loader2 } from "lucide-react";
import { useLogout } from "../hooks/useProfile";

export const LogoutButton = ({
    variant = "outline",
    size = "default",
    className = "",
}) => {
    const { logout, isLoggingOut } = useLogout();

    const handleLogout = async () => {
        try {
            await logout();
        } catch {
            // Error already handled in hook
        }
    };

    return (
        <AlertDialog>
            <AlertDialogTrigger asChild>
                <Button
                    variant={variant}
                    size={size}
                    className={className}
                    disabled={isLoggingOut}
                >
                    {isLoggingOut ? (
                        <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Logging out...
                        </>
                    ) : (
                        <>
                            <LogOut className="w-4 h-4 mr-2" />
                            Logout
                        </>
                    )}
                </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Konfirmasi Logout</AlertDialogTitle>
                    <AlertDialogDescription>
                        Apakah Anda yakin ingin keluar dari akun? Anda perlu
                        login kembali untuk mengakses fitur yang memerlukan
                        autentikasi.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Batal</AlertDialogCancel>
                    <AlertDialogAction
                        onClick={handleLogout}
                        disabled={isLoggingOut}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                        {isLoggingOut ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Logging out...
                            </>
                        ) : (
                            <>
                                <LogOut className="w-4 h-4 mr-2" />
                                Ya, Logout
                            </>
                        )}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};
