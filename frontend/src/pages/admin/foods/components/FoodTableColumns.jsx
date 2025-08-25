import {
    MoreHorizontal,
    Star,
    DollarSign,
    Store,
    ImageIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export const createFoodColumns = (setDeleteFoodId, setEditFoodData) => [
    {
        accessorKey: "name",
        header: "Makanan",
        cell: ({ row }) => (
            <div className="flex items-center space-x-3">
                <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                    {row.original.images && row.original.images.length > 0 ? (
                        // make collapsible image preview
                        row.original.images.map((image, index) => (
                            <img
                                key={index}
                                src={image.image_url}
                                alt={row.original.name}
                                className="size-12 rounded-lg object-cover"
                            />
                        ))
                    ) : (
                        <ImageIcon className="size-6 text-gray-400" />
                    )}
                </div>
                <div className="space-y-1">
                    <span className="font-medium">{row.original.name}</span>
                    <p className="text-sm text-muted-foreground truncate max-w-[200px]">
                        {row.original.description || "Tidak ada deskripsi"}
                    </p>
                </div>
            </div>
        ),
    },
    {
        accessorKey: "restaurant",
        header: "Restoran",
        cell: ({ row }) => (
            <div className="space-y-1">
                <div className="flex items-center">
                    <Store className="h-3 w-3 mr-1" />
                    <span className="font-medium">
                        {row.original.restaurant?.name || "Tidak ada restoran"}
                    </span>
                </div>
                <div className="text-sm text-muted-foreground">
                    {row.original.restaurant?.address || ""}
                </div>
            </div>
        ),
    },
    {
        accessorKey: "price",
        header: "Harga",
        cell: ({ row }) => (
            <div className="flex items-center space-x-1">
                <span className="font-medium">
                    {new Intl.NumberFormat("id-ID", {
                        style: "currency",
                        currency: "IDR",
                        minimumFractionDigits: 0,
                    }).format(row.original.price)}
                </span>
            </div>
        ),
    },
    {
        accessorKey: "category",
        header: "Kategori",
        cell: ({ row }) => (
            <Badge variant="outline">
                {row.original.category || "Tidak ada kategori"}
            </Badge>
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
                        {row.original.ratings?.average?.toFixed(1) || "N/A"}
                    </span>
                </div>
                <span className="text-sm text-muted-foreground">
                    ({row.original.reviews?.review_count || 0} review)
                </span>
            </div>
        ),
    },

    {
        accessorKey: "actions",
        header: "Aksi",
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
                        onClick={() => setEditFoodData(row.original)}
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
                        onClick={() => setDeleteFoodId(row.original.id)}
                        className="text-red-600"
                    >
                        Hapus
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        ),
    },
];
