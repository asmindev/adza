import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Search,
    Plus,
    Filter,
    Eye,
    Edit,
    Trash2,
    MoreHorizontal,
} from "lucide-react";
import { toast } from "sonner";
import AddFoodDialog from "@/dashboard/components/foods/AddFoodDialog";
import EditFoodDialog from "@/dashboard/components/foods/EditFoodDialog";
import DeleteFoodDialog from "@/dashboard/components/foods/DeleteFoodDialog";
import apiService from "@/dashboard/services/api";
import useSWR from "swr";
import { AnimatePresence } from "framer-motion";

export default function FoodsPage() {
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [categoryFilter, setCategoryFilter] = useState("all");
    const [page, setPage] = useState(1);
    const pageSize = 50;

    // Dialog states
    const [addDialogOpen, setAddDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedFood, setSelectedFood] = useState(null);

    // Fetch foods data
    const { data, error, mutate, isLoading } = useSWR(
        [`/foods`, page, pageSize, searchTerm, statusFilter, categoryFilter],
        () =>
            apiService.foods.getAll(
                page,
                pageSize,
                searchTerm,
                statusFilter === "all" ? "" : statusFilter,
                categoryFilter === "all" ? "" : categoryFilter
            ),
        {
            revalidateOnFocus: false,
            onError: () => {
                toast.error("Gagal memuat data makanan");
            },
        }
    );

    const foods = data?.data?.data?.foods || [];
    const pagination = data?.data?.data?.pagination || {};

    // Fetch restaurants for restaurant name display
    const { data: restaurantsData } = useSWR(
        ["/restaurants/list"],
        () => apiService.restaurants.getAll(1, 1000, ""),
        {
            revalidateOnFocus: false,
        }
    );

    const restaurants = restaurantsData?.data?.data?.restaurants || [];

    // Create a restaurant lookup map for quick access
    const restaurantMap = restaurants.reduce((acc, restaurant) => {
        acc[restaurant.id] = restaurant.name;
        return acc;
    }, {});

    // Handle search with debounce
    useEffect(() => {
        const timer = setTimeout(() => {
            setPage(1); // Reset to first page when searching
        }, 300);

        return () => clearTimeout(timer);
    }, [searchTerm, statusFilter, categoryFilter]);

    const handleEdit = (food) => {
        setSelectedFood(food);
        setEditDialogOpen(true);
    };

    const handleDelete = (food) => {
        setSelectedFood(food);
        setDeleteDialogOpen(true);
    };

    const handleSuccess = () => {
        mutate(); // Revalidate the data
    };

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
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Manajemen Makanan
                    </h1>
                    <p className="text-muted-foreground">
                        Kelola koleksi makanan Anda
                    </p>
                </div>
                <Button onClick={() => setAddDialogOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Tambah Makanan
                </Button>
            </div>

            {/* Filters */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Filter className="h-5 w-5" />
                        Filter & Pencarian
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col gap-4 md:flex-row md:items-end">
                        <div className="flex-1">
                            <label className="text-sm font-medium mb-2 block">
                                Cari Makanan
                            </label>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Cari berdasarkan nama makanan..."
                                    value={searchTerm}
                                    onChange={(e) =>
                                        setSearchTerm(e.target.value)
                                    }
                                    className="pl-10"
                                />
                            </div>
                        </div>

                        <div className="min-w-[150px]">
                            <label className="text-sm font-medium mb-2 block">
                                Status
                            </label>
                            <Select
                                value={statusFilter}
                                onValueChange={setStatusFilter}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">
                                        Semua Status
                                    </SelectItem>
                                    <SelectItem value="active">
                                        Aktif
                                    </SelectItem>
                                    <SelectItem value="inactive">
                                        Tidak Aktif
                                    </SelectItem>
                                    <SelectItem value="pending">
                                        Tertunda
                                    </SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="min-w-[150px]">
                            <label className="text-sm font-medium mb-2 block">
                                Kategori
                            </label>
                            <Select
                                value={categoryFilter}
                                onValueChange={setCategoryFilter}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">
                                        Semua Kategori
                                    </SelectItem>
                                    <SelectItem value="appetizer">
                                        Appetizer
                                    </SelectItem>
                                    <SelectItem value="main">
                                        Main Course
                                    </SelectItem>
                                    <SelectItem value="dessert">
                                        Dessert
                                    </SelectItem>
                                    <SelectItem value="beverage">
                                        Minuman
                                    </SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Foods Table */}
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
                                                            e.target.onerror =
                                                                null;
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
                                                    {getStatusBadge(
                                                        food.status
                                                    )}
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
                                                                    handleEdit(
                                                                        food
                                                                    )
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

                    {/* Pagination */}
                    {pagination.total_pages > 1 && (
                        <div className="flex items-center justify-between space-x-2 py-4">
                            <p className="text-sm text-muted-foreground">
                                Halaman {pagination.current_page} dari{" "}
                                {pagination.total_pages} ({pagination.total}{" "}
                                total)
                            </p>
                            <div className="space-x-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage(page - 1)}
                                    disabled={page <= 1}
                                >
                                    Sebelumnya
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage(page + 1)}
                                    disabled={page >= pagination.total_pages}
                                >
                                    Selanjutnya
                                </Button>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Dialogs */}
            <AddFoodDialog
                open={addDialogOpen}
                onOpenChange={setAddDialogOpen}
                onSuccess={handleSuccess}
            />

            <EditFoodDialog
                open={editDialogOpen}
                onOpenChange={setEditDialogOpen}
                foodData={selectedFood}
                onSuccess={handleSuccess}
            />

            <DeleteFoodDialog
                open={deleteDialogOpen}
                onOpenChange={setDeleteDialogOpen}
                food={selectedFood}
                onSuccess={handleSuccess}
            />
        </div>
    );
}
