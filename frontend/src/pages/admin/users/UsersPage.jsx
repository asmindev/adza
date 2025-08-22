import React, { useState } from "react";
import {
    flexRender,
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable,
} from "@tanstack/react-table";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, Plus, Search, UserCircle } from "lucide-react";
import useSWR from "swr";
import { motion, AnimatePresence } from "framer-motion";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import apiService from "@/dashboard/services/api";
import UserDialog from "@/dashboard/components/users/UserDialog";
import DeleteUserDialog from "@/dashboard/components/users/DeleteUserDialog";
import { toast } from "sonner";

export default function UsersPage() {
    const [pageIndex, setPageIndex] = useState(0);
    const [pageSize, setPageSize] = useState(10);
    const [searchTerm, setSearchTerm] = useState("");
    const [sorting, setSorting] = useState([]);
    const [userDialogData, setUserDialogData] = useState(null);
    const [deleteUserId, setDeleteUserId] = useState(null);

    // Fetch users with SWR
    const { data, error, mutate } = useSWR(
        [`/users`, pageIndex, pageSize, searchTerm],
        () => apiService.users.getAll(pageIndex + 1, pageSize, searchTerm),
        {
            revalidateOnFocus: false,
            onError: (err) => {
                toast.error(err.message);
            },
        }
    );

    console.log("Users data:", data);

    const users = data?.data?.data?.users || [];
    const totalCount = users?.length;
    const totalPages = Math.ceil(totalCount / pageSize);
    const isLoading = !data && !error;

    // Table columns definition
    const columns = [
        {
            accessorKey: "name",
            header: "Nama",
            cell: ({ row }) => (
                <div className="flex items-center space-x-3">
                    <Avatar>
                        <AvatarImage src={row.original.avatar || ""} />
                        <AvatarFallback>
                            {row.original.name?.charAt(0) || (
                                <UserCircle className="h-6 w-6" />
                            )}
                        </AvatarFallback>
                    </Avatar>
                    <span className="font-medium">{row.original.name}</span>
                </div>
            ),
        },
        {
            accessorKey: "email",
            header: "Email",
        },
        {
            accessorKey: "role",
            header: "Peran",
            cell: ({ row }) => {
                const role = row.original.role || "user";
                const roleStyles = {
                    admin: "bg-purple-100 text-purple-800",
                    moderator: "bg-blue-100 text-blue-800",
                    user: "bg-gray-100 text-gray-800",
                };

                return (
                    <Badge
                        className={roleStyles[role] || roleStyles.user}
                        variant="outline"
                    >
                        {role.charAt(0).toUpperCase() + role.slice(1)}
                    </Badge>
                );
            },
        },
        {
            accessorKey: "status",
            header: "Status",
            cell: ({ row }) => {
                const status = row.original.status || "active";
                const statusStyles = {
                    active: "bg-green-100 text-green-800",
                    inactive: "bg-red-100 text-red-800",
                    pending: "bg-yellow-100 text-yellow-800",
                };

                return (
                    <Badge className={statusStyles[status]} variant="outline">
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                    </Badge>
                );
            },
        },
        {
            accessorKey: "createdAt",
            header: "Bergabung",
            cell: ({ row }) => {
                const date = new Date(row.original.created_at);
                return date.toLocaleDateString(
                    "id-ID",
                    {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                    },
                    {
                        localeMatcher: "best fit",
                    }
                );
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
                            onClick={() =>
                                setUserDialogData({
                                    isNew: false,
                                    userData: row.original,
                                })
                            }
                        >
                            Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            onClick={() => setDeleteUserId(row.original.id)}
                            className="text-red-600"
                        >
                            Hapus
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            ),
        },
    ];

    // Setup table
    const table = useReactTable({
        data: users,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        onSortingChange: setSorting,
        state: {
            sorting,
            pagination: {
                pageIndex,
                pageSize,
            },
        },
        manualPagination: true,
        pageCount: totalPages,
    });

    // Handle search
    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
        setPageIndex(0); // Reset to first page on new search
    };

    // Handle refresh after operations
    const refreshData = () => {
        mutate();
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
                <h1 className="text-3xl font-bold tracking-tight">
                    Manajemen Pengguna
                </h1>
                <Button
                    onClick={() => setUserDialogData({ isNew: true })}
                    size="sm"
                >
                    <Plus className="h-4 w-4 mr-2" />
                    Tambah Pengguna
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Semua Pengguna</CardTitle>
                    <CardDescription>
                        Kelola pengguna platform makanan Anda. Tambahkan
                        pengguna baru atau ubah yang sudah ada.
                    </CardDescription>
                    <div className="flex w-full max-w-sm items-center space-x-2 mt-4">
                        <Search className="h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Cari pengguna..."
                            value={searchTerm}
                            onChange={handleSearch}
                            className="h-9"
                        />
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                {table.getHeaderGroups().map((headerGroup) => (
                                    <TableRow key={headerGroup.id}>
                                        {headerGroup.headers.map((header) => (
                                            <TableHead key={header.id}>
                                                {header.isPlaceholder
                                                    ? null
                                                    : flexRender(
                                                          header.column
                                                              .columnDef.header,
                                                          header.getContext()
                                                      )}
                                            </TableHead>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableHeader>
                            <TableBody>
                                {isLoading ? (
                                    <TableRow>
                                        <TableCell
                                            colSpan={columns.length}
                                            className="h-24 text-center"
                                        >
                                            Memuat pengguna...
                                        </TableCell>
                                    </TableRow>
                                ) : table.getRowModel().rows.length ? (
                                    <AnimatePresence>
                                        {table.getRowModel().rows.map((row) => (
                                            <motion.tr
                                                key={row.id}
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                layout
                                            >
                                                {row
                                                    .getVisibleCells()
                                                    .map((cell) => (
                                                        <TableCell
                                                            key={cell.id}
                                                        >
                                                            {flexRender(
                                                                cell.column
                                                                    .columnDef
                                                                    .cell,
                                                                cell.getContext()
                                                            )}
                                                        </TableCell>
                                                    ))}
                                            </motion.tr>
                                        ))}
                                    </AnimatePresence>
                                ) : (
                                    <TableRow>
                                        <TableCell
                                            colSpan={columns.length}
                                            className="h-24 text-center"
                                        >
                                            {searchTerm
                                                ? "Tidak ada pengguna yang cocok dengan pencarian Anda"
                                                : "Tidak ada pengguna ditemukan"}
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    <div className="flex items-center justify-between space-x-2 py-4">
                        <div className="flex-1 text-sm text-muted-foreground">
                            {totalCount > 0 && (
                                <span>
                                    Menampilkan {pageIndex * pageSize + 1}{" "}
                                    hingga{" "}
                                    {Math.min(
                                        (pageIndex + 1) * pageSize,
                                        totalCount
                                    )}{" "}
                                    dari {totalCount} pengguna
                                </span>
                            )}
                        </div>
                        <div className="flex items-center space-x-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPageIndex(pageIndex - 1)}
                                disabled={pageIndex === 0}
                            >
                                Sebelumnya
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPageIndex(pageIndex + 1)}
                                disabled={pageIndex === totalPages - 1}
                            >
                                Berikutnya
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* User Dialog (Add/Edit) */}
            {userDialogData && (
                <UserDialog
                    open={!!userDialogData}
                    onOpenChange={(open) => !open && setUserDialogData(null)}
                    isNew={userDialogData.isNew}
                    userData={userDialogData.userData}
                    onSuccess={refreshData}
                />
            )}

            {/* Delete User Dialog */}
            {deleteUserId && (
                <DeleteUserDialog
                    open={!!deleteUserId}
                    onOpenChange={(open) => !open && setDeleteUserId(null)}
                    userId={deleteUserId}
                    onSuccess={refreshData}
                />
            )}
        </div>
    );
}
