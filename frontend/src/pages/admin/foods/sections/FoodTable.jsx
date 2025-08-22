import React from "react";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Edit, MoreHorizontal, Trash2 } from "lucide-react";
import { AnimatePresence } from "framer-motion";

export default function FoodTable({
    foods,
    restaurantMap,
    isLoading,
    error,
    pagination,
    handleEdit,
    handleDelete,
}) {
    const getStatusBadge = (status) => {
        const statusConfig = {
            active: { label: "Aktif", variant: "default" },
            inactive: { label: "Tidak Aktif", variant: "secondary" },
            pending: { label: "Tertunda", variant: "outline" },
        };

        const config = statusConfig[status] || statusConfig.pending;
        return (
            <Badge variant={config.variant} className="capitalize">
                {config.label}
            </Badge>
        );
    };

    const formatPrice = (price) => {
        return new Intl.NumberFormat("id-ID", {
            style: "currency",
            currency: "IDR",
        }).format(price);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>
                    Daftar Makanan ({pagination.total || 0} total)
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Gambar</TableHead>
                                <TableHead>Nama</TableHead>
                                <TableHead>Restoran</TableHead>
                                <TableHead>Kategori</TableHead>
                                <TableHead>Harga</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Rating</TableHead>
                                <TableHead className="text-right">
                                    Aksi
                                </TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            <AnimatePresence>
                                {isLoading ? (
                                    // Loading skeleton
                                    Array.from({ length: 5 }).map(
                                        (_, index) => (
                                            <TableRow key={index}>
                                                <TableCell>
                                                    <div className="w-12 h-12 bg-muted rounded animate-pulse"></div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="h-4 bg-muted rounded animate-pulse"></div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="h-4 bg-muted rounded animate-pulse"></div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="h-4 bg-muted rounded animate-pulse"></div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="h-4 bg-muted rounded animate-pulse"></div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="h-6 w-16 bg-muted rounded animate-pulse"></div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="h-4 bg-muted rounded animate-pulse"></div>
                                                </TableCell>
                                                <TableCell>
                                                    <div className="h-8 w-24 bg-muted rounded animate-pulse ml-auto"></div>
                                                </TableCell>
                                            </TableRow>
                                        )
                                    )
                                ) : foods.length === 0 ? (
                                    <TableRow>
                                        <TableCell
                                            colSpan={8}
                                            className="h-24 text-center"
                                        >
                                            {error
                                                ? "Gagal memuat data makanan"
                                                : "Tidak ada makanan ditemukan"}
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    foods.map((food) => (
                                        <TableRow key={food.id}>
                                            <TableCell>
                                                <img
                                                    src={
                                                        food.main_image
                                                            ?.image_url ||
                                                        food.images?.[0]
                                                            ?.image_url ||
                                                        "https://placehold.co/600x400@2x.png"
                                                    }
                                                    alt={food.name}
                                                    className="w-12 h-12 rounded object-cover"
                                                    onError={(e) => {
                                                        e.target.onerror = null;
                                                        e.target.src =
                                                            "https://via.placeholder.com/48?text=Error";
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell className="font-medium">
                                                {food.name}
                                            </TableCell>
                                            <TableCell>
                                                {restaurantMap[
                                                    food.restaurant_id
                                                ] || "Unknown Restaurant"}
                                            </TableCell>
                                            <TableCell>
                                                <Badge
                                                    variant="outline"
                                                    className="capitalize"
                                                >
                                                    {food.category}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                {formatPrice(food.price)}
                                            </TableCell>
                                            <TableCell>
                                                {getStatusBadge(food.status)}
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-1">
                                                    <span className="text-yellow-500">
                                                        ★
                                                    </span>
                                                    <span>
                                                        {food.average_rating?.toFixed(
                                                            1
                                                        ) || "N/A"}
                                                    </span>
                                                    <span className="text-muted-foreground text-sm">
                                                        (
                                                        {food.total_reviews ||
                                                            0}
                                                        )
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger
                                                        asChild
                                                    >
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                        >
                                                            <MoreHorizontal className="h-4 w-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuItem
                                                            onClick={() =>
                                                                handleEdit(food)
                                                            }
                                                        >
                                                            <Edit className="mr-2 h-4 w-4" />
                                                            Edit
                                                        </DropdownMenuItem>
                                                        <DropdownMenuSeparator />
                                                        <DropdownMenuItem
                                                            onClick={() =>
                                                                handleDelete(
                                                                    food
                                                                )
                                                            }
                                                            className="text-destructive"
                                                        >
                                                            <Trash2 className="mr-2 h-4 w-4" />
                                                            Hapus
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </AnimatePresence>
                        </TableBody>
                    </Table>
                </div>
            </CardContent>
        </Card>
    );
}
