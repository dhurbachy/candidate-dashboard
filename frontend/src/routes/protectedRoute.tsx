
import { Navigate } from "react-router";
import { useAuth } from "../context/authContext";
export default function ProtectedRoute({
  children
}: {
  children: React.ReactNode;
}) {
  const {accessToken}=useAuth();
  const isAuthenticated = !!accessToken;
  // const isAuthenticated = true;

//   const { data: user,isLoading } = useGetMe();
//   const currentRoute = RouteList.find(r => r.path === location.pathname);


  if (!isAuthenticated) {
    // authService.signinRedirect();

    // return (
    //   <div
    //     style={{
    //       height: "100vh",
    //       display: "flex",
    //       justifyContent: "center",
    //       alignItems: "center",
    //     }}
    //   >
    //   </div>
    // );
    return <Navigate to="/login" replace />

  }
//   if(isLoading) {
//     return <><div>Loading ...</div></>;
//   }
//   if (currentRoute?.roles && !currentRoute?.roles.includes(user?.role)) {
//     return <Navigate to="/forbidden" replace />;
//   }



  return <>{children}</>;
}