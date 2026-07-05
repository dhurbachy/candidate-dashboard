import { useMutation,useQueryClient } from "@tanstack/react-query";
import type { ApiError } from "../../../services/candidates-services";
import { AuthenticationGatewaySuiteService } from "../../../services/candidates-services/services/AuthenticationGatewaySuiteService";
import { OpenAPI } from "../../../services/candidates-services/core/OpenAPI";
import { useNavigate } from "react-router";
import {ROUTES} from "../../../routes/routeConstant";
import { useAuth } from "../../../context/authContext";
interface LoginPayload {
  email: string;
  password: string;
}
// -------------------- LOGIN --------------------
export const useLogin = () => {
  const {login}=useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: LoginPayload) =>
      AuthenticationGatewaySuiteService.loginApiAuthLoginPost(payload),
    onSuccess: (data) => {
      console.log(data);
      const token = data.access_token;
      console.log(token);
      if (token) {
        // localStorage.setItem("access_token", token);
        login(token);
      queryClient.invalidateQueries({ queryKey: ["me"] }); 

        OpenAPI.TOKEN = token;
      }
    },
  });
};