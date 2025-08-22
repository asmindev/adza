import { MoreHorizontal, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export const createUserColumns = (setEditUserData, setDeleteUserId) => [
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
                            setEditUserData({
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
