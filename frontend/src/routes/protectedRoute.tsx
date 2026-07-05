
import { Navigate } from "react-router";
import { useAuth } from "../context/authContext";
export default function ProtectedRoute({
  children
}: {
  children: React.ReactNode;
}) {
  const {accessToken,isLoading}=useAuth();
  // const isAuthenticated = !!accessToken;
  // const isAuthenticated = true;

//   const { data: user,isLoading } = useGetMe();
//   const currentRoute = RouteList.find(r => r.path === location.pathname);


  if (isLoading) {
    return <div>Loading your workspace...</div>;
  }
//   if (currentRoute?.roles && !currentRoute?.roles.includes(user?.role)) {
//     return <Navigate to="/forbidden" replace />;
//   }

if (!accessToken) {
    // Save the current location in state so the Login component can send them back here
    return <Navigate to="/login" state={{ from: location }} replace />;
  }



  return <>{children}</>;
}