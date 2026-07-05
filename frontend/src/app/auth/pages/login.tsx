import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom"; 
import { useAuth } from "../../../context/authContext"; 
import { LoginForm } from "../../../components/login-form";

export default function Login() {
  const { accessToken, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (isLoading) return;

    if (accessToken) {
      const from = location.state?.from?.pathname || "/dashboard";
      navigate(from, { replace: true });
    }
  }, [accessToken, isLoading, navigate, location]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#feffe6] flex items-center justify-center">
        <p className="text-gray-500">Checking session...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#feffe6] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <LoginForm />
      </div>
    </div>
  );
}
