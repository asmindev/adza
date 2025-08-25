import { AppSidebar } from "@/components/adminDashboard";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Outlet } from "react-router";
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

export default function Layout() {
    const breadcrumbs = [];
    return (
        <SidebarProvider>
            <AppSidebar />
            <main className="flex flex-col flex-1 w-full h-full overflow-y-auto">
                <div className="flex gap-1 items-center p-4 border-b">
                    <SidebarTrigger />
                    <Breadcrumb>
                        <BreadcrumbList>
                            {breadcrumbs?.map((crumb, index) => (
                                <BreadcrumbItem key={index}>
                                    <BreadcrumbLink href={crumb.href}>
                                        {crumb.label}
                                    </BreadcrumbLink>
                                    {index < breadcrumbs.length - 1 && (
                                        <BreadcrumbSeparator />
                                    )}
                                </BreadcrumbItem>
                            ))}
                        </BreadcrumbList>
                    </Breadcrumb>
                </div>
                <div className="p-4">
                    <Outlet />
                </div>
            </main>
        </SidebarProvider>
    );
}
