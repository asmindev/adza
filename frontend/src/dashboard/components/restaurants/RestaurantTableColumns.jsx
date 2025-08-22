import { MoreHorizontal, Star, MapPin, Phone, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export const createRestaurantColumns = (
    setDeleteRestaurantId,
    setEditRestaurantData
) => [
    {
        accessorKey: "name",
        header: "Nama Restoran",
        cell: ({ row }) => (
            <div className="space-y-1">
                <span className="font-medium">{row.original.name}</span>
                <div className="flex items-center text-sm text-muted-foreground">
                    <MapPin className="h-3 w-3 mr-1" />
                    <span className="truncate max-w-[200px]">
                        {row.original.address}
                    </span>
                </div>
            </div>
        ),
    },
    {
        accessorKey: "contact",
        header: "Kontak",
        cell: ({ row }) => (
            <div className="space-y-1">
                <div className="flex items-center text-sm">
                    <Phone className="h-3 w-3 mr-1" />
                    <span>{row.original.phone}</span>
                </div>
                <div className="flex items-center text-sm text-muted-foreground">
                    <Mail className="h-3 w-3 mr-1" />
                    <span>{row.original.email}</span>
                </div>
            </div>
        ),
    },
    {
        accessorKey: "rating.average",
        header: "Rating",
        cell: ({ row }) => (
            <div className="flex items-center space-x-2">
                <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-500 fill-yellow-500 mr-1" />
                    <span className="font-medium">
                        {row.original.rating?.average?.toFixed(1) || "N/A"}
                    </span>
                </div>
                <span className="text-sm text-muted-foreground">
                    ({row.original.rating?.total || 0} review)
                </span>
            </div>
        ),
    },
    {
        accessorKey: "foods",
        header: "Menu",
        cell: ({ row }) => {
            const foodCount = row.original.foods?.length || 0;
            const avgPrice =
                foodCount > 0
                    ? row.original.foods.reduce(
                          (sum, food) => sum + food.price,
                          0
                      ) / foodCount
                    : 0;

            return (
                <div className="space-y-1">
                    <span className="font-medium">{foodCount} makanan</span>
                    <div className="text-sm text-muted-foreground">
                        Rata-rata:{" "}
                        {new Intl.NumberFormat("id-ID", {
                            style: "currency",
                            currency: "IDR",
                            minimumFractionDigits: 0,
                        }).format(avgPrice)}
                    </div>
                </div>
            );
        },
    },
    {
        accessorKey: "description",
        header: "Deskripsi",
        cell: ({ row }) => (
            <span className="truncate block max-w-[250px]">
                {row.original.description || "Tidak ada deskripsi"}
            </span>
        ),
    },
    {
        accessorKey: "is_active",
        header: "Status",
        cell: ({ row }) => (
            <Badge
                variant={row.original.is_active ? "default" : "secondary"}
                className={
                    row.original.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                }
            >
                {row.original.is_active ? "Aktif" : "Tidak Aktif"}
            </Badge>
        ),
    },
    {
        accessorKey: "created_at",
        header: "Bergabung",
        cell: ({ row }) => {
            const date = new Date(row.original.created_at);
            return date.toLocaleDateString("id-ID", {
                day: "numeric",
                month: "long",
                year: "numeric",
            });
        },
    },
    {
        id: "actions",
        cell: ({ row }) => (
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Buka menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuItem
                        onClick={() => setEditRestaurantData(row.original)}
                    >
                        Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() => {
                            toast.info(
                                "Fitur lihat detail akan segera tersedia"
                            );
                        }}
                    >
                        Lihat Detail
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        onClick={() => setDeleteRestaurantId(row.original.id)}
                        className="text-red-600"
                    >
                        Hapus
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        ),
    },
];
