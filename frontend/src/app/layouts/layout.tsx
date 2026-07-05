import { AppSidebar } from "@/components/app-sidebar"
// import { SiteHeader } from "@/components/site-header"
import {
    SidebarInset,
    SidebarProvider,
} from "@/components/ui/sidebar"
import { Outlet } from "react-router"
export default function AppLayout() {
    return (
        <>
            <div className="dark">
                <SidebarProvider
                    style={
                        {
                            "--sidebar-width": "calc(var(--spacing) * 50)",
                            "--header-height": "calc(var(--spacing) * 12)",
                        } as React.CSSProperties
                    }
                >
                    <AppSidebar variant="inset" />
                    <SidebarInset>
                        {/* <SiteHeader /> */}
                        <div className="flex flex-1 flex-col">
                            <div className="@container/main flex flex-1 flex-col gap-2">
                                     <Outlet />
                            </div>
                        </div>
                    </SidebarInset>
                </SidebarProvider>
            </div>
        </>
    )
}