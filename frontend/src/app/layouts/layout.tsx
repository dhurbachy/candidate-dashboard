import { AppSidebar } from "@/components/app-sidebar"
// import { SiteHeader } from "@/components/site-header"
import {
    SidebarInset,
    SidebarProvider,
} from "@/components/ui/sidebar"
import { Outlet } from "react-router"
import { useAuth } from "../../context/authContext"
export default function AppLayout() {
        const { logout } = useAuth()

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
<header className="flex h-[--header-height] shrink-0 items-center justify-between gap-2 border-b border-zinc-800 px-6 transition-[width,height] ease-linear">
                            <div className="flex items-center gap-2">
                                {/* <SidebarTrigger className="text-zinc-400 hover:text-zinc-100" /> */}
                                <div className="h-4 w-[1px] bg-zinc-800 mx-2" />
                                <span className="text-sm font-medium text-zinc-400">Workspace</span>
                            </div>

                            {/* Profile & Logout Section */}
                            <div className="flex items-center gap-5 py-3">
                                <div className="flex flex-col text-right hidden sm:flex">
                                    <span className="text-xs text-zinc-400">Signed in as</span>
                                    <span className="text-sm font-medium text-zinc-200">{}</span>
                                </div>
                                
                                {/* Profile Avatar Visual Anchor */}
                                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700 font-semibold text-sm text-zinc-200">
                                    {}
                                </div>

                                <button
                                    onClick={logout}
                                    className="h-8 rounded-md bg-destructive/10 px-3 text-xs font-medium text-destructive hover:bg-destructive/20 border border-destructive/20 transition-colors"
                                >
                                    Log out
                                </button>
                            </div>
                        </header>                        <div className="flex flex-1 flex-col">
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