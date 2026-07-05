import { lazy } from "react";
import { ROUTES } from "./routeConstant";
const Login = lazy(() => import("../app/auth/pages/login"));

const Register = lazy(() => import("../app/auth/pages/register"));

export const RouteList = [
  {
    path: ROUTES.HOME,
    element: <>Home</>,
  },
  {
    path: ROUTES.DASHBOARD,
    element: <>Dashboard</>,
  },
  {
    path: ROUTES.LOGIN,
    element: <Login />,
    layout: "auth",
  },
  {
    path: ROUTES.REGISTER,
    element: <Register />,
    layout: "auth",
  },
  
  {
    path: ROUTES.CANDIDATES,
    element: <>Candidates</>,
    protected: true,
  },
  {
    path: ROUTES.CANDIDATE_DETAIL,
    element: <>Candidates Detail</>,
    protected: true,
  },
  
  {
    path: ROUTES.FORBIDDEN,
    element: <>Forbidden</>,
  },
];

export const authRoutes = RouteList.filter((r) => r.layout === "auth");
export const appRoutes = RouteList.filter((r) => r.layout !== "auth");