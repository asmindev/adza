import React from "react";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
} from "@/components/ui/card";
import { Link } from "react-router";
import { ListPlus, ClipboardList, Users } from "lucide-react";

export default function QuickActionsSection() {
    return (
        <div className="grid gap-6 md:grid-cols-3">
            <Link to="/dashboard/foods/add" className="block">
                <Card className="h-full hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-xl font-bold">
                            Tambah Makanan
                        </CardTitle>
                        <ListPlus className="h-6 w-6 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <CardDescription className="text-md">
                            Buat item makanan baru dan tambahkan ke koleksi
                            Anda.
                        </CardDescription>
                    </CardContent>
                </Card>
            </Link>

            <Link to="/dashboard/foods" className="block">
                <Card className="h-full hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-xl font-bold">
                            Kelola Makanan
                        </CardTitle>
                        <ClipboardList className="h-6 w-6 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <CardDescription className="text-md">
                            Lihat, edit, dan hapus item makanan yang ada.
                        </CardDescription>
                    </CardContent>
                </Card>
            </Link>

            <Link to="/dashboard/users" className="block">
                <Card className="h-full hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-xl font-bold">
                            Kelola Pengguna
                        </CardTitle>
                        <Users className="h-6 w-6 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <CardDescription className="text-md">
                            Kelola pengguna dan izin mereka.
                        </CardDescription>
                    </CardContent>
                </Card>
            </Link>
        </div>
    );
}
