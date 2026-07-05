import axios from "axios";
import { useEffect } from "react";
import { useAuth } from "../context/authContext";
import { OpenAPI } from "../services/candidates-services";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
axios.defaults.baseURL = BASE_URL;
axios.defaults.withCredentials = true;

OpenAPI.BASE = BASE_URL;
OpenAPI.WITH_CREDENTIALS = true;
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
