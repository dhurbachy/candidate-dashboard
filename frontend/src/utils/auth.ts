import axios from "axios";
import { useEffect } from "react";
import { useAuth } from "../context/authContext";

export const useAxiosInterceptor = () => {
  const { logout } = useAuth();

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        // If any API call returns 401 Unauthorized, wipe the state immediately
        if (error.response?.status === 401) {
          console.log('logout')
          logout();
        }
        return Promise.reject(error);
      }
    );

    return () => axios.interceptors.response.eject(interceptor);
  }, [logout]);
};
