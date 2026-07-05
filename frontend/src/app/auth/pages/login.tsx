import { LoginForm } from "../../../components/login-form"
// import { Navigate } from "react-router";
export default function Login(){
    return(
        <>
         <div className="min-h-screen bg-[#feffe6] flex items-center justify-center px-4">
            <div className="w-full max-w-sm">
                <LoginForm />
            </div>
        </div>
        </>
    )
}