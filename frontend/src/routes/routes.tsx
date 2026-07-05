import { lazy } from "react";
import { ROUTES } from "./routeConstant";
import { Navigate } from "react-router";
const Login = lazy(() => import("../app/auth/pages/login"));
const Dashboard =lazy(()=>import("../app/dashboard/pages/dashboard"));
const Register = lazy(() => import("../app/auth/pages/register"));
const Candidate=lazy(()=>import("../app/candidate/pages/candidate"));
const CandidateDetail=lazy(()=>import("../app/candidate/pages/candidateDetail"));
const Home =lazy(()=>import("../app/home"))

export const RouteList = [
  {
    path: ROUTES.HOME,
    element: <Home />,
  },
  {
    path: ROUTES.DASHBOARD,
    element:<Dashboard />,
    protected: true,

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
    element: <Candidate />,
    protected: true,
  },
  {
    path: ROUTES.CANDIDATE_DETAIL,
    element: <CandidateDetail />,
    protected: true,
  },
  
  {
    path: ROUTES.FORBIDDEN,
    element: <>Forbidden</>,
  },
];

export const authRoutes = RouteList.filter((r) => r.layout === "auth");
export const appRoutes = RouteList.filter((r) => r.layout !== "auth");