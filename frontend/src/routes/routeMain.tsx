import { Suspense } from "react";
import AppLayout from "../app/layouts/layout";
import { Route, Routes } from "react-router";
import { appRoutes, authRoutes } from "./routes";
import ProtectedRoute from "./protectedRoute";

export default function RouteMain() {

    return(
        <>
         <Suspense fallback={
                <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
                    loading...
                </div>
            }>
                <Routes>
                     {authRoutes.map((route) => (
                        <Route key={route.path} path={route.path} element={route.element} />
                    ))}
                    <Route path="/" element={<ProtectedRoute>
                        <AppLayout />
                        {/* {children} */}
                    </ProtectedRoute>}>
                        {appRoutes.map((route) => (
                            <Route
                                key={route.path}
                                path={route.path.replace("/", "")}
                                element={route.element}
                            />
                        ))}
                        <Route path="*" element={<>Not Found</>} />
                    </Route>

                   

                    {/* Catch-all 404 */}
                    <Route path="*" element={<>Forbidden</>} />
                </Routes>
            </Suspense>

        </>
    )
}