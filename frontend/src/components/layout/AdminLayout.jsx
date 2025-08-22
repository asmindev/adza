import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "../adminDashboard";

export default function Layout({ children }) {
    return (
        <SidebarProvider>
            <AppSidebar />
            <main className="flex flex-col flex-1 w-full h-full overflow-y-auto">
                <SidebarTrigger />
                <div className="p-4">{children}</div>
            </main>
        </SidebarProvider>
    );
}
