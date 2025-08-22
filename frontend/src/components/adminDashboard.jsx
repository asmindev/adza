import {
    ListPlus,
    Home,
    BarChart3,
    ClipboardList,
    Settings,
    Store,
    Users,
    TrendingUp,
    Activity,
} from "lucide-react";
import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar";
import { Link } from "react-router";

// Menu groups for better organization
const menuGroups = [
    {
        label: "Dashboard",
        items: [
            {
                title: "Ikhtisar",
                url: "/dashboard",
                icon: Home,
                description: "Ringkasan umum dashboard",
            },
        ],
    },
    {
        label: "Manajemen Data",
        items: [
            {
                title: "Daftar Makanan",
                url: "/dashboard/foods",
                icon: ListPlus,
                description: "Kelola menu makanan",
            },
            {
                title: "Daftar Restoran",
                url: "/dashboard/restaurants",
                icon: Store,
                description: "Kelola data restoran",
            },
            {
                title: "Daftar Pengguna",
                url: "/dashboard/users",
                icon: Users,
                description: "Kelola akun pengguna",
            },
        ],
    },
    {
        label: "Analitik & Laporan",
        items: [
            {
                title: "Statistik",
                url: "/dashboard/stats",
                icon: BarChart3,
                description: "Lihat analitik data",
            },
            {
                title: "Aktivitas",
                url: "/dashboard/activity",
                icon: Activity,
                description: "Monitor aktivitas sistem",
            },
        ],
    },
    {
        label: "Sistem",
        items: [
            {
                title: "Pengaturan",
                url: "/dashboard/settings",
                icon: Settings,
                description: "Konfigurasi sistem",
            },
        ],
    },
];

export function AppSidebar() {
    return (
        <Sidebar className="border-r">
            <SidebarContent className="gap-0">
                {/* Header */}
                <div className="flex h-14 items-center border-b px-6">
                    <div className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                            <TrendingUp className="h-4 w-4" />
                        </div>
                        <span className="font-semibold">Food Admin</span>
                    </div>
                </div>

                {/* Menu Groups */}
                {menuGroups.map((group, groupIndex) => (
                    <SidebarGroup
                        key={group.label}
                        className={groupIndex > 0 ? "mt-6" : "mt-4"}
                    >
                        <SidebarGroupLabel className="px-6 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                            {group.label}
                        </SidebarGroupLabel>
                        <SidebarGroupContent className="px-3">
                            <SidebarMenu className="gap-1">
                                {group.items.map((item) => (
                                    <SidebarMenuItem key={item.title}>
                                        <SidebarMenuButton
                                            asChild
                                            className="group relative flex h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium hover:bg-accent hover:text-accent-foreground data-[active=true]:bg-accent data-[active=true]:text-accent-foreground"
                                            tooltip={item.description}
                                        >
                                            <Link
                                                to={item.url}
                                                className="flex items-start gap-3"
                                            >
                                                <item.icon className="h-4 w-4 shrink-0 -mt-0.5 " />
                                                <div className="flex flex-col -mt-1.5">
                                                    <span className="text-sm">
                                                        {item.title}
                                                    </span>
                                                    {item.description && (
                                                        <span className="text-xs text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                                                            {item.description}
                                                        </span>
                                                    )}
                                                </div>
                                            </Link>
                                        </SidebarMenuButton>
                                    </SidebarMenuItem>
                                ))}
                            </SidebarMenu>
                        </SidebarGroupContent>
                    </SidebarGroup>
                ))}

                {/* Footer */}
                <div className="mt-auto border-t p-4">
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                        <div className="h-2 w-2 rounded-full bg-green-500 relative after:content-[''] after:absolute after:top-1/2 after:-translate-y-1/2 after:left-1/2 after:-translate-x-1/2 after:w-2 after:h-2 after:bg-green-500 after:rounded-full after:animate-ping"></div>
                        <span>Sistem Online</span>
                    </div>
                </div>
            </SidebarContent>
        </Sidebar>
    );
}
